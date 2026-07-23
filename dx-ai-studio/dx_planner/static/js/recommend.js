const RecommendEngine = {
  DEFAULT_FPS_HEADROOM: 0.1,
  DEFAULT_CPU_BUDGET_PCT: 400,

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
   * @param {Object} inputs - {task, size, cameras, targetFps, priority, ort, fpsHeadroom, maxLatencyMs}
   * @param {Array} platforms - DataLoader.getPlatforms()
   * @returns {Array} sorted recommendation results
   */
  recommend(inputs, platforms) {
    const results = platforms.map(platform => {
      // Match by (size, task, ort) using the benchmark rows' own fields. The data models are
      // named yolo26-n_640x640 / yolo26-l-pose_640x640 etc., so the old `yolo26${size}` string
      // never equalled b.model and every platform fell through to null (0 recommendations).
      const ort = inputs.ort !== undefined ? inputs.ort : true;
      const bench = platform.benchmarks.find(
        b => b.size === inputs.size && b.task === inputs.task && b.ort === ort
      );
      if (!bench) return null;

      const multiAll = platform.multi_stream.filter(
        m => m.size === inputs.size && m.task === inputs.task && m.ort === ort
      );

      const headroom = this._normalizeHeadroom(inputs.fpsHeadroom);
      const channelCalc = this._calcMaxChannels(bench, multiAll, inputs.targetFps, headroom);
      // Only surface platforms backed by MEASURED multi-stream evidence at the target. Drop
      // estimated channel counts — interpolated (between measured points) and theoretical
      // (single-stream throughput ÷ target, no multi-stream data) — so recommendations reflect
      // real measurements only, not extrapolation.
      if (channelCalc.boundaryFlag === 'interpolated' || channelCalc.boundaryFlag === 'theoretical') {
        return null;
      }
      const evidenceRow = this._rowForCameras(multiAll, inputs.cameras);
      const limits = this._operationalLimits(evidenceRow, inputs);

      let boundaryFlag = channelCalc.boundaryFlag;
      if (limits.thermal) boundaryFlag = 'thermal';
      else if (limits.hostLimited) boundaryFlag = 'host-limited';

      const maxChannels = channelCalc.maxChannels;
      const latencyMs = bench.latency_ms || 0;
      const meetsChannels = maxChannels >= inputs.cameras;
      const meetsLatency = this._meetsLatency(latencyMs, inputs.maxLatencyMs);
      const meetsRequirement = meetsChannels && meetsLatency && !limits.thermal && !limits.hostLimited;

      const topsPerWatt = platform.npu.tdp_w > 0
        ? platform.npu.tops / platform.npu.tdp_w
        : 0;

      return {
        platform,
        throughputFps: bench.throughput_fps || 0,
        latencyMs,
        maxChannels,
        boundaryFlag,
        confidenceTier: this._confidenceTier(boundaryFlag),
        effectiveTargetFps: this._effectiveTarget(inputs.targetFps, headroom),
        fpsHeadroom: headroom,
        evidenceRow,
        meetsChannels,
        meetsLatency,
        hostLimited: limits.hostLimited,
        thermalLimited: limits.thermal,
        meetsRequirement,
        topsPerWatt: Math.round(topsPerWatt * 100) / 100,
        stabilityScore: this._stabilityScore(evidenceRow),
      };
    }).filter(Boolean);

    return this._sort(results, inputs.priority);
  },

  _normalizeHeadroom(value) {
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0) return this.DEFAULT_FPS_HEADROOM;
    return Math.min(n, 0.5);
  },

  _effectiveTarget(targetFps, headroom) {
    const margin = this._normalizeHeadroom(headroom);
    return Math.round(targetFps * (1 + margin) * 100) / 100;
  },

  _meetsLatency(latencyMs, maxLatencyMs) {
    const budget = Number(maxLatencyMs);
    if (!Number.isFinite(budget) || budget <= 0) return true;
    if (!latencyMs) return true;
    return latencyMs <= budget;
  },

  _confidenceTier(boundaryFlag) {
    switch (boundaryFlag) {
      case '+':
      case 'measured':
        return 0;
      case null:
        return 0;
      case 'interpolated':
        return 1;
      case 'host-limited':
      case 'thermal':
        return 2;
      case 'theoretical':
        return 3;
      default:
        return 2;
    }
  },

  _stabilityScore(row) {
    if (!row || row.fps_std == null || !Number.isFinite(row.fps_std)) return 0;
    return Math.round((1 / (1 + row.fps_std)) * 1000) / 1000;
  },

  _sortedMulti(multiAll) {
    return [...multiAll].sort(
      (a, b) => (a.stream_count || 0) - (b.stream_count || 0)
    );
  },

  _rowForCameras(multiAll, cameras) {
    const sorted = this._sortedMulti(multiAll);
    if (!sorted.length) return null;
    const exact = sorted.find(m => m.stream_count === cameras);
    if (exact) return exact;
    const atOrAbove = sorted.find(m => (m.stream_count || 0) >= cameras);
    if (atOrAbove) return atOrAbove;
    return sorted[sorted.length - 1];
  },

  _operationalLimits(row, inputs) {
    const cpuBudget = Number.isFinite(Number(inputs.cpuBudgetPct))
      ? Number(inputs.cpuBudgetPct)
      : this.DEFAULT_CPU_BUDGET_PCT;
    if (!row) return { hostLimited: false, thermal: false };
    const hostLimited = row.avg_cpu_pct != null && row.avg_cpu_pct > cpuBudget;
    const thermal = Boolean(row.npu_throttled);
    return { hostLimited, thermal };
  },

  _calcMaxChannels(bench, multiAll, targetFps, headroom) {
    const effectiveTarget = this._effectiveTarget(targetFps, headroom);
    const sorted = this._sortedMulti(multiAll);
    const filtered = sorted.filter(m => m.per_channel_fps >= effectiveTarget);

    if (filtered.length > 0) {
      const maxMeasured = filtered.reduce((max, m) => {
        const streamCount = m.stream_count ?? null;
        return streamCount !== null && streamCount > max ? streamCount : max;
      }, 0);
      const totalMax = sorted.reduce((max, m) => {
        const streamCount = m.stream_count ?? null;
        return streamCount !== null && streamCount > max ? streamCount : max;
      }, 0);

      if (maxMeasured === 0 && filtered.every(m => m.stream_count == null)) {
        return this._theoreticalFallback(bench, effectiveTarget);
      }
      if (maxMeasured === totalMax) {
        return { maxChannels: maxMeasured, boundaryFlag: '+' };
      }
      return { maxChannels: maxMeasured, boundaryFlag: 'measured' };
    }

    const interpolated = this._interpolateCrossing(sorted, effectiveTarget);
    if (interpolated != null) {
      return { maxChannels: interpolated, boundaryFlag: 'interpolated' };
    }

    return this._theoreticalFallback(bench, effectiveTarget);
  },

  _interpolateCrossing(sorted, effectiveTarget) {
    if (sorted.length < 2) return null;
    for (let i = 0; i < sorted.length - 1; i += 1) {
      const a = sorted[i];
      const b = sorted[i + 1];
      const fpsA = a.per_channel_fps;
      const fpsB = b.per_channel_fps;
      const s1 = a.stream_count;
      const s2 = b.stream_count;
      if (
        s1 == null || s2 == null ||
        fpsA == null || fpsB == null ||
        fpsB === fpsA
      ) {
        continue;
      }
      if (fpsA >= effectiveTarget && fpsB < effectiveTarget) {
        const cross = s1 + ((effectiveTarget - fpsA) * (s2 - s1)) / (fpsB - fpsA);
        return Math.max(0, Math.floor(cross));
      }
    }
    return null;
  },

  _theoreticalFallback(bench, effectiveTarget) {
    const theoretical = effectiveTarget > 0
      ? Math.floor((bench.throughput_fps || 0) / effectiveTarget)
      : 0;
    return { maxChannels: theoretical, boundaryFlag: 'theoretical' };
  },

  _sort(results, priority) {
    return results.sort((a, b) => {
      if (a.meetsRequirement !== b.meetsRequirement) {
        return a.meetsRequirement ? -1 : 1;
      }
      if (a.confidenceTier !== b.confidenceTier) {
        return a.confidenceTier - b.confidenceTier;
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

      if (a.maxChannels !== b.maxChannels) {
        return b.maxChannels - a.maxChannels;
      }
      return b.stabilityScore - a.stabilityScore;
    });
  },
};
