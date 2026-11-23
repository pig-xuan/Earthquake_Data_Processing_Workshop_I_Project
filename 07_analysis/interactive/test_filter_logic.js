#!/usr/bin/env node
"use strict";
const assert = require("assert");
const path = require("path");
const fs = require("fs");
const { depthClass, filterIndices, subset, markerSizes } = require("./filter_logic.js");

function check(name, fn) {
  try {
    fn();
    console.log("OK ", name);
  } catch (err) {
    console.error("FAIL", name, err);
    process.exitCode = 1;
  }
}

check("depth class boundaries", () => {
  assert.strictEqual(depthClass(0), "shallow");
  assert.strictEqual(depthClass(69.999), "shallow");
  assert.strictEqual(depthClass(70), "intermediate");
  assert.strictEqual(depthClass(300), "intermediate");
  assert.strictEqual(depthClass(300.001), "deep");
  assert.strictEqual(depthClass(700), "deep");
});

const events = {
  x: [1, 2, 3, 4, 5, 6],
  y: [1, 2, 3, 4, 5, 6],
  z: [0, -80, -300, -301, -10, -20],
  depth: [0, 80, 300, 301, 10, 20],
  mag: [5.5, 6.0, 7.0, 8.0, 5.6, 9.1],
  year: [1965, 1980, 2000, 2016, 1990, 2010],
  date: ["a", "b", "c", "d", "e", "f"],
  time: ["t1", "t2", "t3", "t4", "t5", "t6"],
  lon: [70, 80, 90, 100, 110, 120],
  lat: [10, 20, 30, 40, 50, 55],
  plate: ["EU", "AM", "PS", "SU", "YA", "BU"],
};

const allOn = {
  yearMin: 1965,
  yearMax: 2016,
  magMin: 5.5,
  magMax: 9.1,
  classes: { shallow: true, intermediate: true, deep: true },
};

check("all filters on keeps six", () => {
  assert.deepStrictEqual(filterIndices(events, allOn), [0, 1, 2, 3, 4, 5]);
});

check("year window inclusive", () => {
  const f = Object.assign({}, allOn, { yearMin: 1980, yearMax: 2000 });
  assert.deepStrictEqual(filterIndices(events, f), [1, 2, 4]);
});

check("magnitude window inclusive", () => {
  const f = Object.assign({}, allOn, { magMin: 7.0, magMax: 8.0 });
  assert.deepStrictEqual(filterIndices(events, f), [2, 3]);
});

check("shallow only excludes 70-300 inclusive and deep", () => {
  const f = Object.assign({}, allOn, { classes: { shallow: true, intermediate: false, deep: false } });
  assert.deepStrictEqual(filterIndices(events, f), [0, 4, 5]);
});

check("intermediate includes 70 and 300, excludes 301", () => {
  const f = Object.assign({}, allOn, { classes: { shallow: false, intermediate: true, deep: false } });
  assert.deepStrictEqual(filterIndices(events, f), [1, 2]);
});

check("deep only", () => {
  const f = Object.assign({}, allOn, { classes: { shallow: false, intermediate: false, deep: true } });
  assert.deepStrictEqual(filterIndices(events, f), [3]);
});

check("all depth classes off yields empty but callable", () => {
  const f = Object.assign({}, allOn, { classes: { shallow: false, intermediate: false, deep: false } });
  const idx = filterIndices(events, f);
  assert.deepStrictEqual(idx, []);
  const sub = subset(events, f);
  assert.strictEqual(sub.n, 0);
  assert.deepStrictEqual(sub.x, []);
  assert.deepStrictEqual(sub.z, []);
  assert.deepStrictEqual(sub.indices, []);
});

check("combined year+mag+class", () => {
  const f = {
    yearMin: 1990,
    yearMax: 2016,
    magMin: 5.5,
    magMax: 8.0,
    classes: { shallow: true, intermediate: true, deep: false },
  };
  // 1990 M5.6 shallow, 2000 M7.0 mid, 2016 M8 deep excluded, 2010 M9.1 mag excluded
  assert.deepStrictEqual(filterIndices(events, f), [2, 4]);
});

check("marker size formula", () => {
  const s = markerSizes([5.5, 6.5, 9.1], { a: 5, b: 4, m0: 5.5 });
  assert.strictEqual(s[0], 5);
  assert.strictEqual(s[1], 9);
  assert.ok(Math.abs(s[2] - (5 + 4 * 3.6)) < 1e-10);
});

check("generated HTML embeds the same filter_logic.js", () => {
  const htmlPath = path.join(__dirname, "07_china_region_hypocenter_3d.html");
  const srcPath = path.join(__dirname, "filter_logic.js");
  if (!fs.existsSync(htmlPath)) {
    console.log("SKIP HTML embed check (html not built yet)");
    return;
  }
  const html = fs.readFileSync(htmlPath, "utf8");
  const src = fs.readFileSync(srcPath, "utf8").trim();
  assert.ok(html.indexOf("function depthClass(depth)") !== -1);
  assert.ok(html.indexOf("function filterIndices(events, filters)") !== -1);
  // core source should appear verbatim
  assert.ok(html.indexOf(src) !== -1, "HTML should embed filter_logic.js verbatim");
});

if (process.exitCode) {
  console.error("some tests failed");
  process.exit(process.exitCode);
} else {
  console.log("all filter tests passed");
}
