const RecommendEngine = {
  _topologyLabel(platform) {
    const topo = platform && platform.topology ? platform.topology : {};
    const parts = [];
    if (topo.hw_config) parts.push(String(topo.hw_config));
    if (Number(topo.m1_modules) > 1) {
      parts.push('M1 ×' + topo.m1_modules);
    } else if (Number(topo.h1_cards) > 0) {
      parts.push('H1 ×' + topo.h1_cards);
    }
    if (Number(topo.device_count) > 1) {
      parts.push((typeof T === 'function' ? T('{n} DXRT devices') : '{n} DXRT devices').replace('{n}', topo.device_count));
    }
    if (topo.pcie) {
      const pcie = String(topo.pcie).split('[')[0].trim();
      if (pcie) parts.push(pcie);
    }
    return parts.join(' · ');
  },

  // An estimate never claims more than this many times the highest stream count we measured.
  EXTRAPOLATION_CAP: 2,
  // NPU busy share at the most loaded measured point above which the NPU, not the host, is the limit.
  NPU_BOUND_PCT: 85,

  /**
   * Channel capacity from the multi-stream benchmark (spec 2026-10-11-edgeguide-recommendation).
   *
   * The benchmark measured only the stream counts that bracket ~30 FPS per channel. Around that
   * point the pipeline is throughput-bound: total FPS stays roughly flat as streams are added and
   * falls when oversubscribed. So:
   *   T_sat = the lowest measured total FPS (the most loaded, most conservative figure)
   *   M     = the largest measured stream count that held the target per channel
   *   E     = floor(T_sat / target)
   * A measured failure above M → M (measured). Every row held the target → max(M, E) capped at
   * 2× the highest tested count (estimated; '+' when capped). No row held it → E (estimated).
   * E with the minimum T_sat never contradicts a measured row: a failing row has total < target·n.
   * Throttling no longer zeroes a platform — the measured FPS already ran at throttled clocks —
   * it is reported (throttled) and ranks after an equal cool result.
   *
   * @param {Object} inputs - {task, size, cameras, targetFps, priority, ort, maxLatencyMs}
   * @param {Array} platforms - DataLoader.getPlatforms()
   * @returns {Array} sorted recommendation results
   */
  recommend(inputs, platforms) {
    const ort = inputs.ort !== undefined ? inputs.ort : true;

    const results = platforms.map(platform => {
      const bench = platform.benchmarks.find(
        b => b.size === inputs.size && b.task === inputs.task && b.ort === ort
      );
      if (!bench) return null;

      const multiAll = platform.multi_stream.filter(
        m => m.size === inputs.size && m.task === inputs.task && m.ort === ort
      );

      const cap = this._calcMaxChannels(bench, multiAll, inputs.targetFps);
      const maxChannels = cap.maxChannels;
      const latencyMs = Number(bench.latency_ms) > 0 ? Number(bench.latency_ms) : null;
      const meetsChannels = maxChannels >= inputs.cameras;
      const meetsLatency = this._meetsLatency(latencyMs, inputs.maxLatencyMs);
      let status = 'short';
      if (meetsChannels && meetsLatency !== false) {
        status = (cap.evidence === 'measured' && meetsLatency === true) ? 'meets' : 'meets-estimated';
      }
      const tdp = Number(platform.npu.tdp_w) || 0;
      const topsPerWatt = tdp > 0 ? platform.npu.tops / tdp : 0;

      return {
        platform,
        throughputFps: bench.throughput_fps || 0,     // single-model NPU throughput (benchmark tool)
        pipelineFps: cap.tSat,                        // end-to-end camera pipeline total FPS (measured)
        latencyMs,
        maxChannels,
        boundaryFlag: cap.boundaryFlag,
        evidence: cap.evidence,
        why: cap.why,
        throttled: cap.throttled,
        bottleneck: cap.bottleneck,
        meetsChannels,
        meetsLatency,
        status,
        meetsRequirement: status !== 'short',
        // Informational: smallest measured stream count where the NPU throttled.
        throttleOnset: this._throttleOnset(multiAll),
        topsPerWatt: Math.round(topsPerWatt * 100) / 100,
        fpsPerWatt: tdp > 0 ? Math.round((cap.tSat / tdp) * 10) / 10 : 0,
      };
    }).filter(Boolean);

    return this._sort(results, inputs.priority);
  },

  /** true / false, or null when a budget is set but no latency was measured (never a silent pass). */
  _meetsLatency(latencyMs, maxLatencyMs) {
    const budget = Number(maxLatencyMs);
    if (maxLatencyMs == null || !Number.isFinite(budget) || budget <= 0) return true;
    if (!latencyMs) return null;
    return latencyMs <= budget;
  },

  // Kept for RadarChart, which calls this directly on a multi-stream row.
  _stabilityScore(row) {
    if (!row || row.fps_std == null || !Number.isFinite(row.fps_std)) return 0;
    return Math.round((1 / (1 + row.fps_std)) * 1000) / 1000;
  },

  _sortedMulti(multiAll) {
    return [...multiAll].sort(
      (a, b) => (a.stream_count || 0) - (b.stream_count || 0)
    );
  },

  _throttleOnset(multiAll) {
    const throttled = this._sortedMulti(multiAll).find(m => m.npu_throttled === true);
    return throttled ? (throttled.stream_count || null) : null;
  },

  /**
   * @returns {{maxChannels:number, boundaryFlag:('measured'|'estimated'|'+'), evidence:('measured'|'estimated'|'none'),
   *            tSat:number, throttled:boolean, bottleneck:('npu'|'host'|null), why:Object}}
   */
  _calcMaxChannels(bench, multiAll, targetFps) {
    const rows = this._sortedMulti(multiAll).filter(
      m => Number(m.stream_count) > 0 && Number.isFinite(Number(m.total_fps)) && m.per_channel_fps != null
    );
    const target = Number(targetFps) || 0;
    if (!rows.length || target <= 0) {
      return { maxChannels: 0, boundaryFlag: 'measured', evidence: 'none', tSat: 0, throttled: false,
               bottleneck: null, why: { kind: 'none' } };
    }

    const satRow = rows.reduce((lo, m) => (Number(m.total_fps) < Number(lo.total_fps) ? m : lo), rows[0]);
    const tSat = Number(satRow.total_fps);
    const maxTested = rows[rows.length - 1].stream_count;
    const held = rows.filter(m => m.per_channel_fps >= target);
    const mRow = held.length ? held[held.length - 1] : null;
    const measured = mRow ? mRow.stream_count : 0;
    const failAbove = rows.find(m => m.stream_count > measured && m.per_channel_fps < target);
    const estimate = Math.floor(tSat / target);

    let maxChannels; let evidence; let capped = false; let basis;
    if (mRow && failAbove) {
      maxChannels = measured; evidence = 'measured'; basis = mRow;
    } else if (mRow) {
      const limit = this.EXTRAPOLATION_CAP * maxTested;
      capped = estimate > limit;
      maxChannels = Math.max(measured, Math.min(estimate, limit));
      evidence = maxChannels > measured ? 'estimated' : 'measured';
      basis = evidence === 'measured' ? mRow : satRow;
    } else {
      maxChannels = estimate; evidence = 'estimated'; basis = satRow;
    }

    const loaded = rows[rows.length - 1];
    const npuPct = Number(loaded.npu_total_avg_pct);
    const why = evidence === 'measured'
      ? { kind: 'measured', n: measured, atFps: mRow.per_channel_fps,
          nextN: failAbove ? failAbove.stream_count : null, nextFps: failAbove ? failAbove.per_channel_fps : null }
      : { kind: 'estimated', n: maxChannels, tSat, maxTested, capped };
    return {
      maxChannels,
      boundaryFlag: capped ? '+' : evidence,
      evidence,
      tSat,
      throttled: basis.npu_throttled === true,
      bottleneck: Number.isFinite(npuPct) ? (npuPct >= this.NPU_BOUND_PCT ? 'npu' : 'host') : null,
      why,
    };
  },

  _tier(r) {
    return r.status === 'meets' ? 0 : r.status === 'meets-estimated' ? 1 : 2;
  },

  _sort(results, priority) {
    return results.sort((a, b) => {
      if (this._tier(a) !== this._tier(b)) return this._tier(a) - this._tier(b);
      if (a.throttled !== b.throttled) return a.throttled ? 1 : -1;

      let primary = 0;
      switch (priority) {
        case 'channels':
          primary = b.maxChannels - a.maxChannels;
          break;
        case 'performance':
          primary = (b.pipelineFps - a.pipelineFps) || ((a.latencyMs || Infinity) - (b.latencyMs || Infinity));
          break;
        case 'power':
          primary = (a.platform.npu.tdp_w - b.platform.npu.tdp_w) || (b.fpsPerWatt - a.fpsPerWatt);
          break;
        default:
          primary = 0;
      }
      if (primary) return primary;

      // Deterministic tiebreak: more channels -> higher pipeline FPS -> stable platform id.
      if (a.maxChannels !== b.maxChannels) return b.maxChannels - a.maxChannels;
      if (a.pipelineFps !== b.pipelineFps) return b.pipelineFps - a.pipelineFps;
      return String(a.platform.id).localeCompare(String(b.platform.id));
    });
  },
};
