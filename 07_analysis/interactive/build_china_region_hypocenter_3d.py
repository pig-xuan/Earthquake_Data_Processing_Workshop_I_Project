#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成中国及周边区域独立离线 HTML 三维震源图。

只读取已有本地数据，不改写源文件或既有图表。可被同目录笔记本按步骤调用。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import (
    LineString,
    MultiLineString,
    MultiPolygon,
    Point,
    Polygon,
    box,
    shape,
)
from shapely.ops import linemerge, unary_union
from shapely.strtree import STRtree
from shapely.validation import make_valid

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
LON_MIN, LON_MAX = 70.0, 145.0
LAT_MIN, LAT_MAX = 10.0, 60.0
PROJ_LON0, PROJ_LAT0 = 107.5, 35.0
R_KM = 6371.0
DEPTH_SHALLOW = 70.0
DEPTH_INTERMEDIATE = 300.0  # 含 300
VERT_EXAG_ALT = 5.0
SIMPLIFY_TOL_KM = {
    "coast": 4.0,
    "border": 4.0,
    "plate": 2.0,
    "block_l1": 1.0,
    "block_l1d": 1.0,
    "block_l2": 1.0,
    "fault": 2.5,
}
DENSIFY_DEG = 0.5
JUMP_SPLIT_KM = 500.0
MARKER_SIZE = {"a": 5.0, "b": 4.0, "m0": 5.5}
# 深度色阶：浅部暖金/珊瑚，深部青蓝，避开深紫背景与金色地图线
COLORSCALE = [
    [0.00, "#FFE28A"],
    [0.10, "#F7B267"],
    [0.22, "#F06B6B"],
    [0.40, "#D45BB3"],
    [0.60, "#8B6CFF"],
    [0.80, "#3E9BFF"],
    [1.00, "#4FF0E0"],
]
FONT_STACK = (
    "Noto Sans CJK SC, Noto Sans SC, Source Han Sans SC, "
    "Microsoft YaHei, PingFang SC, WenQuanYi Micro Hei, Noto Sans, sans-serif"
)
CST = timezone(timedelta(hours=8), name="CST")

PLATE_CN = {
    "Africa": "非洲板块",
    "Antarctica": "南极板块",
    "Somalia": "索马里板块",
    "India": "印度板块",
    "Australia": "澳大利亚板块",
    "Eurasia": "欧亚板块",
    "North America": "北美板块",
    "South America": "南美板块",
    "Nazca": "纳斯卡板块",
    "Pacific": "太平洋板块",
    "Arabia": "阿拉伯板块",
    "Sunda": "巽他板块",
    "Timor": "帝汶板块",
    "Kermadec": "克马德克板块",
    "Tonga": "汤加板块",
    "Niuafo'ou": "纽阿福欧板块",
    "Woodlark": "伍德拉克板块",
    "Maoke": "毛克板块",
    "South Bismarck": "南俾斯麦板块",
    "Solomon Sea": "所罗门海板块",
    "North Bismarck": "北俾斯麦板块",
    "New Hebrides": "新赫布里底板块",
    "Caribbean": "加勒比板块",
    "Cocos": "科科斯板块",
    "Okhotsk": "鄂霍次克板块",
    "Juan de Fuca": "胡安·德富卡板块",
    "Altiplano": "阿尔蒂普拉诺板块",
    "North Andes": "北安第斯板块",
    "Okinawa": "冲绳板块",
    "Philippine Sea": "菲律宾海板块",
    "Amur": "阿穆尔板块",
    "Caroline": "加罗林板块",
    "Mariana": "马里亚纳板块",
    "Futuna": "富图纳板块",
    "Scotia": "斯科舍板块",
    "Shetland": "南设得兰板块",
    "Aegean Sea": "爱琴海板块",
    "Anatolia": "安纳托利亚板块",
    "Yangtze": "扬子板块",
    "Burma": "缅甸板块",
    "Rivera": "里维拉板块",
    "Birds Head": "鸟头板块",
    "Molucca Sea": "马鲁古海板块",
    "Banda Sea": "班达海板块",
    "Manus": "马努斯板块",
    "Conway Reef": "康威礁板块",
    "Balmoral Reef": "巴尔莫勒尔礁板块",
    "Easter": "复活节岛板块",
    "Juan Fernandez": "胡安·费尔南德斯板块",
    "Galapagos": "加拉帕戈斯板块",
    "Sandwich": "桑威奇板块",
    "Panama": "巴拿马板块",
}

# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------

def _first_existing(candidates, predicate):
    for p in candidates:
        try:
            if p is not None and predicate(Path(p)):
                return Path(p)
        except OSError:
            continue
    return None


