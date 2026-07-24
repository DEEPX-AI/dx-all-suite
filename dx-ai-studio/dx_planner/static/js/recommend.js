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
      parts.push(topo.device_count + ' DXRT devices');
    }
    if (topo.pcie) {
      const pcie = String(topo.pcie).split('[')[0].trim();
      if (pcie) parts.push(pcie);
    }
    return parts.join(' · ');
  },

  /**
   * Pure-benchmark recommendation. Everything below is derived from MEASURED
   * benchmark rows only — no FPS headroom, no confidence tiers, no CPU gate,
   * and no extrapolation beyond measured stream counts.
   *
   * A stream_count is "sustainable" iff it was measured at per_channel_fps >=
   * targetFps AND the NPU did not thermally throttle at that point. maxChannels
   * is the largest sustainable stream_count. If host CPU saturation actually
   * hurt throughput it already shows up as per_channel_fps < target, so avg_cpu
   * is informational only.
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

      const channelCalc = this._calcMaxChannels(bench, multiAll, inputs.targetFps);
      const maxChannels = channelCalc.maxChannels;
      const boundaryFlag = channelCalc.boundaryFlag;

      const latencyMs = bench.latency_ms || 0;
      const meetsChannels = maxChannels >= inputs.cameras;
      const meetsLatency = this._meetsLatency(latencyMs, inputs.maxLatencyMs);
      const meetsRequirement = meetsChannels && meetsLatency;

      const topsPerWatt = platform.npu.tdp_w > 0
        ? platform.npu.tops / platform.npu.tdp_w
        : 0;

      return {
        platform,
        throughputFps: bench.throughput_fps || 0,
        latencyMs,
        maxChannels,
        boundaryFlag,
        meetsChannels,
        meetsLatency,
        meetsRequirement,
        // Informational only (never affects ranking): smallest measured stream
        // where the NPU throttled, i.e. "sustains up to maxChannels, throttles
        // at throttleOnset and beyond". null when no measured point throttled.
        throttleOnset: this._throttleOnset(multiAll),
        topsPerWatt: Math.round(topsPerWatt * 100) / 100,
      };
    }).filter(Boolean);

    return this._sort(results, inputs.priority);
  },

  _meetsLatency(latencyMs, maxLatencyMs) {
    const budget = Number(maxLatencyMs);
    if (!Number.isFinite(budget) || budget <= 0) return true;
    if (!latencyMs) return true;
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
   * Largest MEASURED, sustainable stream_count. Sustainable = per_channel_fps
   * meets targetFps AND not npu_throttled. No headroom, no extrapolation.
   * boundaryFlag: '+' when even the top tested stream sustains (so real max is
   * "at least this many"), otherwise 'measured'.
   * @returns {{maxChannels:number, boundaryFlag:('measured'|'+')}}
   */
  _calcMaxChannels(bench, multiAll, targetFps) {
    const sorted = this._sortedMulti(multiAll);
    const target = Number(targetFps) || 0;

    const sustainable = sorted.filter(
      m => m.per_channel_fps != null && m.per_channel_fps >= target && m.npu_throttled !== true
    );

    const streamMax = (rows) => rows.reduce((max, m) => {
      const sc = m.stream_count ?? null;
      return sc !== null && sc > max ? sc : max;
    }, 0);

    const maxChannels = streamMax(sustainable);
    const maxTested = streamMax(sorted);
    const boundaryFlag = (maxChannels > 0 && maxChannels === maxTested) ? '+' : 'measured';
    return { maxChannels, boundaryFlag };
  },

  _sort(results, priority) {
    return results.sort((a, b) => {
      if (a.meetsRequirement !== b.meetsRequirement) {
        return a.meetsRequirement ? -1 : 1;
      }

      let primary = 0;
      switch (priority) {
        case 'channels':
          primary = b.maxChannels - a.maxChannels;
          break;
        case 'performance':
          primary = b.throughputFps - a.throughputFps;
          break;
        case 'power':
          primary = a.platform.npu.tdp_w - b.platform.npu.tdp_w;
          break;
        default:
          primary = 0;
      }
      if (primary !== 0) return primary;

      // Deterministic tiebreak (ties are common at the all-fail tail):
      // more channels -> higher throughput -> stable platform id.
      if (a.maxChannels !== b.maxChannels) return b.maxChannels - a.maxChannels;
      if (a.throughputFps !== b.throughputFps) return b.throughputFps - a.throughputFps;
      return String(a.platform.id).localeCompare(String(b.platform.id));
    });
  },
};
