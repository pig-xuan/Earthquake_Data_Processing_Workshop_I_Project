# 07_external 数据来源说明

本目录是 BNBU DS 2043 项目选项 07（地震）的**外部公开数据原始收集结果**，只做官方下载、格式原样保存与必要的分页/分窗拼接（例如 USGS 年度窗口合并时去掉重复表头、NCEI JSON 转为 CSV、官方 NDK 按文件顺序拼接），**未做清洗、筛选、去重数据行、地理编码、可视化或建模**。收集过程没有修改或覆盖 `ProjectData` 原始数据、既有 `acquired` 档案，也没有改动 `/workspace/07_fine_clean/` 下的任何文件。2022–2023 年 USGS 目录是从本地已获取文件**复制**而来，没有重新向 ComCat 请求，以免目录修订造成内容漂移。

- 检索起始时间：2026-11-15 12:34:24 CST（UTC+8）；各文件在 12:34–12:40 CST 之间落盘。
- 用户代理：`BNBU-DS2043-earthquake-external-collection/1.0 (academic course project; educational use)`
- 可复现脚本：`retrieve_07_external.py`（可重新拉取 USGS / NCEI / GitHub / GCMT；其中 2022–2023 USGS 文件仍从本地副本复制，不重新下载）。
- 本次运行日志与机器可读清单：`retrieve_log.txt`、`retrieval_manifest.json`。
- 目录合计约 126 MB，80 个文件（含本说明）。本次三层数据均已完整获取，无失败项。下列行数、时间范围、字节数与 sha256 均为落盘后实测。

## 目录树

```
07_external/
├── SOURCES.md
├── retrieve_07_external.py
├── retrieve_log.txt
├── retrieval_manifest.json
├── catalogs/
│   ├── 07_usgs_quakes_m5_2017_2021.csv
│   ├── 07_usgs_quakes_m5_2022_2023.csv          # 本地复制，未重下
│   ├── 07_usgs_quakes_m5_2024_now.csv
│   └── 07_usgs_quakes_m55_1965_2016.csv
├── impact/
│   ├── ncei_significant_earthquakes.csv
│   ├── ncei_significant_tsunamis.csv
│   ├── ncei_tsunami_runups.csv
│   ├── ncei_tsunami_deposits.csv
│   └── ncei_tsunami_marigrams.csv
└── context/
    ├── tectonicplates/                          # Bird 2003 PB2002（含 GeoJSON、shapefile、original、zip）
    ├── gem_global_active_faults/                # GEM GAF-DB GeoJSON + 许可与说明
    └── gcmt/                                    # 官方 NDK + 格式说明与引用页
        ├── jan76_dec25.ndk
        ├── monthly_2026/*.ndk
        ├── gcmt_1976_latest.ndk                 # 上述官方文件拼接
        ├── pre1976/
        └── quick/qcmt.ndk
```

---

## 1. 地震目录（`catalogs/`）

来源机构：U.S. Geological Survey (USGS)，ANSS Comprehensive Earthquake Catalog (ComCat)，FDSN Event Web Service。

基础地址：`https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv`  
计数接口：`https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson`  
文档：`https://earthquake.usgs.gov/fdsnws/event/1/`

共同查询参数：`format=csv`，`minmagnitude`，`starttime`，`endtime`（UTC）。使用默认 ComCat，**未设置** `eventtype`，未丢弃任何数据行。单次查询上限 20,000 条；超过时按公历年拆分后再合并（仅去掉重复表头，按 `time` 排序）。四个 CSV 的列均为标准 USGS CSV 前 12 列起首：`time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id`，共 22 列。

许可 / 使用条款：美国联邦政府作品，公有领域（public domain）。参见 USGS Copyrights and Credits：https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits

### `catalogs/07_usgs_quakes_m5_2017_2021.csv`

- 用途：补齐本地目录结束于 2016 年之后、已有 2022–2023 目录之前的空档。
- 查询：`minmagnitude=5`，`starttime=2017-01-01`，`endtime=2022-01-01`（用次日零时作为窗口终点，覆盖至 2021-12-31）。计数接口返回 8711，低于 20,000，一次拉取。
- 检索时间：2026-11-15 12:34 起，CST（UTC+8）。
- 覆盖：时间 `2017-01-01T00:13:25.380Z`–`2021-12-31T05:53:42.198Z`；震级 5.0–8.2。
- 行数：8,711（与计数接口一致）；列数：22。
- `type` 实测分布（未过滤）：earthquake 8656，volcanic eruption 54，nuclear explosion 1。
- 大小：1,583,882 bytes（约 1.51 MB）
- sha256：`771607a39c4adc66ef413c718727c8d8553ce1748cddb3746294cce2c8a12fa6`

### `catalogs/07_usgs_quakes_m5_2022_2023.csv`