def find_paths(start: Path | None = None) -> dict:
    """按项目相对布局查找数据，兼容桌面目录、当前目录与箱子路径。"""
    here = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    seeds = []
    if start is not None:
        seeds.append(Path(start).resolve())
    seeds.extend(
        [
            Path.cwd().resolve(),
            here,
            here.parent,
            here.parent.parent,
            Path.cwd().parent,
            Path(r"C:\Users\WHB\Desktop\DPW I"),
            Path("/workspace"),
        ]
    )
    roots = []
    seen = set()
    for s in seeds:
        for cand in (s, s / "07_analysis", s.parent, s.parent.parent):
            try:
                r = cand.resolve()
            except OSError:
                continue
            if r in seen:
                continue
            seen.add(r)
            roots.append(r)

    def hunt_file(*relatives):
        cands = []
        for root in roots:
            for rel in relatives:
                cands.append(root / rel)
        return _first_existing(cands, lambda p: p.is_file())

    def hunt_dir(*relatives, marker=None):
        cands = []
        for root in roots:
            for rel in relatives:
                cands.append(root / rel)
        if marker:
            return _first_existing(cands, lambda p: p.is_dir() and (p / marker).exists())
        return _first_existing(cands, lambda p: p.is_dir())

    sample = hunt_file(
        "07_earthquake_analysis_sample.csv",
        "07_analysis/07_earthquake_analysis_sample.csv",
    )
    if sample is None:
        raise FileNotFoundError(
            "找不到 07_earthquake_analysis_sample.csv。请从项目目录或 07_analysis 运行。"
        )
    analysis_dir = sample.parent
    project = analysis_dir.parent if analysis_dir.name == "07_analysis" else analysis_dir

    plate_json = hunt_file(
        "07_external/context/tectonicplates/GeoJSON/PB2002_plates.json",
        "07_external/context/tectonicplates/PB2002_plates.json",
    )
    plate_shp = hunt_file("07_external/context/tectonicplates/PB2002_plates.shp")
    plate_bnd_json = hunt_file(
        "dpw1_report/mapdata/PB2002_boundaries.json",
        "mapdata/PB2002_boundaries.json",
        "07_external/context/tectonicplates/GeoJSON/PB2002_boundaries.json",
    )
    plate_bnd_shp = hunt_file("07_external/context/tectonicplates/PB2002_boundaries.shp")

    mapdata = hunt_dir(
        "dpw1_report/mapdata",
        "mapdata",
        marker="ne_50m_land",
    )
    if mapdata is None:
        # 允许 land 目录直接作为标记
        land = hunt_dir(
            "dpw1_report/mapdata/ne_50m_land",
            "mapdata/ne_50m_land",
            marker="ne_50m_land.shp",
        )
        if land is not None:
            mapdata = land.parent

    blocks = hunt_dir("07_external/china/blocks", marker="CN-block-L1.gmt")
    faults = hunt_file(
        "07_external/china/faults/CN-faults.gmt",
        "07_external/china/CN-faults.gmt",
    )
    counts_csv = hunt_file(
        "07_analysis/07_st_3d_plate_counts.csv",
        "07_st_3d_plate_counts.csv",
    )

    land_shp = None
    country_shp = None
    if mapdata is not None:
        p = mapdata / "ne_50m_land" / "ne_50m_land.shp"
        if p.exists():
            land_shp = p
        p = mapdata / "ne_50m_admin_0_countries" / "ne_50m_admin_0_countries.shp"
        if p.exists():
            country_shp = p

    missing = []
    if plate_json is None and plate_shp is None:
        missing.append("PB2002 板块多边形")
    if plate_bnd_json is None and plate_bnd_shp is None:
        missing.append("PB2002 板块边界线")
    if land_shp is None:
        missing.append("Natural Earth 50m 陆地 (ne_50m_land.shp)")
    if country_shp is None:
        missing.append("Natural Earth 50m 国界 (ne_50m_admin_0_countries.shp)")
    if blocks is None:
        missing.append("中国活动地块 GMT (CN-block-L1.gmt 等)")
    if faults is None:
        missing.append("中国断层 CN-faults.gmt")
    if missing:
        raise FileNotFoundError("已有数据不足，缺少：" + "；".join(missing) + "。未造几何。")

    out_dir = analysis_dir / "interactive"
    return {
        "project": project,
        "analysis_dir": analysis_dir,
        "sample": sample,
        "plate_json": plate_json,
        "plate_shp": plate_shp,
        "plate_bnd_json": plate_bnd_json,
        "plate_bnd_shp": plate_bnd_shp,
        "mapdata": mapdata,
        "land_shp": land_shp,
        "country_shp": country_shp,
        "blocks_dir": blocks,
        "faults_gmt": faults,
        "counts_csv": counts_csv,
        "out_dir": out_dir,
    }


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def coerce_bool(s: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False).astype(bool)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def now_cst_label() -> str:
    return datetime.now(CST).strftime("%Y-%m-%d %H:%M") + "（北京时间，Asia/Shanghai，UTC+8）"


def depth_class(depth: float) -> str:
    if depth < DEPTH_SHALLOW:
        return "shallow"
    if depth <= DEPTH_INTERMEDIATE:
        return "intermediate"
    return "deep"


# ---------------------------------------------------------------------------
# 读取主样本
# ---------------------------------------------------------------------------

