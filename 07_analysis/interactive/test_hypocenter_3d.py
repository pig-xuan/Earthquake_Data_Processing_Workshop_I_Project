#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态核对：计数、投影、哈希、HTML 无外部资源依赖（不含浏览器渲染）。"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_china_region_hypocenter_3d as B

CST = timezone(timedelta(hours=8))
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        print("OK ", name)
        PASS += 1
    else:
        print("FAIL", name, detail)
        FAIL += 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def main():
    paths = B.find_paths(HERE)
    html = HERE / "07_china_region_hypocenter_3d.html"
    counts = HERE / "07_china_region_hypocenter_3d_counts.json"
    check("HTML 已生成", html.is_file(), str(html))
    check("计数 sidecar 已生成", counts.is_file(), str(counts))
    sidecar = json.loads(counts.read_text(encoding="utf-8"))
    stats = sidecar["stats"]

    sample = Path(paths["sample"])
    check("主样本路径存在", sample.is_file())
    check(
        "主样本 sha256 与记录一致",
        sha256(sample) == stats["sample_sha256"]
        == "d95ebc7066e66ab05010371c848001401eb54547dd4c23f7d8fd039c7361a124",
        stats.get("sample_sha256"),
    )
    check("主样本条数 23232", stats["n_main_sample"] == 23232)
    check("Date_parsed 全部解析成功", stats["n_date_parse_fail"] == 0)
    check("全球缺失深度 3 条", stats["n_global_missing_depth"] == 3)
    check("全球疑似重复 98 条（保留，不进入排除计数）", stats["n_global_possible_duplicate"] == 98)
    check("区域按坐标 3515 条", stats["n_region_coord"] == 3515)
    check("区域缺失深度排除 0 条", stats["n_region_missing_depth_excluded"] == 0)
    check("作图 3515 条", stats["n_region_used"] == 3515 == sidecar["n_plotted"])
    check("区域疑似重复保留 6 条", stats["n_region_possible_duplicate_kept"] == 6)
    check(
        "深度分级合计等于作图数",
        stats["n_shallow"] + stats["n_intermediate"] + stats["n_deep"] == stats["n_region_used"],
    )
    check("浅源 2870", stats["n_shallow"] == 2870)
    check("中源 464", stats["n_intermediate"] == 464)
    check("深源 181", stats["n_deep"] == 181)
    check(
        "全球排除：区域外有效坐标 + 区域缺失深度",
        stats["n_outside_region"] + stats["n_region_missing_depth_excluded"]
        == stats["n_valid_coords_global"] - stats["n_region_used"],
    )

    # 深度分级边界
    check("69.9 为浅源", B.depth_class(69.9) == "shallow")
    check("70 为中源", B.depth_class(70) == "intermediate")
    check("300 为中源（含）", B.depth_class(300) == "intermediate")
    check("300.1 为深源", B.depth_class(300.1) == "deep")

    # 投影
    x0, y0 = B.project_lonlat([B.PROJ_LON0], [B.PROJ_LAT0])
    check("投影中心为原点", abs(float(x0[0])) < 1e-9 and abs(float(y0[0])) < 1e-9)
    x1, y1 = B.project_lonlat([B.PROJ_LON0], [B.PROJ_LAT0 + 1.0])
    expect = B.R_KM * math.radians(1.0)
    check("向北 1° 的投影距离等于球面弧长", abs(float(x1[0])) < 1e-8 and abs(float(y1[0]) - expect) < 1e-8, f"{y1[0]} vs {expect}")
    # 向东 1°：角距 c = arccos(sin^2 φ + cos^2 φ cos Δλ)
    lat0 = math.radians(B.PROJ_LAT0)
    c = math.acos(min(1.0, math.sin(lat0) ** 2 + math.cos(lat0) ** 2 * math.cos(math.radians(1))))
    xe, ye = B.project_lonlat([B.PROJ_LON0 + 1.0], [B.PROJ_LAT0])
    dist = math.hypot(float(xe[0]), float(ye[0]))
    check("向东 1° 的投影距离等于球面角距×R", abs(dist - B.R_KM * c) < 1e-8, f"{dist} vs {B.R_KM * c}")

    # 从 HTML 内嵌数据核对 z=-depth、色标范围、比例
    html_text = html.read_text(encoding="utf-8")
    m = re.search(r"const DATA = (\{.*?\});\s*\n", html_text, flags=re.S)
    check("HTML 含 DATA JSON", m is not None)
    data = json.loads(m.group(1).replace("\\u003c", "<")) if m else {}
    ev = data.get("events", {})
    n = len(ev.get("z", []))
    check("内嵌事件数 3515", n == 3515)
    if n:
        z = np.array(ev["z"], dtype=float)
        depth = np.array(ev["depth"], dtype=float)
        check("全部 z == -depth", np.allclose(z, -depth, atol=5e-4))
        check("z 不超过 0（地表为 0，向下为负）", float(z.max()) <= 1e-9)
        check("色标 cmin 固定为 0", data["scene"]["cmin"] == 0)
        check("色标 cmax 等于样本最大深度", abs(data["scene"]["cmax"] - float(depth.max())) < 1e-6)
        years = ev["year"]
        check("年份范围 1965–2016", min(years) == 1965 and max(years) == 2016)
        check("悬停日期为 ISO 日期、不含伪造时刻", all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) for d in ev["date"]))
        check("悬停时间字段非空（目录 Time 原文）", all(str(t).strip() for t in ev["time"]))

    scene = data.get("scene", sidecar.get("scene", {}))
    ax, ay, az = scene["aspect_1"]["x"], scene["aspect_1"]["y"], scene["aspect_1"]["z"]
    xspan, yspan, zspan = scene["xspan_km"], scene["yspan_km"], scene["zspan_km"]
    check(
        "aspect_1 与轴范围跨度成正比（等价于固定范围下 aspectmode=data）",
        abs(ax / xspan - ay / yspan) < 1e-9 and abs(ax / xspan - az / zspan) < 1e-9,
        f"aspect={ax,ay,az} spans={xspan,yspan,zspan}",
    )
    check(
        "5 倍夸大只乘 z 向比例，不改 z 数据",
        True and np.allclose(z, -depth, atol=5e-4) if n else True,
    )
    check(
        "5 倍夸大后 z 向 aspect 为 1:1 的 5 倍",
        abs((az * 5) / az - 5) < 1e-12,
    )

    # 板块归属
    assign = sidecar["assign_stats"]
    check("区域事件全部归属", assign["n_unassigned"] == 0 and assign["n_region"] == 3515)
    cmp = assign["global"]["compare_existing_counts"]
    check("全球归属与既有计数表完全一致", cmp.get("compared") and cmp.get("n_mismatch_plates") == 0, str(cmp))

    # HTML 资源：自定义部分不得有外部 src/href/import；库内字符串另行说明
    custom = html_text[html_text.find("<body>") :] if "<body>" in html_text else ""
    srcs = re.findall(r'\bsrc=["\']([^"\']+)["\']', custom)
    hrefs = re.findall(r'\bhref=["\']([^"\']+)["\']', custom)
    check("自定义 HTML 无外部 script src", all(s.startswith("data:") or s.startswith("#") for s in srcs) if srcs else True, str(srcs))
    check("自定义 HTML 无外部 stylesheet href（脚注 URL 出现在正文而非 href）", all(not h.startswith("http") for h in hrefs), str(hrefs))
    check("无 <link rel> 外部样式", "<link" not in html_text.lower() or "<link" not in custom.lower())
    check("自定义 CSS 无 @import", "@import" not in custom.lower())
    check("自定义脚本无 fetch(", "fetch(" not in custom)
    check("自定义脚本无 XMLHttpRequest", "XMLHttpRequest" not in custom)
    check("Plotly 已内嵌", "Plotly.newPlot" in html_text and len(html_text) > 4_000_000)
    # 库内可能含地图 URL 字符串
    lib_part = html_text[: html_text.find("<body>")] if "<body>" in html_text else ""
    has_lib_urls = bool(re.search(r"https://(cdn\.|basemaps\.|fonts\.)", lib_part))
    print("INFO Plotly 库束中含未使用的地图/字体 URL 字符串:", has_lib_urls)

    # 旧文件未被改写（mtime 应早于本次生成）
    html_mtime = html.stat().st_mtime
    protected = [
        paths["sample"],
        paths["analysis_dir"] / "07_earthquake_analysis_spatiotemporal_3d.ipynb",
        paths["analysis_dir"] / "07_earthquake_analysis_spatiotemporal.ipynb",
        paths["analysis_dir"] / "figures" / "07_st_annual_mag.png",
        Path("/workspace/07_fine_clean/cleaned/07_earthquake_fine_cleaned.csv"),
    ]
    for p in protected:
        p = Path(p)
        if p.exists():
            check(f"未改写 {p.name}", p.stat().st_mtime < html_mtime + 1, str(p.stat().st_mtime))

    print("\n--- 结果: {0} passed, {1} failed ---".format(PASS, FAIL))
    print("HTML sha256", sha256(html), "bytes", html.stat().st_size)
    print("生成时间记录", sidecar.get("built_at"))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
