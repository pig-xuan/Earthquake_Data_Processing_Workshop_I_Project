# Earthquake Data Processing Workshop I Project

BNBU DS 2043 数据处理工作坊 I（2026 秋）选题 07：全球地震数据的清洗、外部数据补充与时空分析。

本分支 `Aliwu` 由吴宇轩整理并上传，对应桌面项目文件夹中已经完成的精细清洗、外部数据收集和时空分析。`main` 上原有的练习脚本 `earthquake_cleaning.py` 和课程原始表 `data/07earthquake.csv` 全部保留，互不覆盖。

## 目录结构

```
.
├── README.md
├── earthquake_cleaning.py          # 组内原有的入门练习脚本（保留）
├── data/07earthquake.csv           # 课程提供的原始表（保留）
├── requirements.txt
├── mapdata/ne_50m_land/            # Natural Earth 50m 陆地底图，供地图复现
├── 07_fine_clean/                  # 精细清洗笔记本与清洗结果
├── 07_analysis/                    # 分析样本、对照目录、时空平面图与立体图
└── 07_external/                    # 外部数据原文（只保存、未清洗）
```

## 主数据口径

后续分析以精细清洗后的本地长序列为主，主分析只取构造地震（`is_earthquake`）。

- 本地主样本 23,232 条，时间范围 1965-01-02 至 2016-12-30，震级 5.5–9.1。
- 非构造事件 180 条只做计数，不进入主样本。
- 无效坐标不进入空间图，震级异常不进入震级统计；本样本中这两类均为 0 条。
- 负深度 3 条、疑似重复 98 条保留在主样本中，并加标记说明；深度图会排除缺失深度的记录。
- 日期只新增 `Date_parsed`（按混合格式解析为 UTC），不改原日期列。
- 中国子集按 `Country == "CN"` 登记：主样本 358 条。

USGS 只作对照和延伸，不与本地目录简单拼接：

- 1965–2016 年 M≥5.5：同期对照
- 2017 年后 M≥5：时间延伸
- 2022–2023 年已做过精细清洗；其余外部 USGS 在 `07_analysis/` 中另存标记副本，不删行

板块边界、活动断层和 Global CMT 目前只作为背景数据收齐，构造背景分析笔记本尚未开写。国家统计局灾害、人口和 GDP 表只保存官网原文，尚未转录。

## 各文件夹说明

### 07_fine_clean/

对课程原始表和 USGS 2022–2023 年目录做精细清洗：标记与派生列，不改已导出的原始值（负深度除外：加标记后在分析副本中置空）。输出在 `cleaned/`：

- `07_earthquake_fine_cleaned.csv`（本地 23,412 行）
- `07_usgs_quakes_fine_cleaned.csv`（USGS 2022–2023，3,503 行）
- `07_geocode_corrections.csv`（逆地理校正表）

课程原始表在本仓库中位于 `data/07earthquake.csv`（与桌面项目里的 `ProjectData/07earthquake.csv` 为同一份数据）。

### 07_analysis/

在精细清洗结果上做样本界定和时空格局，新开笔记本，不覆盖旧的升级图。

- [`interactive/`](07_analysis/interactive/)：中国及周边离线三维震源图。请下载 [`07_china_region_hypocenter_3d.html`](07_analysis/interactive/07_china_region_hypocenter_3d.html) 到本地后用浏览器打开；GitHub 文件页不是运行预览。Plotly 已内嵌。范围是 1965–2016、70–145°E / 10–60°N，3515 个事件；真实深度向下，水平垂直 1:1 与深度夸大 5 倍可切换。
- `07_earthquake_analysis_sample.ipynb`：样本界定与质量清点
- `07_earthquake_analysis_sample.csv`：本地主样本（23,232 条）
- `07_analysis_sample_quality.csv`：清点表
- `07_usgs_*_flagged.csv`：各时段 USGS 标记副本
- `07_earthquake_analysis_spatiotemporal.ipynb`：时空平面图（年度/十年频次、全球密度与 M≥7、按深度分层）
- `figures/`：平面图；`figures/3d/`：按板块分张的紫金立体图（52 张）
- `07_st_annual_counts.csv`、`07_st_decade_counts.csv`、`07_st_3d_plate_counts.csv`：配套计数表

立体图规则：每个板块单独一张，地图斜铺在底部，每场地震在震中立柱，柱高 `h = M − 5.0`；同一张图内 9.1 明显高于 5.5，不同板块之间的柱高不能直接比较。板块归属使用 `07_external/context/tectonicplates/` 中的 PB2002 多边形，点在多边形内则归该板块，落在边界上则就近归属。本样本 23,232 条全部归属，未归属 0 条。

### 07_external/

按三层收集的公开数据，只保存原文，不做清洗。来源、许可、抓取参数和缺口记在 `07_external/SOURCES.md` 和 `07_external/nbs/SOURCES.md`。

- `catalogs/`：USGS 目录（1965–2016 年 M≥5.5 同期对照，2017–2021、2022–2023、2024 至抓取日的 M≥5）
- `impact/`：NOAA NCEI 显著地震与海啸目录
- `context/`：板块边界（PB2002）、GEM 全球活动断层、Global CMT 震源机制
- `nbs/`：国家统计局年鉴「地震灾害情况」、分省人口和地区生产总值，以及环境统计资料中的地震灾害表。尚未转录成分析表。
- `china/`：中国优先补充，位于 `07_external/china/`。含中国地震台网正式目录（2009 年起）、CN-block 地块与 CN-faults 活动断层；国家地震台网整包目录因需登录未收入。说明见 `07_external/china/SOURCES.md`。

### mapdata/

复现地图所需的 Natural Earth 50m 陆地底图。笔记本里也预留了桌面路径回退。

## 运行说明

建议使用 Python 3.11 或更新版本。组内原有练习：

```bash
python -m pip install -r requirements.txt
python earthquake_cleaning.py
```

组内原有练习脚本 `earthquake_cleaning.py` 的 19 步说明，是队友当时写在根 README 里的原文，现原样保存在 [`docs/earthquake_cleaning_19_steps.md`](docs/earthquake_cleaning_19_steps.md)。那份文档只描述该清洗脚本当时的范围；其中列出的未做事项不等于整个项目的当前进度。

精细清洗与分析笔记本在 `07_fine_clean/` 和 `07_analysis/` 中，需额外安装 `geopandas`、`matplotlib`、`seaborn`、`pyproj`。地图基于 Natural Earth 50m，立体图使用 matplotlib 的三维坐标。读取 `Date_parsed` 时请使用：

```python
pd.to_datetime(..., format="ISO8601", utc=True)
```

布尔标记从 CSV 读入后可能变成字符串，使用前需再转成布尔值。

## 当前进度与未做事项

已完成：精细清洗、外部数据与统计局原文收集、分析样本界定、时空平面图、分板块立体图。

尚未开始（需先确认技术细节再写）：

- 构造背景分析（板块边界、断层、CMT 与板缘/板内差异）
- 本地目录与 USGS 的对照分析
- 国家统计局表转录，以及中国分省活动与灾情、人口、GDP 暴露的深挖
- 机器学习

## 数据来源

- 本地长序列：课程提供的 `ProjectData/07earthquake.csv`，本仓库副本为 `data/07earthquake.csv`
- USGS、NCEI、GEM、Global CMT、板块边界与国家统计局数据的出处和许可见 `07_external/SOURCES.md` 与 `07_external/nbs/SOURCES.md`