def load_sample(sample_path: Path) -> tuple[pd.DataFrame, dict]:
    raw = Path(sample_path).read_bytes()
    df = pd.read_csv(sample_path)
    n0 = len(df)
    df["Date_parsed"] = pd.to_datetime(
        df["Date_parsed"], format="ISO8601", utc=True, errors="coerce"
    )
    bool_cols = [
        "flag_coord_invalid",
        "flag_mag_outlier",
        "flag_depth_negative",
        "flag_possible_duplicate",
        "flag_depth_over_700",
        "in_china",
        "is_earthquake",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = coerce_bool(df[col])
    stats = {
        "sample_path": str(Path(sample_path).resolve()),
        "sample_sha256": hashlib.sha256(raw).hexdigest(),
        "sample_bytes": len(raw),
        "n_main_sample": int(n0),
        "n_date_parse_fail": int(df["Date_parsed"].isna().sum()),
        "n_coord_invalid": int(df["flag_coord_invalid"].sum()) if "flag_coord_invalid" in df else 0,
        "n_global_missing_depth": int(df["Depth"].isna().sum()),
        "n_global_depth_negative_flag": int(df["flag_depth_negative"].sum())
        if "flag_depth_negative" in df
        else 0,
        "n_global_possible_duplicate": int(df["flag_possible_duplicate"].sum())
        if "flag_possible_duplicate" in df
        else 0,
        "date_min": None
        if df["Date_parsed"].isna().all()
        else str(df["Date_parsed"].min()),
        "date_max": None
        if df["Date_parsed"].isna().all()
        else str(df["Date_parsed"].max()),
        "n_date_parsed_midnight_utc": int(
            (
                df["Date_parsed"].notna()
                & (df["Date_parsed"].dt.hour == 0)
                & (df["Date_parsed"].dt.minute == 0)
                & (df["Date_parsed"].dt.second == 0)
                & (df["Date_parsed"].dt.microsecond == 0)
            ).sum()
        ),
    }
    return df, stats


def filter_region(df: pd.DataFrame, global_stats: dict) -> tuple[pd.DataFrame, dict]:
    """按矩形范围筛选；不按 Country；缺失深度排除；疑似重复保留。"""
    valid = (
        ~df.get("flag_coord_invalid", False)
        & df["Latitude"].notna()
        & df["Longitude"].notna()
    )
    in_box = (
        valid
        & (df["Longitude"] >= LON_MIN)
        & (df["Longitude"] <= LON_MAX)
        & (df["Latitude"] >= LAT_MIN)
        & (df["Latitude"] <= LAT_MAX)
    )
    region = df.loc[in_box].copy()
    missing_depth = region["Depth"].isna()
    kept = region.loc[~missing_depth].copy()
    kept["year"] = kept["Date_parsed"].dt.year.astype("Int64")
    kept["depth_class"] = kept["Depth"].map(depth_class)
    # 悬停日期：只用 Date_parsed 的日期部分（ISO），时间用目录 Time 原文
    kept["hover_date"] = kept["Date_parsed"].dt.strftime("%Y-%m-%d")
    kept["hover_time"] = kept["Time"].astype(str).fillna("")

    stats = {
        "lon_min": LON_MIN,
        "lon_max": LON_MAX,
        "lat_min": LAT_MIN,
        "lat_max": LAT_MAX,
        "n_valid_coords_global": int(valid.sum()),
        "n_outside_region": int((valid & ~in_box).sum()),
        "n_region_coord": int(len(region)),
        "n_region_missing_depth_excluded": int(missing_depth.sum()),
        "n_region_used": int(len(kept)),
        "n_region_possible_duplicate_kept": int(
            kept["flag_possible_duplicate"].sum() if "flag_possible_duplicate" in kept else 0
        ),
        "n_shallow": int((kept["depth_class"] == "shallow").sum()),
        "n_intermediate": int((kept["depth_class"] == "intermediate").sum()),
        "n_deep": int((kept["depth_class"] == "deep").sum()),
        "mag_min": float(kept["Magnitude"].min()) if len(kept) else None,
        "mag_max": float(kept["Magnitude"].max()) if len(kept) else None,
        "depth_min": float(kept["Depth"].min()) if len(kept) else None,
        "depth_max": float(kept["Depth"].max()) if len(kept) else None,
        "year_min": int(kept["year"].min()) if len(kept) and kept["year"].notna().any() else None,
        "year_max": int(kept["year"].max()) if len(kept) and kept["year"].notna().any() else None,
        "n_in_china_flag_in_region": int(kept["in_china"].sum()) if "in_china" in kept else None,
    }
    stats.update({k: global_stats[k] for k in global_stats})
    return kept, stats


# ---------------------------------------------------------------------------
# 投影：球面方位等距，单位 km
# ---------------------------------------------------------------------------

def project_lonlat(lon, lat, lon0=PROJ_LON0, lat0=PROJ_LAT0, r=R_KM):
    """球面方位等距投影（Azimuthal Equidistant）。

    与既有分板块立体图一致：+proj=aeqd +R=6371000，再换算为公里。
    自投影中心的球面距离保持真实；远离中心时面积与方位有畸变。
    """
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    lon_r = np.radians(lon)
    lat_r = np.radians(lat)
    lon0_r = math.radians(lon0)
    lat0_r = math.radians(lat0)
    dlon = lon_r - lon0_r
    cos_c = np.sin(lat0_r) * np.sin(lat_r) + np.cos(lat0_r) * np.cos(lat_r) * np.cos(dlon)
    cos_c = np.clip(cos_c, -1.0, 1.0)
    c = np.arccos(cos_c)
    sin_c = np.sin(c)
    k = np.ones_like(c)
    mask = sin_c != 0
    k[mask] = c[mask] / sin_c[mask]
    x = r * k * np.cos(lat_r) * np.sin(dlon)
    y = r * k * (
        np.cos(lat0_r) * np.sin(lat_r) - np.sin(lat0_r) * np.cos(lat_r) * np.cos(dlon)
    )
    return x, y


def inverse_aeqd_distance_from_center(lat_offset_deg, r=R_KM) -> float:
    """中心向北偏移给定纬度时，投影距离应等于球面弧长。"""
    return r * math.radians(lat_offset_deg)


# ---------------------------------------------------------------------------
# 板块归属（复用既有立体图：within，否则经纬度平面最近）
# ---------------------------------------------------------------------------

def as_poly(g):
    if g is None or g.is_empty:
        return g
    g = make_valid(g)
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    if g.geom_type == "GeometryCollection":
        polys = [x for x in g.geoms if x.geom_type in ("Polygon", "MultiPolygon") and not x.is_empty]
        return unary_union(polys) if polys else g
    return g


def _load_geojson_features(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    feats = data["features"] if data.get("type") == "FeatureCollection" else [data]
    out = []
    for feat in feats:
        geom = shape(feat["geometry"]) if feat.get("geometry") else None
        props = dict(feat.get("properties") or {})
        out.append({"properties": props, "geometry": geom})
    return out


def _read_dbf_records(dbf_path: Path) -> list[dict]:
    data = Path(dbf_path).read_bytes()
    nrec = struct.unpack_from("<I", data, 4)[0]
    header_len = struct.unpack_from("<H", data, 8)[0]
    rec_len = struct.unpack_from("<H", data, 10)[0]
    fields = []
    offset = 32
    while offset < header_len - 1:
        if data[offset] == 0x0D:
            break
        name = data[offset : offset + 11].split(b"\x00", 1)[0].decode("latin-1").strip()
        typ = chr(data[offset + 11])
        length = data[offset + 16]
        fields.append((name, typ, length))
        offset += 32
    records = []
    pos = header_len
    for _ in range(nrec):
        rec = data[pos : pos + rec_len]
        pos += rec_len
        if not rec or rec[0] == 0x2A:  # deleted
            continue
        cur = 1
        row = {}
        for name, typ, length in fields:
            raw = rec[cur : cur + length]
            cur += length
            s = raw.decode("latin-1", errors="replace").strip()
            row[name] = s
        records.append(row)
    return records


def read_shapefile(shp_path: Path, with_properties: bool = False) -> list[dict]:
    """读取点/线/面 shapefile（2D 或带 Z），不依赖 geopandas/pyshp。"""
    shp_path = Path(shp_path)
    data = shp_path.read_bytes()
    if len(data) < 100:
        raise ValueError(f"shapefile 过短: {shp_path}")
    file_code = struct.unpack_from(">i", data, 0)[0]
    if file_code != 9994:
        raise ValueError(f"不是有效 shapefile: {shp_path}")
    props_list = None
    if with_properties:
        dbf = shp_path.with_suffix(".dbf")
        if not dbf.exists():
            raise FileNotFoundError(f"缺少 DBF: {dbf}")
        props_list = _read_dbf_records(dbf)

    def pts(buf, n, off, has_z=False, has_m=False):
        xy = []
        for i in range(n):
            x, y = struct.unpack_from("<dd", buf, off + i * 16)
            xy.append((x, y))
        return xy

    def parse_parts(rec, has_z=False, has_m=False):
        # after shape type (4) + box (32)
        off = 36
        n_parts, n_pts = struct.unpack_from("<ii", rec, off)
        off += 8
        parts = list(struct.unpack_from("<" + "i" * n_parts, rec, off))
        off += 4 * n_parts
        xy = pts(rec, n_pts, off)
        rings = []
        for i, start in enumerate(parts):
            end = parts[i + 1] if i + 1 < n_parts else n_pts
            seq = xy[start:end]
            if len(seq) >= 2:
                rings.append(seq)
        return rings

    geoms = []
    offset = 100
    rec_i = 0
    while offset + 8 <= len(data):
        rec_num, rec_len = struct.unpack_from(">ii", data, offset)
        offset += 8
        nbytes = rec_len * 2
        rec = data[offset : offset + nbytes]
        offset += nbytes
        if len(rec) < 4:
            continue
        st = struct.unpack_from("<i", rec, 0)[0]
        geom = None
        if st in (3, 13, 23):  # polyline / Z / M
            rings = parse_parts(rec, has_z=st == 13, has_m=st == 23)
            lines = [LineString(r) for r in rings if len(r) >= 2]
            if len(lines) == 1:
                geom = lines[0]
            elif len(lines) > 1:
                geom = MultiLineString(lines)
        elif st in (5, 15, 25):  # polygon
            rings = parse_parts(rec, has_z=st == 15, has_m=st == 25)
            # ESRI: first ring outer, negatives holes; we only need outlines later,
            # but keep proper polygons when possible.
            polys = []
            if rings:
                try:
                    # group simply: treat each closed ring as a polygon shell
                    for r in rings:
                        if len(r) >= 4:
                            polys.append(Polygon(r))
                    if len(polys) == 1:
                        geom = polys[0]
                    elif polys:
                        geom = MultiPolygon(polys)
                except Exception:
                    lines = [LineString(r) for r in rings if len(r) >= 2]
                    geom = MultiLineString(lines) if lines else None
        elif st in (1, 11, 21):
            x, y = struct.unpack_from("<dd", rec, 4)
            geom = Point(x, y)
        elif st == 0:
            geom = None
        else:
            # skip unknown types
            geom = None
        props = props_list[rec_i] if props_list is not None and rec_i < len(props_list) else {}
        geoms.append({"properties": props, "geometry": geom})
        rec_i += 1
    return geoms


def load_plates(paths: dict) -> list[dict]:
    """读取 PB2002 板块多边形，make_valid 后按 PlateName 合并被日界线切开的部分。"""
    feats = None
    source = None
    if paths.get("plate_shp") and Path(paths["plate_shp"]).exists():
        try:
            feats = read_shapefile(paths["plate_shp"], with_properties=True)
            source = str(Path(paths["plate_shp"]).resolve())
        except Exception as exc:
            print("读取板块 shapefile 失败，回退 GeoJSON：", exc)
            feats = None
    if feats is None:
        if not paths.get("plate_json"):
            raise FileNotFoundError("没有可用的 PB2002 板块多边形")
        feats = _load_geojson_features(paths["plate_json"])
        source = str(Path(paths["plate_json"]).resolve())

    groups = defaultdict(list)
    meta = {}
    for feat in feats:
        props = feat["properties"] or {}
        name = props.get("PlateName") or props.get("PLATENAME") or props.get("Name")
        if not name:
            continue
        g = as_poly(feat["geometry"])
        if g is None or g.is_empty:
            continue
        groups[name].append(g)
        if name not in meta:
            meta[name] = {
                "PlateName": name,
                "Code": props.get("Code") or props.get("CODE") or "",
            }
    plates = []
    for name, geoms in groups.items():
        merged = as_poly(unary_union(geoms))
        if merged is None or merged.is_empty:
            continue
        item = dict(meta[name])
        item["geometry"] = merged
        plates.append(item)
    plates.sort(key=lambda d: d["PlateName"])
    print(f"板块数据: {source} 合并后要素数: {len(plates)}")
    return plates


def assign_plates(df: pd.DataFrame, plates: list[dict]) -> tuple[pd.DataFrame, dict]:
    """点在多边形内则归该板块；边界或缝隙归最近板块（经纬度平面距离）。"""
    geoms = [p["geometry"] for p in plates]
    tree = STRtree(geoms)
    names = []
    codes = []
    rules = []
    n_within = n_nearest = n_unassigned = 0
    lons = df["Longitude"].to_numpy()
    lats = df["Latitude"].to_numpy()
    for lon, lat in zip(lons, lats):
        pt = Point(float(lon), float(lat))
        hits = tree.query(pt, predicate="within")
        if hits is not None and len(np.atleast_1d(hits)):
            idx = int(np.atleast_1d(hits)[0])  # keep first
            names.append(plates[idx]["PlateName"])
            codes.append(plates[idx]["Code"])
            rules.append("within")
            n_within += 1
            continue
        near = tree.nearest(pt)
        if near is None:
            names.append(None)
            codes.append(None)
            rules.append(None)
            n_unassigned += 1
        else:
            idx = int(near)
            names.append(plates[idx]["PlateName"])
            codes.append(plates[idx]["Code"])
            rules.append("nearest")
            n_nearest += 1
    out = df.copy()
    out["PlateName"] = names
    out["PlateCode"] = codes
    out["assign_rule"] = rules
    out["plate_hover"] = [
        (
            f"{PLATE_CN.get(n, n)}（{n} / {c}）"
            if n and c
            else (f"{PLATE_CN.get(n, n)}（{n}）" if n else "未归属")
        )
        for n, c in zip(names, codes)
    ]
    stats = {
        "n_assigned_input": int(len(out)),
        "n_within": int(n_within),
        "n_nearest": int(n_nearest),
        "n_unassigned": int(n_unassigned),
        "assign_rule": "点落在 PB2002 板块多边形内则归该板块；在边界上或缝隙中则归最近板块（距离在经纬度平面上计算，与既有立体图 sjoin_nearest 一致，不是大地线距离）。",
    }
    print(
        f"空间样本: {len(out)} 已归属: {len(out) - n_unassigned} "
        f"未归属: {n_unassigned}；within={n_within} nearest={n_nearest}"
    )
    return out, stats


def plate_count_table(eq: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, sub in eq.groupby("PlateName", dropna=False):
        rows.append(
            {
                "plate_name": name if pd.notna(name) else "未归属",
                "plate_name_zh": PLATE_CN.get(name, "未归属") if pd.notna(name) else "未归属",
                "code": (
                    sub["PlateCode"].dropna().iloc[0]
                    if "PlateCode" in sub.columns and sub["PlateCode"].notna().any()
                    else ""
                ),
                "n_events": int(len(sub)),
                "n_within": int((sub["assign_rule"] == "within").sum()),
                "n_nearest": int((sub["assign_rule"] == "nearest").sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["n_events", "plate_name"], ascending=[False, True])


def compare_plate_counts(table: pd.DataFrame, counts_csv: Path | None) -> dict:
    if counts_csv is None or not Path(counts_csv).exists():
        return {"compared": False, "reason": "没有既有 07_st_3d_plate_counts.csv"}
    prev = pd.read_csv(counts_csv)
    merged = table.merge(
        prev[["plate_name", "n_events"]].rename(columns={"n_events": "n_prev"}),
        on="plate_name",
        how="outer",
    )
    merged["n_events"] = merged["n_events"].fillna(0).astype(int)
    merged["n_prev"] = merged["n_prev"].fillna(0).astype(int)
    merged["delta"] = merged["n_events"] - merged["n_prev"]
    diffs = merged[merged["delta"] != 0]
    return {
        "compared": True,
        "counts_csv": str(Path(counts_csv).resolve()),
        "n_mismatch_plates": int(len(diffs)),
        "mismatches": diffs[["plate_name", "n_events", "n_prev", "delta"]].to_dict("records"),
        "sum_new": int(table["n_events"].sum()),
        "sum_prev": int(prev["n_events"].sum()),
    }


# ---------------------------------------------------------------------------
# 地图线：读取、裁切、抽稀（仅显示）、投影
# ---------------------------------------------------------------------------

def parse_gmt_lines(path: Path) -> list[list[tuple[float, float]]]:
    lines: list[list[tuple[float, float]]] = []
    cur: list[tuple[float, float]] = []
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith(">"):
            if len(cur) >= 2:
                lines.append(cur)
            cur = []
            continue
        parts = s.split()
        if len(parts) < 2:
            continue
        try:
            lon = float(parts[0])
            lat = float(parts[1])
        except ValueError:
            continue
        cur.append((lon, lat))
    if len(cur) >= 2:
        lines.append(cur)
    return lines


def _iter_line_coords(geom):
    if geom is None or geom.is_empty:
        return
    gt = geom.geom_type
    if gt == "LineString":
        yield list(geom.coords)
    elif gt == "LinearRing":
        yield list(geom.coords)
    elif gt == "MultiLineString":
        for g in geom.geoms:
            yield list(g.coords)
    elif gt == "Polygon":
        yield list(geom.exterior.coords)
        for r in geom.interiors:
            yield list(r.coords)
    elif gt == "MultiPolygon":
        for g in geom.geoms:
            yield list(g.exterior.coords)
            for r in g.interiors:
                yield list(r.coords)
    elif gt == "GeometryCollection":
        for g in geom.geoms:
            yield from _iter_line_coords(g)


def geometries_to_lines(geoms) -> list[LineString]:
    out = []
    for geom in geoms:
        if geom is None:
            continue
        try:
            g = make_valid(geom) if not geom.is_empty else geom
        except Exception:
            g = geom
        for coords in _iter_line_coords(g):
            if len(coords) >= 2:
                try:
                    out.append(LineString([(c[0], c[1]) for c in coords]))
                except Exception:
                    continue
    return out


def densify_coords(coords, max_deg=DENSIFY_DEG):
    if len(coords) < 2:
        return coords
    out = [coords[0]]
    for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        if d > max_deg and max_deg > 0:
            n = int(math.ceil(d / max_deg))
            for i in range(1, n):
                t = i / n
                out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
        out.append((x1, y1))
    return out


def clip_and_project_lines(
    lines: list[LineString],
    bbox,
    simplify_km: float,
) -> tuple[list[np.ndarray], dict]:
    n_in = len(lines)
    n_vert_in = 0
    n_vert_out = 0
    parts_out = []
    for ln in lines:
        if ln is None or ln.is_empty or ln.geom_type not in ("LineString", "LinearRing"):
            continue
        n_vert_in += len(ln.coords)
        try:
            clipped = ln.intersection(bbox)
        except Exception:
            continue
        if clipped is None or clipped.is_empty:
            continue
        segs = []
        if clipped.geom_type in ("LineString", "LinearRing"):
            segs = [clipped]
        elif clipped.geom_type == "MultiLineString":
            segs = list(clipped.geoms)
        elif clipped.geom_type == "GeometryCollection":
            segs = [g for g in clipped.geoms if g.geom_type in ("LineString", "LinearRing")]
        for seg in segs:
            coords = densify_coords([(c[0], c[1]) for c in seg.coords], DENSIFY_DEG)
            if len(coords) < 2:
                continue
            xs, ys = project_lonlat([c[0] for c in coords], [c[1] for c in coords])
            # 投影后按大跳跃拆段
            chunks = []
            cx, cy = [xs[0]], [ys[0]]
            for i in range(1, len(xs)):
                if math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]) > JUMP_SPLIT_KM:
                    if len(cx) >= 2:
                        chunks.append((np.array(cx), np.array(cy)))
                    cx, cy = [xs[i]], [ys[i]]
                else:
                    cx.append(xs[i])
                    cy.append(ys[i])
            if len(cx) >= 2:
                chunks.append((np.array(cx), np.array(cy)))
            for x, y in chunks:
                if simplify_km and simplify_km > 0 and len(x) >= 3:
                    try:
                        simp = LineString(np.column_stack([x, y])).simplify(
                            simplify_km, preserve_topology=False
                        )
                        if simp.is_empty or simp.geom_type != "LineString" or len(simp.coords) < 2:
                            continue
                        xy = np.array(simp.coords)
                        x, y = xy[:, 0], xy[:, 1]
                    except Exception:
                        pass
                n_vert_out += len(x)
                parts_out.append(np.column_stack([x, y]))
    stats = {
        "n_segments_in": n_in,
        "n_segments_out": len(parts_out),
        "n_vertices_in": n_vert_in,
        "n_vertices_out": n_vert_out,
        "simplify_tol_km": simplify_km,
        "densify_deg": DENSIFY_DEG,
        "note": "抽稀与裁切仅用于显示，未改写原始文件。",
    }
    return parts_out, stats


def parts_to_xyz(parts: list[np.ndarray]) -> dict:
    xs, ys, zs = [], [], []
    for i, arr in enumerate(parts):
        if i:
            xs.append(None)
            ys.append(None)
            zs.append(None)
        for x, y in arr:
            xs.append(round(float(x), 3))
            ys.append(round(float(y), 3))
            zs.append(0.0)
    return {"x": xs, "y": ys, "z": zs}


def load_all_layers(paths: dict) -> tuple[dict, dict]:
    bbox = box(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX)
    layers = {}
    stats = {}

    def add_shapefile_outlines(key, shp, title):
        feats = read_shapefile(shp, with_properties=False)
        geoms = [f["geometry"] for f in feats if f.get("geometry") is not None]
        lines = geometries_to_lines(geoms)
        parts, st = clip_and_project_lines(lines, bbox, SIMPLIFY_TOL_KM[key])
        payload = parts_to_xyz(parts)
        payload["title"] = title
        payload["source"] = str(Path(shp).resolve())
        layers[key] = payload
        st["source"] = payload["source"]
        st["title"] = title
        stats[key] = st
        print(f"图层 {key}: 段 {st['n_segments_in']}->{st['n_segments_out']} 顶点 {st['n_vertices_in']}->{st['n_vertices_out']}")

    def add_geojson_lines(key, path, title):
        feats = _load_geojson_features(path)
        geoms = [f["geometry"] for f in feats if f.get("geometry") is not None]
        lines = geometries_to_lines(geoms)
        parts, st = clip_and_project_lines(lines, bbox, SIMPLIFY_TOL_KM[key])
        payload = parts_to_xyz(parts)
        payload["title"] = title
        payload["source"] = str(Path(path).resolve())
        layers[key] = payload
        st["source"] = payload["source"]
        st["title"] = title
        stats[key] = st
        print(f"图层 {key}: 段 {st['n_segments_in']}->{st['n_segments_out']} 顶点 {st['n_vertices_in']}->{st['n_vertices_out']}")

    def add_gmt(key, path, title):
        raw = parse_gmt_lines(path)
        lines = [LineString(c) for c in raw if len(c) >= 2]
        parts, st = clip_and_project_lines(lines, bbox, SIMPLIFY_TOL_KM[key])
        payload = parts_to_xyz(parts)
        payload["title"] = title
        payload["source"] = str(Path(path).resolve())
        layers[key] = payload
        st["source"] = payload["source"]
        st["title"] = title
        stats[key] = st
        print(f"图层 {key}: 段 {st['n_segments_in']}->{st['n_segments_out']} 顶点 {st['n_vertices_in']}->{st['n_vertices_out']}")

    add_shapefile_outlines("coast", paths["land_shp"], "海岸线")
    add_shapefile_outlines("border", paths["country_shp"], "国界")
    if paths.get("plate_bnd_json") and Path(paths["plate_bnd_json"]).exists():
        add_geojson_lines("plate", paths["plate_bnd_json"], "PB2002 板块边界")
    else:
        add_shapefile_outlines("plate", paths["plate_bnd_shp"], "PB2002 板块边界")

    bdir = Path(paths["blocks_dir"])
    add_gmt("block_l1", bdir / "CN-block-L1.gmt", "中国一级活动地块边界")
    add_gmt("block_l1d", bdir / "CN-block-L1-deduced.gmt", "中国一级地块推断边界")
    add_gmt("block_l2", bdir / "CN-block-L2.gmt", "中国二级活动地块边界")
    add_gmt("fault", paths["faults_gmt"], "中国活动断层")
    return layers, stats


# ---------------------------------------------------------------------------
# 组装数据与 HTML
# ---------------------------------------------------------------------------

def project_events(df: pd.DataFrame) -> pd.DataFrame:
    x, y = project_lonlat(df["Longitude"].to_numpy(), df["Latitude"].to_numpy())
    out = df.copy()
    out["x_km"] = x
    out["y_km"] = y
    out["z_km"] = -out["Depth"].astype(float)  # 地表 0，向下为负，单位 km
    return out


def scene_from_events(df: pd.DataFrame, layers: dict) -> dict:
    xs = df["x_km"].to_numpy()
    ys = df["y_km"].to_numpy()
    # 把地图线也纳入水平范围，保证框住整个研究区
    all_x = [float(xs.min()), float(xs.max())]
    all_y = [float(ys.min()), float(ys.max())]
    for ly in layers.values():
        vx = [v for v in ly["x"] if v is not None]
        vy = [v for v in ly["y"] if v is not None]
        if vx:
            all_x.extend((min(vx), max(vx)))
        if vy:
            all_y.extend((min(vy), max(vy)))
    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = min(all_y), max(all_y)
    padx = 0.03 * (xmax - xmin or 1)
    pady = 0.03 * (ymax - ymin or 1)
    xrange = [xmin - padx, xmax + padx]
    yrange = [ymin - pady, ymax + pady]
    zmax = float(df["Depth"].max())
    zpad = max(20.0, 0.05 * zmax)
    zrange = [-(zmax + zpad), zpad]
    xspan = xrange[1] - xrange[0]
    yspan = yrange[1] - yrange[0]
    zspan = zrange[1] - zrange[0]
    # 归一化到合理视觉尺度，保持跨度比 = 物理跨度比
    scale = max(xspan, yspan)
    aspect_1 = {
        "x": round(xspan / scale, 6),
        "y": round(yspan / scale, 6),
        "z": round(zspan / scale, 6),
    }
    # 深度刻度（正向标注）
    pretty = [0, 50, 100, 150, 200, 300, 400, 500, 600, 700]
    ticks = [d for d in pretty if d <= zmax + 1e-6]
    if not ticks or ticks[-1] < zmax * 0.9:
        ticks.append(int(round(zmax)))
    z_tickvals = [-d for d in ticks]
    z_ticktext = [str(d) for d in ticks]
    return {
        "xrange": [round(xrange[0], 3), round(xrange[1], 3)],
        "yrange": [round(yrange[0], 3), round(yrange[1], 3)],
        "zrange": [round(zrange[0], 3), round(zrange[1], 3)],
        "xspan_km": round(xspan, 3),
        "yspan_km": round(yspan, 3),
        "zspan_km": round(zspan, 3),
        "aspect_1": aspect_1,
        "cmin": 0.0,
        "cmax": round(zmax, 2),
        "colorscale": COLORSCALE,
        "z_tickvals": z_tickvals,
        "z_ticktext": z_ticktext,
        "projection": {
            "name": "azimuthal equidistant (spherical)",
            "lon0": PROJ_LON0,
            "lat0": PROJ_LAT0,
            "R_km": R_KM,
            "units": "km",
        },
    }


def events_payload(df: pd.DataFrame) -> dict:
    def rnd(series, nd):
        return [round(float(v), nd) for v in series]

    return {
        "x": rnd(df["x_km"], 3),
        "y": rnd(df["y_km"], 3),
        "z": rnd(df["z_km"], 3),
        "lon": rnd(df["Longitude"], 4),
        "lat": rnd(df["Latitude"], 4),
        "depth": rnd(df["Depth"], 2),
        "mag": rnd(df["Magnitude"], 2),
        "year": [int(v) for v in df["year"]],
        "date": list(df["hover_date"].astype(str)),
        "time": list(df["hover_time"].astype(str)),
        "plate": list(df["plate_hover"].astype(str)),
    }


def build_payload(df: pd.DataFrame, layers: dict, stats: dict, layer_stats: dict, assign_stats: dict) -> dict:
    scene = scene_from_events(df, layers)
    meta = {
        "title": "中国及周边三维震源分布",
        "built_at": now_cst_label(),
        "n_main_sample": stats["n_main_sample"],
        "n_plotted": int(len(df)),
        "n_region_coord": stats["n_region_coord"],
        "n_region_missing_depth_excluded": stats["n_region_missing_depth_excluded"],
        "n_global_missing_depth": stats["n_global_missing_depth"],
        "n_outside_region": stats["n_outside_region"],
        "n_region_possible_duplicate_kept": stats["n_region_possible_duplicate_kept"],
        "sample_sha256": stats["sample_sha256"],
        "projection": "球面方位等距投影，中心 107.5°E、35°N，R=6371 km",
    }
    return {
        "meta": meta,
        "events": events_payload(df),
        "layers": layers,
        "scene": scene,
        "marker_size": MARKER_SIZE,
        "filters": {
            "year_min": int(stats["year_min"]),
            "year_max": int(stats["year_max"]),
            "mag_min": float(stats["mag_min"]),
            "mag_max": float(stats["mag_max"]),
        },
        "stats": stats,
        "layer_stats": layer_stats,
        "assign_stats": assign_stats,
    }


def get_plotly_js() -> str:
    try:
        from plotly.offline import get_plotlyjs

        return get_plotlyjs()
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    cand = here / "plotly.min.js"
    if cand.exists():
        return cand.read_text(encoding="utf-8")
    raise RuntimeError(
        "无法得到 plotly.min.js。请安装 Python 包 plotly，或将 plotly.min.js 放在本脚本同目录。"
    )


def write_html(payload: dict, out_html: Path, force: bool = False) -> Path:
    here = Path(__file__).resolve().parent
    template = (here / "hypocenter_3d_template.html").read_text(encoding="utf-8")
    filter_js = (here / "filter_logic.js").read_text(encoding="utf-8")
    plotly_js = get_plotly_js()
    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data_json = data_json.replace("<", "\\u003c")
    html = (
        template.replace("__PLOTLY_JS__", plotly_js)
        .replace("__FILTER_JS__", filter_js)
        .replace("__DATA_JSON__", data_json)
    )
    out_html = Path(out_html)
    if out_html.exists() and not force:
        raise FileExistsError(f"已存在 {out_html}，拒绝覆盖。需要时传入 force=True。")
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    return out_html


def write_counts_sidecar(payload: dict, out_json: Path, force: bool = False) -> Path:
    out_json = Path(out_json)
    if out_json.exists() and not force:
        raise FileExistsError(f"已存在 {out_json}，拒绝覆盖。")
    slim = {
        "built_at": payload["meta"]["built_at"],
        "stats": payload["stats"],
        "assign_stats": payload["assign_stats"],
        "layer_stats": payload["layer_stats"],
        "scene": {
            k: payload["scene"][k]
            for k in (
                "xrange",
                "yrange",
                "zrange",
                "xspan_km",
                "yspan_km",
                "zspan_km",
                "aspect_1",
                "cmin",
                "cmax",
                "projection",
            )
        },
        "sample_sha256": payload["meta"]["sample_sha256"],
        "n_plotted": payload["meta"]["n_plotted"],
    }
    out_json.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


def safe_write_text(path: Path, text: str, force: bool = False) -> Path:
    path = Path(path)
    if path.exists() and not force:
        raise FileExistsError(f"已存在 {path}，拒绝覆盖。")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_all(start: Path | None = None, out_dir: Path | None = None, force: bool = False) -> dict:
    paths = find_paths(start)
    out_dir = Path(out_dir) if out_dir else paths["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    df, gstats = load_sample(paths["sample"])
    print(
        f"读取主样本: {gstats['n_main_sample']}  Date_parsed 失败: {gstats['n_date_parse_fail']}  "
        f"缺失深度: {gstats['n_global_missing_depth']}"
    )
    region, stats = filter_region(df, gstats)
    print(
        f"区域 {LON_MIN}–{LON_MAX}E, {LAT_MIN}–{LAT_MAX}N: {stats['n_region_coord']} 条，"
        f"排除缺失深度 {stats['n_region_missing_depth_excluded']}，用于作图 {stats['n_region_used']}；"
        f"浅/中/深 = {stats['n_shallow']}/{stats['n_intermediate']}/{stats['n_deep']}；"
        f"疑似重复保留 {stats['n_region_possible_duplicate_kept']}"
    )

    # 先对全主样本（坐标有效）归属，便于与既有计数表对照；再映射到区域子集
    plates = load_plates(paths)
    spatial = df.loc[
        ~df.get("flag_coord_invalid", False) & df["Latitude"].notna() & df["Longitude"].notna()
    ].copy()
    assigned_all, assign_all_stats = assign_plates(spatial, plates)
    table_all = plate_count_table(assigned_all)
    cmp = compare_plate_counts(table_all, paths.get("counts_csv"))
    assign_all_stats["compare_existing_counts"] = cmp
    if cmp.get("compared"):
        print(
            f"与既有板块计数表对照: 不匹配板块数={cmp['n_mismatch_plates']} "
            f"新合计={cmp['sum_new']} 旧合计={cmp['sum_prev']}"
        )

    # 区域事件的归属
    region = region.merge(
        assigned_all[["PlateName", "PlateCode", "assign_rule", "plate_hover"]],
        left_index=True,
        right_index=True,
        how="left",
    )
    assign_region = {
        "n_region": int(len(region)),
        "n_within": int((region["assign_rule"] == "within").sum()),
        "n_nearest": int((region["assign_rule"] == "nearest").sum()),
        "n_unassigned": int(region["PlateName"].isna().sum()),
        "global": assign_all_stats,
    }
    print(
        f"区域归属: within={assign_region['n_within']} nearest={assign_region['n_nearest']} "
        f"未归属={assign_region['n_unassigned']}"
    )

    region = project_events(region)
    layers, layer_stats = load_all_layers(paths)
    payload = build_payload(region, layers, stats, layer_stats, assign_region)

    html_path = out_dir / "07_china_region_hypocenter_3d.html"
    counts_path = out_dir / "07_china_region_hypocenter_3d_counts.json"
    write_html(payload, html_path, force=force)
    write_counts_sidecar(payload, counts_path, force=force)
    print("写入", html_path, "bytes", html_path.stat().st_size)
    return {
        "paths": {k: (str(v) if v is not None else None) for k, v in paths.items()},
        "html": str(html_path),
        "counts_json": str(counts_path),
        "stats": stats,
        "assign": assign_region,
        "layer_stats": layer_stats,
        "payload": payload,
        "df": region,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="生成中国及周边独立离线 HTML 三维震源图")
    p.add_argument("--start", type=Path, default=None, help="路径搜索起点")
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--force", action="store_true", help="允许覆盖已有同名 HTML/计数 JSON")
    args = p.parse_args(argv)
    build_all(start=args.start, out_dir=args.out_dir, force=args.force)


if __name__ == "__main__":
    main()