- 用途：已有的 2022–2023 年 M≥5 目录，作为连续序列中的一段，不重新下载。
- 来源：从 `/workspace/dpw1_acquired/07_usgs_quakes_m5_2022_2023.csv` 复制（该文件与 `/workspace/07_fine_clean/acquired/07_usgs_quakes_m5_2022_2023.csv` 内容一致，sha256 相同）。复制后三者哈希仍一致，源文件未被修改。
- 检索时间：复制于 2026-11-15 12:31–12:34 CST（UTC+8）。源文件本身为更早获取的 ComCat 导出，未在本次向 USGS 重新请求。
- 覆盖：时间 `2022-01-01T08:08:09.823Z`–`2023-12-30T17:16:23.833Z`；震级 5.0–7.8。
- 行数：3,503；列数：22。
- `type` 实测分布：earthquake 3502，volcanic eruption 1。
- 大小：678,601 bytes（约 662.70 KB）
- sha256：`2bbb2c6bd07817bdc8343db5089f9d6b26e1629f68e7a9b9a365c0626ff9b57f`

### `catalogs/07_usgs_quakes_m5_2024_now.csv`

- 用途：把目录从 2024 年补到本次抓取时刻。
- 查询：`minmagnitude=5`，`starttime=2024-01-01`，`endtime=2026-11-15T04:34:24`（UTC，即检索脚本启动时刻）。计数接口返回 5416，一次拉取。
- 检索时间：2026-11-15 12:34:24 CST（UTC+8）及之后数分钟内。
- 覆盖：时间 `2024-01-01T07:06:05.477Z`–`2026-11-14T09:26:13.073Z`；震级 5.0–8.8。窗口终点之后至抓取时刻之间，没有更新的 M≥5 事件进入本次结果。
- 行数：5,416（与计数接口一致）；列数：22。
- `type` 实测分布：earthquake 5414，landslide 2。
- 大小：1,022,495 bytes（约 998.53 KB）
- sha256：`39ebd7e5c9ec13275ec60f2d02f07ad703aadf29c5eaf63e8b2898946c250d8c`

### `catalogs/07_usgs_quakes_m55_1965_2016.csv`

- 用途：与本地 ProjectData 同期、震级下限相近（本地约 5.5–9.1）的 USGS 对照目录。
- 查询：`minmagnitude=5.5`，整体窗口 `starttime=1965-01-01`，`endtime=2017-01-01`。计数接口返回 24,692，超过 20,000 上限，故按年拆成 52 次请求（每年 `starttime=YYYY-01-01`，`endtime=(YYYY+1)-01-01`），再拼接。
- 检索时间：2026-11-15 12:34 起，CST（UTC+8）。
- 覆盖：时间 `1965-01-01T21:38:31.360Z`–`2016-12-29T22:30:19.300Z`；震级 5.5–9.1。
- 行数：24,692（与整体计数一致）；列数：22。无完全重复行，无重复 `id`。
- `type` 实测分布：earthquake 24444，nuclear explosion 241，explosion 7。
- 大小：4,092,810 bytes（约 3.90 MB）
- sha256：`d858339482597c23db349ff17cf036ee6a3de552145f02ef3ab4735a241eefde`

---

## 2. 灾害影响（`impact/`）

来源机构：NOAA National Centers for Environmental Information (NCEI) / World Data Service for Geophysics，HazEL（Hazardous Event Lookup）服务。

任务书中的短路径 `https://www.ngdc.noaa.gov/hazel/api/v1/earthquakes` 与 `/hazel/api/v1/tsunamis/events` 在本次检索中返回 HTTP 404。当前官方可用接口为：

- 基址：`https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1`
- 显著地震：`https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes`
- 海啸事件：`https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events`
- 海啸 runup / deposits / marigrams：同上基址下的 `/tsunamis/runups`、`/tsunamis/deposits`、`/tsunamis/marigrams`

分页参数：`page`（从 1 起）、`itemsPerPage=200`（接口上限）。逐页取完，直到累计条数等于响应中的 `totalItems`。产品页未提供可替代的完整官方批量 CSV；因此以该 API 为准，将 JSON `items` 转为 CSV，保留全部字段与全部记录，嵌套值（如有）写成 JSON 字符串。未使用 HTML 表格抓取。

产品页：

- 地震：https://www.ncei.noaa.gov/products/natural-hazards/tsunamis-earthquakes-volcanoes/earthquakes
- 海啸：https://www.ncei.noaa.gov/products/natural-hazards/tsunamis-earthquakes-volcanoes/tsunamis
- 检索界面：https://www.ngdc.noaa.gov/hazel/view/hazards/earthquake/search 与 https://www.ngdc.noaa.gov/hazel/view/hazards/tsunami/event-search

许可 / 使用条款：美国联邦政府公开数据，免费、无注册、通常视为公有领域。引用请使用下述 DOI。NCEI 声明不对数据中的错漏承担责任。

检索时间：2026-11-15 约 12:37–12:39 CST（UTC+8）。

### `impact/ncei_significant_earthquakes.csv`

