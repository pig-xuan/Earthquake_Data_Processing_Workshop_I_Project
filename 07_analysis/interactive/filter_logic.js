/**
 * 三维震源图筛选逻辑（与独立 HTML 共用，可供 Node 单元测试）。
 * 深度分级：浅源 < 70 km，中源 70–300 km（含 300），深源 > 300 km。
 */
(function (root) {
  function depthClass(depth) {
    if (depth < 70) return "shallow";
    if (depth <= 300) return "intermediate";
    return "deep";
  }

  function filterIndices(events, filters) {
    var idx = [];
    var n = events.year.length;
    var classes = filters.classes || {};
    var yearMin = filters.yearMin;
    var yearMax = filters.yearMax;
    var magMin = filters.magMin;
    var magMax = filters.magMax;
    for (var i = 0; i < n; i++) {
      if (events.year[i] < yearMin || events.year[i] > yearMax) continue;
      if (events.mag[i] < magMin || events.mag[i] > magMax) continue;
      if (!classes[depthClass(events.depth[i])]) continue;
      idx.push(i);
    }
    return idx;
  }

  function pick(arr, idx) {
    var out = new Array(idx.length);
    for (var i = 0; i < idx.length; i++) out[i] = arr[idx[i]];
    return out;
  }

  function emptyPayload(events) {
    return {
      x: [],
      y: [],
      z: [],
      depth: [],
      mag: [],
      textDates: [],
      n: 0,
    };
  }

  function subset(events, filters) {
    var idx = filterIndices(events, filters);
    if (idx.length === 0) {
      var empty = emptyPayload(events);
      empty.indices = idx;
      return empty;
    }
    return {
      x: pick(events.x, idx),
      y: pick(events.y, idx),
      z: pick(events.z, idx),
      depth: pick(events.depth, idx),
      mag: pick(events.mag, idx),
      date: pick(events.date, idx),
      time: pick(events.time, idx),
      lon: pick(events.lon, idx),
      lat: pick(events.lat, idx),
      plate: pick(events.plate, idx),
      indices: idx,
      n: idx.length,
    };
  }

  function markerSizes(mags, formula) {
    // size = a + b * (mag - m0); 与生成器约定一致
    var a = (formula && formula.a) != null ? formula.a : 5;
    var b = (formula && formula.b) != null ? formula.b : 4;
    var m0 = (formula && formula.m0) != null ? formula.m0 : 5.5;
    var out = new Array(mags.length);
    for (var i = 0; i < mags.length; i++) out[i] = a + b * (mags[i] - m0);
    return out;
  }

  var api = {
    depthClass: depthClass,
    filterIndices: filterIndices,
    pick: pick,
    subset: subset,
    markerSizes: markerSizes,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.HypocenterFilter = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
