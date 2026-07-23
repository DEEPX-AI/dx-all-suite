/**
 * DataLoader — benchmarks.json 로드 + 에러 처리.
 * 사용: const data = await DataLoader.load();
 */
const DataLoader = {
  _data: null,
  STALE_BENCHMARK_DAYS: 180,

  async load() {
    if (this._data) return this._data;
    try {
      const resp = await fetch('/static/data/benchmarks.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      this._data = await resp.json();
      console.log(`[DataLoader] ${this._data.meta.platform_count} platforms loaded`);
      return this._data;
    } catch (e) {
      console.error('[DataLoader] Failed to load benchmarks:', e);
      throw e;
    }
  },

  getPlatforms() { return this._data?.platforms || []; },

  getPlatformById(id) {
    return this.getPlatforms().find(p => p.id === id);
  },

  getBenchmark(platformId, model, task) {
    const p = this.getPlatformById(platformId);
    if (!p) return null;
    return p.benchmarks.find(b => b.model === model && b.task === task);
  },

  getMultiStream(platformId, model, task) {
    const p = this.getPlatformById(platformId);
    if (!p) return [];
    return p.multi_stream.filter(m => m.model === model && m.task === task);
  },

  getMeta() { return this._data?.meta || {}; },

  getGeneratedAt() {
    return this.getMeta().generated || null;
  },

  getBenchmarkDate(platformId) {
    const dates = this.getMeta().benchmark_dates || {};
    return dates[platformId] || null;
  },

  isBenchmarkStale(platformId, now) {
    const benchmarkDate = this.getBenchmarkDate(platformId);
    if (!benchmarkDate) return true;
    const parsed = new Date(benchmarkDate + 'T00:00:00Z');
    if (Number.isNaN(parsed.getTime())) return true;
    const reference = now instanceof Date ? now : new Date();
    const ageDays = (reference.getTime() - parsed.getTime()) / (1000 * 60 * 60 * 24);
    return ageDays > this.STALE_BENCHMARK_DAYS;
  }
};