- 数据集：NCEI/WDS Global Significant Earthquake Database（显著地震，含伤亡、损失、震级与是否伴生海啸等）。
- DOI：https://doi.org/10.7289/V5TD9V7K
- 精确请求：`GET https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes?page={1..34}&itemsPerPage=200`
- 用途：灾害影响层，补充目录中没有的死亡、受伤、经济损失等信息。
- 行数：6,698（与 `totalItems=6698` 一致）；列数：49。
- 时间覆盖：`year` 字段 -2150 至 2026（无缺失）。这是历史显著事件库，不是完整的仪器目录。
- 大小：1,005,460 bytes（约 981.89 KB）
- sha256：`4a6ea2b5e6b5ba4f65c001caa349d06e663cfd6c5efa0ff36ca881bb6f83c5df`

### `impact/ncei_significant_tsunamis.csv`

- 数据集：NCEI/WDS Global Historical Tsunami Database — 事件表（源事件）。
- DOI：https://doi.org/10.7289/V5PN93H7
- 精确请求：`GET https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events?page={1..16}&itemsPerPage=200`
- 用途：海啸事件及与地震的关联、最大波高、伤亡与损失。
- 行数：3,140（与 `totalItems=3140` 一致）；列数：52。
- 时间覆盖：`year` 字段 -2000 至 2026（无缺失）。
- 大小：441,032 bytes（约 430.70 KB）
- sha256：`62f02bc7ddf1d943bd84cd53f63436e0b7001524d8186e07cc9ea6398adc62d3`

### `impact/ncei_tsunami_runups.csv`（同一官方海啸库的配套表，一并收齐）

- 数据集：同上 DOI，runup（沿岸观测）表。
- 精确请求：`GET .../tsunamis/runups?page={1..176}&itemsPerPage=200`
- 行数：35,141（与 `totalItems=35141` 一致）；列数：52。
- 时间覆盖：`year` 字段 -2000 至 2026（无缺失）。
- 大小：6,294,554 bytes（约 6.00 MB）
- sha256：`4ba3edc9eefb343cb64b1e3423a959bfffd13b8133e5923a52a49a6a8a8b6f3c`

### `impact/ncei_tsunami_deposits.csv`（官方海啸库配套表）

- 数据集：同上 DOI，地质沉积记录。
- 精确请求：`GET .../tsunamis/deposits?page={1..7}&itemsPerPage=200`
- 行数：1,400（与 `totalItems=1400` 一致）；列数：19。
- 时间覆盖：表中 `year` 字段为 1845–2026（1,400 行均有值），从样例看更接近文献发表年，而非事件年。`yearBegin` 有值 630 行，范围为 -9000 至 7000；`yearEnd` 有值 665 行，范围为 -3500 至 2020。另有 `ageDescription`、`geologicAgeId` 描述地质年代。
- 大小：327,829 bytes（约 320.15 KB）
- sha256：`e0c5efbb204f6fa29f18f022f450c45c5c8cbbda1c47c66396d5d46dfe0d07e3`

### `impact/ncei_tsunami_marigrams.csv`（官方海啸库配套表）

- 数据集：同上 DOI，潮位仪/海啸仪记录索引。
- 精确请求：`GET .../tsunamis/marigrams?page={1..18}&itemsPerPage=200`
- 行数：3,483（与 `totalItems=3483` 一致）；列数：23。
- 时间覆盖：`year` 字段 1854–1994（无缺失）。
- 大小：747,299 bytes（约 729.78 KB）
- sha256：`880827eac64b44236947361b19a117f3a8763265a246163e9f03e7cb7c806ed8`

---

## 3. 构造与震源机制背景（`context/`）

### 3.1 Bird (2003) PB2002 板块边界 — `context/tectonicplates/`

