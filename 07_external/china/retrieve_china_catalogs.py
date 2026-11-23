#!/usr/bin/env python3
"""Raw collection of the publicly queryable 中国地震台网正式地震目录 (M>=5.5).

Only concatenates official HTML query pages (strips repeated headers).
Does not clean, filter, convert timezones, or overwrite older 07_external layers.
Official Excel/bulk download on data.earthquake.cn requires login and is not used.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

CST = ZoneInfo("Asia/Shanghai")
UA = "BNBU-DS2043-earthquake-external-collection/1.0 (academic course project; educational use)"
BASE = "https://data.earthquake.cn/datashare/report.shtml"
DEST = Path("/workspace/07_external/china")
LOG_PATH = DEST / "retrieve_log.txt"
CSV_PATH = DEST / "catalogs" / "07_cenc_zhengshi_m55_2009_latest.csv"

BEGTIME = "2009-01-01"
# Retrieval calendar date in Asia/Shanghai; the form expands a date-only endtime to 23:59:59.
ENDTIME = "2026-11-16"
MINM = "5.5"
MAXM = "10"

COLUMNS = [
    "序号",
    "发震日期（北京时间）",
    "经度(°)",
    "纬度(°)",
    "震源深度(Km)",
    "震级类型",
    "震级",
    "震中位置",
    "事件类型",
]


def now_cst() -> datetime:
    return datetime.now(CST)


def ts() -> str:
    return now_cst().strftime("%Y-%m-%d %H:%M:%S %Z")


def log(msg: str) -> None:
    line = f"[{ts()}] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_catalog_page(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = html
    total_m = re.search(r"共&nbsp;<b>(\d+)</b>&nbsp;条", text)
    per_m = re.search(r"每页&nbsp;<b>(\d+)</b>&nbsp;条", text)
    page_m = re.search(
        r"当前第&nbsp;<b>(\d+)</b>&nbsp;页/共&nbsp;<b>(\d+)</b>&nbsp;页", text
    )
    rec_m = re.search(r"catalog_RECORDCOUNT=(\d+)", text)
    pgc_m = re.search(r"catalog_PAGECOUNT=(\d+)", text)

    def visible_cells(tr):
        out = []
        for td in tr.find_all(["th", "td"], recursive=False):
            style = (td.get("style") or "").replace(" ", "").lower()
            if "display:none" in style:
                continue  # Wabacus hidden spacer, not an official field
            out.append(re.sub(r"\s+", " ", td.get_text()).strip())
        return out

    # Use the official list rows (cls-data-tr-*), not the huge wrapping page table.
    data_trs = soup.find_all("tr", class_=re.compile(r"^cls-data-tr-(even|odd)$"))
    head_trs = soup.find_all("tr", class_=re.compile(r"cls-data-tr-head"))
    if not data_trs and "无数据" in text and not total_m:
        return {
            "total": 0,
            "per_page": 20,
            "page": 1,
            "page_count": 0,
            "rows": [],
            "empty": True,
            "header": None,
        }
    if not data_trs and not head_trs:
        raise ValueError("could not find catalog table rows")

    header = visible_cells(head_trs[0]) if head_trs else None
    rows_out: list[list[str]] = []
    for tr in data_trs:
        cells = visible_cells(tr)
        if not cells:
            continue
        if cells == ["无数据"] or (len(cells) == 1 and "无数据" in cells[0]):
            continue
        rows_out.append(cells)

    total = int(total_m.group(1)) if total_m else (int(rec_m.group(1)) if rec_m else len(rows_out))
    per_page = int(per_m.group(1)) if per_m else 20
    page = int(page_m.group(1)) if page_m else 1
    page_count = int(page_m.group(2)) if page_m else (int(pgc_m.group(1)) if pgc_m else 1)
    if header and header != COLUMNS:
        # keep going but record mismatch
        pass
    return {
        "total": total,
        "per_page": per_page,
        "page": page,
        "page_count": page_count,
        "header": header,
        "rows": rows_out,
        "empty": False,
    }


def build_url(page: int | None, total: int | None, page_count: int | None) -> str:
    params = {
        "DISPLAY_TYPE": "1",
        "PAGEID": "earthquake_zhengshi",
        "minM": MINM,
        "maxM": MAXM,
        "location": "",
        "locationselect": "",
        "begtime": BEGTIME,
        "endtime": ENDTIME,
        "minLat": "-90.0",
        "maxLat": "90.0",
        "minLon": "-180.0",
        "maxLon": "180.0",
        "minDepths": "0",
        "maxDepths": "1000",
    }
    if page is not None and total is not None and page_count is not None:
        params["catalog_PAGENO"] = str(page)
        params["catalog_ALLDATASETS_RECORDCOUNT"] = (
            f"catalog__default_default_default_key__default_default_default_key={total};"
        )
        params["catalog_RECORDCOUNT"] = str(total)
        params["catalog_PAGECOUNT"] = str(page_count)
    # doseq not needed; urlencode will encode = and ; in ALLDATASETS
    return BASE + "?" + urlencode(params, safe="")


def fetch_page(session: requests.Session, url: str, expected_page: int | None = None, retries: int = 4) -> dict[str, Any]:
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=60)
            r.raise_for_status()
            if "login.jsp" in r.url and "earthquake_zhengshi" not in r.url:
                raise RuntimeError(f"redirected to login: {r.url}")
            parsed = parse_catalog_page(r.text)
            if expected_page is not None and parsed.get("page") != expected_page and not parsed.get("empty"):
                raise RuntimeError(
                    f"expected page {expected_page}, got {parsed.get('page')} rows={len(parsed['rows'])}"
                )
            if expected_page is not None and expected_page > 1 and not parsed["rows"]:
                raise RuntimeError(f"page {expected_page} parsed zero rows")
            return parsed
        except Exception as e:  # noqa: BLE001 — log and retry network/parse issues
            last_err = e
            wait = min(8, 1.5 * attempt)
            log(f"WARN fetch attempt {attempt}/{retries} failed: {e}; sleep {wait:.1f}s")
            time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    # start/append log
    log("Start 中国地震台网正式地震目录 public HTML query collection")
    log(f"User-Agent: {UA}")
    log(f"Query: PAGEID=earthquake_zhengshi minM={MINM} maxM={MAXM} begtime={BEGTIME} endtime={ENDTIME} (date-only endtime; site expands to 23:59:59)")
    log("Timezone: official column is 发震日期（北京时间）; values kept as-is, not converted")
    log("Method: public DISPLAY_TYPE=1 HTML query pages, 20 rows/page; Excel/bulk export is login-walled and was not used")

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"})

    url1 = build_url(None, None, None)
    log(f"GET page 1 (no pagination params) {url1}")
    first = fetch_page(session, url1, expected_page=1)
    total = first["total"]
    page_count = first["page_count"]
    per_page = first["per_page"]
    header = first.get("header") or COLUMNS
    log(f"Page 1 ok: total={total} per_page={per_page} page_count={page_count} header={header} first_row={first['rows'][0] if first['rows'] else None}")
    if header != COLUMNS:
        log(f"WARN header differs from expected COLUMNS: {header}")

    if any(len(r) != len(COLUMNS) for r in first["rows"]):
        raise RuntimeError(f"page 1 has a row with unexpected width: {[len(r) for r in first['rows'][:3]]}")
    all_rows: list[list[str]] = list(first["rows"])
    expected_pages = page_count
    if total == 0:
        log("No rows returned for this query")
        return 1

    for pno in range(2, expected_pages + 1):
        url = build_url(pno, total, page_count)
        parsed = fetch_page(session, url, expected_page=pno)
        n = len(parsed["rows"])
        if any(len(r) != len(COLUMNS) for r in parsed["rows"]):
            raise RuntimeError(f"page {pno} has a row with unexpected width: {[len(r) for r in parsed['rows'][:3]]}")
        # last page may be short
        if pno < expected_pages and n != per_page:
            log(f"WARN page {pno} has {n} rows, expected {per_page}")
        if parsed["total"] != total:
            log(f"WARN page {pno} reports total={parsed['total']} (page 1 was {total})")
        all_rows.extend(parsed["rows"])
        if pno == 2 or pno == expected_pages or pno % 25 == 0:
            log(f"Page {pno}/{expected_pages} ok rows_on_page={n} cumulative={len(all_rows)} first={parsed['rows'][0] if parsed['rows'] else None}")
        # gentle pacing
        time.sleep(0.15)

    log(f"Fetched {len(all_rows)} data rows from {expected_pages} pages (declared total={total})")
    if len(all_rows) != total:
        log(f"ERROR row count {len(all_rows)} != declared total {total}")

    # write CSV, official field names, all rows, no filtering
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNS if header is None else header)
        for row in all_rows:
            w.writerow(row)

    digest = sha256_file(CSV_PATH)
    size = CSV_PATH.stat().st_size
    log(f"Wrote {CSV_PATH} bytes={size} sha256={digest} rows={len(all_rows)} cols={len(header or COLUMNS)}")

    # summary stats (no row drops)
    times = [r[1] for r in all_rows if len(r) > 1]
    mags = []
    for r in all_rows:
        try:
            mags.append(float(r[6]))
        except Exception:
            pass
    types = Counter(r[8] if len(r) > 8 else "" for r in all_rows)
    magtypes = Counter(r[5] if len(r) > 5 else "" for r in all_rows)
    seq = [r[0] for r in all_rows]
    log(f"Time range as given (北京时间): {min(times) if times else None} .. {max(times) if times else None}")
    # also first/last in file order (site sorts descending)
    log(f"File-order first origin time: {times[0] if times else None}; last: {times[-1] if times else None}")
    log(f"Magnitude range (numeric 震级 column only): {min(mags) if mags else None} .. {max(mags) if mags else None} (n_numeric={len(mags)})")
    log(f"事件类型: {dict(types)}")
    log(f"震级类型: {dict(magtypes)}")
    log(f"序号 first={seq[0] if seq else None} last={seq[-1] if seq else None}")
    log("Finished formal catalog HTML query collection")
    return 0 if len(all_rows) == total else 2


if __name__ == "__main__":
    sys.exit(main())