- 数据集：Peter Bird, 2003, “An updated digital model of plate boundaries”, *Geochemistry, Geophysics, Geosystems* 4(3), 1027, doi:10.1029/2001GC000252。
- 采用的公开发行版：https://github.com/fraxen/tectonicplates （Hugo Ahlenius / Nordpil 将 Peter Bird 原数据转为 shapefile 与 GeoJSON）。原数据来源说明见该仓库 README：http://peterbird.name/oldFTP/PB2002/（2014 年 6 月取得，副本在 `original/`）。
- 为何用这一发行版：这是广泛使用、带许可与引用说明的 PB2002 数字化发行；本次未发现更新、更完整的 USGS 或 GEM「官方替代全集」。GEM 活动断层库本身也把 PB2002 列为板块边界构成数据之一，但完整的板块多边形/边界线仍以 Bird 2003 这份为准。
- 下载：`https://github.com/fraxen/tectonicplates/archive/refs/heads/master.zip`，并解压到本目录。GitHub `master` 提交 `339b0c56563c118307b1f4542703047f5f698fae`（2014-10-06T08:19:01Z，即 2014-10-06 16:19:01 CST）。
- 许可：Open Data Commons Attribution License (ODC-By) 1.0，见 `LICENSE.md` 与 http://opendatacommons.org/licenses/by/1.0/ 。请同时注明 Hugo Ahlenius、Nordpil 与 Peter Bird。
- 检索时间：2026-11-15 12:39:55 CST（UTC+8）。
- 用途：全球板块边界与板块多边形，供后续地图与构造背景使用。
- 主要图层（GeoJSON 要素数与对应 shapefile 记录数一致）：
  - `GeoJSON/PB2002_boundaries.json`：241 条 LineString，226,378 bytes，sha256 `42b3e0876a7e40f133e958ba7ab85f8851b5c693a046fbc3b138e7751863d92a`
  - `GeoJSON/PB2002_plates.json`：54 个要素（Polygon 52，MultiPolygon 2），327,718 bytes，sha256 `922918f970baf7e645821a4a728b945dbb5eeac1337d71d087fba021bcc79e21`
  - `GeoJSON/PB2002_orogens.json`：13 个要素（Polygon 12，MultiPolygon 1），33,209 bytes，sha256 `d808c74e3f9f22aae37b8670d05e03990d94aa8a06c82485069d3d3a56767c3a`
  - `GeoJSON/PB2002_steps.json`：5,824 条 LineString，10,371,475 bytes，sha256 `528fdeb1d57eb3d4c6e730951eabc6fd7da9dbc5fc7038b9f19100c52b986c9a`
  - shapefile 主文件记录数：`PB2002_boundaries.shp` 241，`PB2002_plates.shp` 54，`PB2002_orogens.shp` 13，`PB2002_steps.shp` 5,824（均带齐 .dbf/.prj/.shx 等附属文件）。
- 完整仓库压缩包 `tectonicplates-master.zip`：7,596,103 bytes（约 7.24 MB），sha256 `cd2c77c8de7ef338c205227043ddef111edcdae833b0c903605c46fd10ecd6c8`
- 附属文件（许可、说明、原始 dig/dat、示例图等）的字节数与 sha256 见文末总表。

### 3.2 GEM Global Active Faults — `context/gem_global_active_faults/`

- 数据集：GEM Global Active Faults Database (GEM GAF-DB)。官方仓库：https://github.com/GEMScienceTools/gem-global-active-faults
- 引用：Styron, Richard, and Marco Pagani. “The GEM Global Active Faults Database.” *Earthquake Spectra* 36, no. 1_suppl (2020): 160–180. doi:10.1177/8755293020944182。仓库 README 另提供 Zenodo DOI 徽章。
- 下载自 `master` 的规范路径（仓库说明 GeoJSON 为 version of record），提交 `56816508ad92fd6846dad1163b1c8c01376a2cd1`（2021-06-24T16:52:24Z，即 2021-06-25 00:52:24 CST）。未使用 fork。2019.0 / 0.9 发行版早于该提交，故采用当前 canonical 路径而非旧 release。
- 精确 URL：
  - `https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/geojson/gem_active_faults.geojson`
  - `https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/geojson/gem_active_faults_harmonized.geojson`
  - `https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/LICENSE.txt`
  - `https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/README.md`
- 许可：Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)，全文在 `LICENSE.txt`。
- 检索时间：2026-11-15 12:39:58–12:40:01 CST（UTC+8）。
- 用途：全球活动断层迹线及滑动速率等属性，供构造背景与地图使用。

#### `gem_active_faults.geojson`

- 要素数：16,195（GeoJSON FeatureCollection）。
- 大小：12,302,802 bytes（约 11.73 MB）
- sha256：`603513086b4693de6008e3444959995c34683b30dac291856340522a76d8505e`

#### `gem_active_faults_harmonized.geojson`

- 要素数：13,696。
- 大小：10,622,730 bytes（约 10.13 MB）
- sha256：`37babb516edfac22b5ae91744495d8546b3ae4676b4d4f68cc77da8222df20e1`

### 3.3 Global CMT 矩张量 — `context/gcmt/`

- 来源机构：Global Centroid-Moment-Tensor (CMT) Project，Lamont-Doherty Earth Observatory, Columbia University（Göran Ekström, Meredith Nettles）。
- 文件清单页（2026-08-01 更新）：https://www.globalcmt.org/CMTfiles.html
- 目录镜像：https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/  
  该目录本身列出为 403（禁止目录浏览），但清单页给出的具体文件均可直接下载。
- 官方格式为 ASCII NDK，**没有**提供官方完整 CSV/TSV。因此保存原始 NDK，仅将官方历史文件与后续官方月文件按字节顺序拼接为 `gcmt_1976_latest.ndk`，未做有损转换。NDK 格式说明：https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/allorder.ndk_explained（已保存）。事件数按每 5 行一条记录计算，各官方文件行数均可被 5 整除。
- 许可 / 使用条款：由美国国家科学基金会（NSF）资助的研究目录，网站提供免费下载，未见 Creative Commons 之类的正式许可证文本。项目要求在发表中引用目录，见 https://www.globalcmt.org/CMTcite.html（已保存为 `CMTcite.html`）。一般使用请同时引用：
  - Dziewonski, A. M., T.-A. Chou and J. H. Woodhouse, *J. Geophys. Res.*, 86, 2825–2852, 1981. doi:10.1029/JB086iB04p02825
  - Ekström, G., M. Nettles, and A. M. Dziewonski, *Phys. Earth Planet. Inter.*, 200–201, 1–9, 2012. doi:10.1016/j.pepi.2012.04.002
- 检索时间：2026-11-15 12:40:01–12:40:22 CST（UTC+8）。
- 用途：震源机制 / 矩张量，补充目前偏少的物理特征。
- 覆盖范围说明：官方「全部事件 1976–2025」文件覆盖至 2025 年 12 月；`NEW_MONTHLY/2026/` 在抓取日列出的完整月文件为 2026 年 1–6 月。2026 年 7 月及以后的正式月文件尚未发布。Quick CMT（`qcmt.ndk`）为初步解，已单独保存，**未**并入 `gcmt_1976_latest.ndk`。

| 文件 | 来源 URL | 事件数（行数） | 大小（bytes） | sha256 |
| --- | --- | ---: | ---: | --- |
| `jan76_dec25.ndk` | `https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/jan76_dec25.ndk` | 70,044（350,220 行） | 28,367,820 | `aae7913b5fe429e19eef0b0db81f1b5c73052b1c676df350e879322f1fa685f5` |
| `monthly_2026/jan26.ndk` | `.../NEW_MONTHLY/2026/jan26.ndk` | 232（1,160） | 93,960 | `68f98835816df2c7400d8dc8a38ec2ed6b5e8a6e5d6b6b2ddfcfbe30bef736f4` |
| `monthly_2026/feb26.ndk` | `.../NEW_MONTHLY/2026/feb26.ndk` | 173（865） | 70,065 | `4e1b1576df46d66aa709a08d4b5c10852cb24946a89eb9b2799e5c0b16a7be7f` |
| `monthly_2026/mar26.ndk` | `.../NEW_MONTHLY/2026/mar26.ndk` | 224（1,120） | 90,720 | `0e72bb8d0906ef05202d399998866f47dc0d3b04fc753733a12ff12525dbd8a1` |
| `monthly_2026/apr26.ndk` | `.../NEW_MONTHLY/2026/apr26.ndk` | 208（1,040） | 84,240 | `b3791d11b81b8c7db9ba7a2f02251e29e82f356d691ed238998e49524732d673` |
| `monthly_2026/may26.ndk` | `.../NEW_MONTHLY/2026/may26.ndk` | 200（1,000） | 81,000 | `08adb965a253f2614222c56de895930403e244724099a82fe41c84218930a06f` |
| `monthly_2026/jun26.ndk` | `.../NEW_MONTHLY/2026/jun26.ndk` | 198（990） | 80,190 | `a521f67c5519c43f5ce9302cb201504255fa6c7952c992b209a47c0302d27b46` |
| `gcmt_1976_latest.ndk` | 由上列官方文件按此顺序拼接 | 71,279（356,395 行，与各文件事件数之和一致） | 28,867,995 | `42d9446826311dfcba389349f099b70073db7f8b685553087e8d6dc27279a528` |
| `pre1976/deep_1962-1976.ndk` | `.../PRE1976/deep_1962-1976.ndk` | 104（520） | 42,120 | `6024a66c04405f0b1547eeb200baf83674a9720fe9f5df6f0e1464e5368c3b58` |
| `pre1976/intdep_1962-1975.ndk` | `.../PRE1976/intdep_1962-1975.ndk` | 76（380） | 30,780 | `6d6858e737df9b412959fc42d25ba5a55e0af39ccda59fc129cb1f7ba2f654e0` |
| `quick/qcmt.ndk` | `.../NEW_QUICK/qcmt.ndk` | 441（2,205） | 178,605 | `c256c5b79d37c22c810e0cfcd7852f4b3e335b867204d2402ad21a19148fdc5b` |

1962–1976 的深源 / 中源补充解与 Quick CMT 均按官方清单另行保存，不并入 `gcmt_1976_latest.ndk`。

---

## 未获取或未完全覆盖的内容

1. **Global CMT 正式月目录目前只到 2026 年 6 月。** 抓取日（2026-11-15）`NEW_MONTHLY/2026/` 仅列出 jan–jun。7–11 月的正式解尚未作为完整月文件发布。已另外保存初步 Quick CMT（441 条），但未并入完整目录。
2. **没有官方 GCMT CSV。** 只保存官方 NDK（及一份无转换的拼接文件）。
3. **HazEL 短路径 404。** 已改用当前官方 ` /hazel/hazard-service/api/v1/ `，目录已完整分页下载。
4. **2022–2023 USGS 目录有意不重下。** 使用本地已获取副本，sha256 见上。
5. 本次没有失败的必收图层；未使用需注册或付费的来源（例如 EM-DAT），也未使用浏览器。

---

## 全部文件字节数与 sha256

（写本说明之前对目录内已有文件实测；本文件 `SOURCES.md` 本身不列入下表。）

```
   4092810  d858339482597c23db349ff17cf036ee6a3de552145f02ef3ab4735a241eefde  catalogs/07_usgs_quakes_m55_1965_2016.csv
   1583882  771607a39c4adc66ef413c718727c8d8553ce1748cddb3746294cce2c8a12fa6  catalogs/07_usgs_quakes_m5_2017_2021.csv
    678601  2bbb2c6bd07817bdc8343db5089f9d6b26e1629f68e7a9b9a365c0626ff9b57f  catalogs/07_usgs_quakes_m5_2022_2023.csv
   1022495  39ebd7e5c9ec13275ec60f2d02f07ad703aadf29c5eaf63e8b2898946c250d8c  catalogs/07_usgs_quakes_m5_2024_now.csv
      3561  a579ed6c0b0c40ae8f84de18b5bfca7180eb487374e5090d28c40bbe7555400b  context/gcmt/CMTcite.html
      3442  1e074c1f974efa5c116bef360b2f1dc955ca69313d1fd0b0cc32f8254434ad4b  context/gcmt/CMTfiles.html
       246  39aadaf71dc48457e85a18f805fdc9305dd72ca323ec93984702432898b004e2  context/gcmt/NEW_MONTHLY_2026_index.html
      7015  23ec975445d67b81b2cbe129bb504c90f3ebd41c66ce1789851b6378f614211d  context/gcmt/allorder.ndk_explained
  28867995  42d9446826311dfcba389349f099b70073db7f8b685553087e8d6dc27279a528  context/gcmt/gcmt_1976_latest.ndk
  28367820  aae7913b5fe429e19eef0b0db81f1b5c73052b1c676df350e879322f1fa685f5  context/gcmt/jan76_dec25.ndk
     84240  b3791d11b81b8c7db9ba7a2f02251e29e82f356d691ed238998e49524732d673  context/gcmt/monthly_2026/apr26.ndk
     70065  4e1b1576df46d66aa709a08d4b5c10852cb24946a89eb9b2799e5c0b16a7be7f  context/gcmt/monthly_2026/feb26.ndk
     93960  68f98835816df2c7400d8dc8a38ec2ed6b5e8a6e5d6b6b2ddfcfbe30bef736f4  context/gcmt/monthly_2026/jan26.ndk
     80190  a521f67c5519c43f5ce9302cb201504255fa6c7952c992b209a47c0302d27b46  context/gcmt/monthly_2026/jun26.ndk
     90720  0e72bb8d0906ef05202d399998866f47dc0d3b04fc753733a12ff12525dbd8a1  context/gcmt/monthly_2026/mar26.ndk
     81000  08adb965a253f2614222c56de895930403e244724099a82fe41c84218930a06f  context/gcmt/monthly_2026/may26.ndk
     42120  6024a66c04405f0b1547eeb200baf83674a9720fe9f5df6f0e1464e5368c3b58  context/gcmt/pre1976/deep_1962-1976.ndk
     30780  6d6858e737df9b412959fc42d25ba5a55e0af39ccda59fc129cb1f7ba2f654e0  context/gcmt/pre1976/intdep_1962-1975.ndk
    178605  c256c5b79d37c22c810e0cfcd7852f4b3e335b867204d2402ad21a19148fdc5b  context/gcmt/quick/qcmt.ndk
     20139  2baa3b754cbd61f19a14c354a38e6521d306412367195a4bb0cad030ca16d9bd  context/gem_global_active_faults/LICENSE.txt
     14372  ab91b3a8e90e6c4eb00ecbbf653790dc5528565c99eaf2c5fbb05eac39c237a9  context/gem_global_active_faults/README.md
  12302802  603513086b4693de6008e3444959995c34683b30dac291856340522a76d8505e  context/gem_global_active_faults/gem_active_faults.geojson
  10622730  37babb516edfac22b5ae91744495d8546b3ae4676b4d4f68cc77da8222df20e1  context/gem_global_active_faults/gem_active_faults_harmonized.geojson
        13  957b830dd5e26bd3a579928362c198165da2e60ffa31879b70aa66ca793a367f  context/tectonicplates/.gitignore
    226378  42b3e0876a7e40f133e958ba7ab85f8851b5c693a046fbc3b138e7751863d92a  context/tectonicplates/GeoJSON/PB2002_boundaries.json
     33209  d808c74e3f9f22aae37b8670d05e03990d94aa8a06c82485069d3d3a56767c3a  context/tectonicplates/GeoJSON/PB2002_orogens.json
    327718  922918f970baf7e645821a4a728b945dbb5eeac1337d71d087fba021bcc79e21  context/tectonicplates/GeoJSON/PB2002_plates.json
  10371475  528fdeb1d57eb3d4c6e730951eabc6fd7da9dbc5fc7038b9f19100c52b986c9a  context/tectonicplates/GeoJSON/PB2002_steps.json
       186  aca5f9e92e61843413b9297659af2eef552eb38fef39eae2f701566d985de36c  context/tectonicplates/LICENSE.md
     53969  f50a8ccca3231479b60311048e45d72bfbd12f73ed928f95db63a417eaaa835c  context/tectonicplates/PB2002_boundaries.dbf
       145  a02a27b1d1982c8516d83398e85a3c8b1aef1713c13ef4d84d7bde17430c07c4  context/tectonicplates/PB2002_boundaries.prj
      2476  f2f80059a09bb74256b6e34c067105673d2f8691ceaf851fdb142de8f3d758a6  context/tectonicplates/PB2002_boundaries.sbn
       300  b4c542709e884b992f7233933a84a2ffcfb767f94027cba5b8587ce1eb9da2da  context/tectonicplates/PB2002_boundaries.sbx
    114268  798798ed9054aa749f4d46c97d31115c12fb57e830df44e49a09fab7c06bc010  context/tectonicplates/PB2002_boundaries.shp
     19872  7a868226a61753aeb2933e84df2b8364c3f160c3aeec11a8eba1dbc87c19ae68  context/tectonicplates/PB2002_boundaries.shp.xml
      2028  4f3016a3de8d6f7d1d717acb4715d7a77874931d09759602793b3dd8e3eb5ef0  context/tectonicplates/PB2002_boundaries.shx
         5  3ad3031f5503a4404af825262ee8232cc04d4ea6683d42c5dd0a2f2a27ac9824  context/tectonicplates/PB2002_orogens.cpg
      1209  6ec171f4263ba3549717a83fabe57cb927e249de635b854c4a5fdc3a754f80cc  context/tectonicplates/PB2002_orogens.dbf
       145  a02a27b1d1982c8516d83398e85a3c8b1aef1713c13ef4d84d7bde17430c07c4  context/tectonicplates/PB2002_orogens.prj
       260  0f27ae878b3b46bd5579ed557634cc8534762f844778c93400664c0e3b543491  context/tectonicplates/PB2002_orogens.sbn
       132  2c9a54617df81fe6aea955de51aae620ffd745ae91041bab554c30bc857aae63  context/tectonicplates/PB2002_orogens.sbx
     19024  ddb12c5f0ee598cd2c6b9ece70935cb9e388beec74bcb6d1c1519e10c0fa76b7  context/tectonicplates/PB2002_orogens.shp
     14285  8b7a7655b01561364af2c0b226394a0143cdcff2539590c4b02fe45b85d2054d  context/tectonicplates/PB2002_orogens.shp.xml
       204  613178100ab10f0bc4179aa5dff76c02b5a5ef65e67ee94407446c2e42e2fda7  context/tectonicplates/PB2002_orogens.shx
      8662  3ab2b9b039b058d54537dc135b15d42b3e3919ae875197e1f01f013fbd52b2c2  context/tectonicplates/PB2002_plates.dbf
       143  98aaf3d1c0ecadf1a424a4536de261c3daf4e373697cb86c40c43b989daf52eb  context/tectonicplates/PB2002_plates.prj
       652  49dd27a6d19bde93fe8d42ca010d025a1a271bd57d6a9a68200643b82c14f3e8  context/tectonicplates/PB2002_plates.sbn
       164  5f857d1e9479e724e2467f284e1bd5a0247d1683f29b0f9b26ba85a0e572bbb6  context/tectonicplates/PB2002_plates.sbx
    190944  fdb627d097641a181a42337a5da950ea2e060d00fd69fcd51de2e54bfefa3478  context/tectonicplates/PB2002_plates.shp
     17119  f0b11c31c4020503b990bbc351d33087e5ba92e635e142e81942aed036ab9282  context/tectonicplates/PB2002_plates.shp.xml
       532  7861d2ff5c5754fbfc2f35c057f7d0153275a56c45664528cf1447362f28bd54  context/tectonicplates/PB2002_plates.shx
     22528  cef8d75f27eb70fbeedca19128ce80eaba6cc7a08d3ee72068c8a9b045e08821  context/tectonicplates/PB2002_poles.xls
         5  3ad3031f5503a4404af825262ee8232cc04d4ea6683d42c5dd0a2f2a27ac9824  context/tectonicplates/PB2002_steps.cpg
   8602658  8e0cf4d36396163bf11d1136bca3b8201bf94ac84997003fbcd100dc6082d1cd  context/tectonicplates/PB2002_steps.dbf
       145  a02a27b1d1982c8516d83398e85a3c8b1aef1713c13ef4d84d7bde17430c07c4  context/tectonicplates/PB2002_steps.prj
     58044  445d52bbca45e087011aebebbf4bca2773ebd5a28dbdd5209da3846e9e2fd6e4  context/tectonicplates/PB2002_steps.sbn
      3268  e5d6d38024b0016ee9f1cb3017182db0a8b683718b9d154eccb3ba93ec58ebba  context/tectonicplates/PB2002_steps.sbx
   4632692  28d5254791b28069d72a0f08f6fde743209ad79992ede1a6baf40e6c23839243  context/tectonicplates/PB2002_steps.shp
     25943  f20fed59e6c8ede1cb76d042b9c0a3b200ed90241417e4719dbd42ba7fca01c5  context/tectonicplates/PB2002_steps.shp.xml
     46692  134aea560a6fa840d1e899b291e2e1564d2f112aa5e0044e02e180e4a01e245b  context/tectonicplates/PB2002_steps.shx
      2871  ed650bfd4ffde9cd09afe7981bdd5ea266d89529f78138a02d8d6e341e50c438  context/tectonicplates/README.md
     38338  338d03c9ca94599bbd1b7045fcce7331b4a71183823c3d9e40e918e47f497c7c  context/tectonicplates/example_plates.png
    181502  d75631c5c85a1ccf42ba4714902d9bee973069e162403e3467b5855fb9b3efba  context/tectonicplates/original/PB2002_boundaries.dig.txt
     31662  daf4e6ff6c5e6983d70df8977bc989f814b79dd4efda28c24433db012f2e77c6  context/tectonicplates/original/PB2002_orogens.dig.txt
    329608  ff7e25dbf29658d4330b38e95e876533c5cdfd292ef71fa806e2340edfa3abc0  context/tectonicplates/original/PB2002_plates.dig.txt
      2802  887d208bda44cea75ee0c778c1883476906757a3d8035608a6cff7b79cf40f2e  context/tectonicplates/original/PB2002_poles.dat.txt
    558825  840dd47195723826ad5c918925edf66734e5227d776a6f027bcb02d28cb5865a  context/tectonicplates/original/PB2002_steps.csv
    564443  513babb111c65cd275274e2edcb249085d00e007c79d8755e1b4b79f60806f37  context/tectonicplates/original/PB2002_steps.dat.txt
      1528  ac769f83c60e8bfa0696c8da89658314d45634cd10de141629a425853ad3259a  context/tectonicplates/original/PB2002_steps_desc.txt
      8019  d1bfa5b21ff8a53baaf2bc7c54ee1c51628ef724b82976e4448771e8d31a7b65  context/tectonicplates/original/README.md
   7596103  cd2c77c8de7ef338c205227043ddef111edcdae833b0c903605c46fd10ecd6c8  context/tectonicplates/tectonicplates-master.zip
   1005460  4a6ea2b5e6b5ba4f65c001caa349d06e663cfd6c5efa0ff36ca881bb6f83c5df  impact/ncei_significant_earthquakes.csv
    441032  62f02bc7ddf1d943bd84cd53f63436e0b7001524d8186e07cc9ea6398adc62d3  impact/ncei_significant_tsunamis.csv
    327829  e0c5efbb204f6fa29f18f022f450c45c5c8cbbda1c47c66396d5d46dfe0d07e3  impact/ncei_tsunami_deposits.csv
    747299  880827eac64b44236947361b19a117f3a8763265a246163e9f03e7cb7c806ed8  impact/ncei_tsunami_marigrams.csv
   6294554  4ba3edc9eefb343cb64b1e3423a959bfffd13b8133e5923a52a49a6a8a8b6f3c  impact/ncei_tsunami_runups.csv
     26435  feb6705f015cfc6b3d372ce82c9fbdc937ff4c57b9587e19957ba335bbb60100  retrieval_manifest.json
     34018  6a59677be40808c2ef7caf0eec14387f9ed4b83cb97f48e0340801904f1b93fc  retrieve_07_external.py
     40041  cd6e2c326c75bdfc3f53cfa51241d1a4c6f913382ac0b939fec78d0666e9b527  retrieve_log.txt
```

## 补充：国家统计局（nbs/）

2026-11-15 起，在本目录下新增 `nbs/`，从国家统计局官网收集《中国统计年鉴》「地震灾害情况」表，以及分省年末常住人口、地区生产总值；并补充「环境统计资料」中的地震灾害表。
只保存官方原始文件，不清洗，也不改动本文件以上已记录的 catalogs / impact / context 数据。
详细来源、口径、抓取参数和文件清单见 [`nbs/SOURCES.md`](nbs/SOURCES.md)。

## 补充：中国优先数据（china/）

2026-11-16 起，在本目录下新增 `china/`：中国地震台网正式目录（2009 年起）、CN-block 地块与 CN-faults 活动断层，以及官方地理数据包。国家地震台网整包目录因需登录未收入。
只保存收集到的原始文件，不清洗，也不改动本文件以上已记录的 catalogs / impact / context / nbs 数据。
详细来源、许可、抓取参数和缺口见 [`china/SOURCES.md`](china/SOURCES.md)。
