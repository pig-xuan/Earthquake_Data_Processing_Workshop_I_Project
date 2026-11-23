# 中国及周边三维震源交互图（独立离线 HTML）

本目录是对既有本地主样本的**独立分析输出**，不改写源数据、旧图或旧笔记本，也不上传仓库。

主成果是可在浏览器中用 `file://` 离线打开的三维图：

- `07_china_region_hypocenter_3d.html` — 独立离线 HTML（内嵌数据、Plotly 与交互脚本）
- `07_china_region_hypocenter_3d.ipynb` — 中文复现笔记本，可从项目相对路径重建 HTML
- `build_china_region_hypocenter_3d.py` — 生成器（笔记本按步骤调用）
- `hypocenter_3d_template.html`、`filter_logic.js` — 页面模板与共用筛选逻辑
- `07_china_region_hypocenter_3d_counts.json` — 本次生成的计数与投影参数
- `test_hypocenter_3d.py`、`test_filter_logic.js` — 静态/单元测试

## 打开方式

用浏览器直接打开 HTML 即可，不需要网络、地图密钥或外部字体。三维显示需要 WebGL。中文显示依赖本机字体（如 Noto Sans CJK SC、微软雅黑、苹方）。

操作要点：拖动旋转、滚轮缩放；俯视 / 侧视 / 复位只改变相机；「水平垂直 1:1」与「深度夸大 5 倍」只改变显示比例，轴标注始终是真实深度；年份、震级与浅/中/深源筛选可组合，顶部计数会更新；断层图层默认关闭。

## 数据与范围

- 地震：`07_analysis/07_earthquake_analysis_sample.csv`（本地精细清洗后的构造地震主样本，1965–2016）。按坐标选取 70–145°E、10–60°N，**不按国家代码筛选**，不混入 USGS 或中国官方目录。
- 缺失深度的事件不进入本图（本次区域样本中为 0 条；全球主样本有 3 条，均在研究区外）。疑似重复按既有约定保留（区域 6 条）。
- 板块多边形与边界：Bird (2003) PB2002。
- 海岸线与国界：Natural Earth 50m（`dpw1_report/mapdata` 或项目 `mapdata/`）。
- 中国活动地块与断层：GMT 中文社区 china-geospatial-data v0.4.0 的 GMT 边界线（一级、推断一级、二级地块只作为线，不填充为面；断层默认关闭，且只画在地表）。

PB2002 板块与中国活动地块是不同层级的构造划分，不能互相替代。

## 投影与垂直比例

水平坐标使用球面方位等距投影（Azimuthal Equidistant），地球半径 6371 km，中心 107.5°E、35°N，单位为公里。这与既有分板块立体图的 aeqd 设定一致。自投影中心出发的球面距离是准确的；离开中心越远，面积、方位和横距畸变越大。本区跨度大，不能把图上任意两点的直尺距离都当成精确大地线长。

默认水平与垂直同物理比例（1 km = 1 km）。实现上按固定坐标轴范围设置 `aspectmode=manual` 的 `aspectratio`，使其等于各轴数据跨度之比（与在相同固定范围下使用 `aspectmode=data` 等价），这样筛选或空结果时比例也不会被 Plotly 自动压缩。深度夸大 5 倍只把 z 向比例乘 5，不改 z 值；请始终阅读图顶的比例说明。

## 复现

在已安装依赖的 Python 环境中，进入本目录后运行：

```text
python build_china_region_hypocenter_3d.py
```

或打开并运行 `07_china_region_hypocenter_3d.ipynb`。路径搜索按项目相对布局进行（`07_analysis/`、`07_external/`、`mapdata/` 或 `dpw1_report/mapdata/`），也兼容常见的桌面项目目录，不只写死箱子上的绝对路径。若同名 HTML 已存在，命令行需加 `--force` 才会覆盖。

### 依赖

- Python 3.10+
- pandas、numpy、shapely（读取与几何）
- plotly（仅用于把 `plotly.min.js` 内嵌进 HTML；打开 HTML 不需要 Python）

本环境使用 `/workspace/dpw1_venv`（说明中的 `/workspace/dpw1_report/.venv` 不存在）。生成时的 plotly 版本为 7.1.0。不需要 geopandas、pyproj 或网络地图库。

单元测试：

```text
python test_hypocenter_3d.py
node test_filter_logic.js
```

测试覆盖计数、投影、数据哈希、深度分级、板块归属对照，以及 HTML 自定义部分无外部资源引用。它们**不能**代替真实浏览器里的旋转、图层、比例观感和 `file://` 网络面板检查。

## 科学限制（摘要）

- 这是展示真实震源位置与深度结构的图，不是柱高表示震级的示意图。
- 地表断层线不是地下断层面；地图线经过显示用抽稀，容差写在计数 JSON 的 `layer_stats` 中，源文件未被修改。
- 板块归属复用既有立体图算法：点在 PB2002 多边形内则归该板块，否则按经纬度平面最近归属（不是大地线距离）。
- 悬停日期来自 `Date_parsed` 的 UTC 日期部分；时间使用目录 `Time` 字段原文。源数据中 `Date_parsed` 绝大多数为 UTC 午夜，本图不把日期与时间拼成未经证实的精确发震时刻。
- 研究范围是经纬度矩形，因此会包含日本、菲律宾等周边事件，与按 `Country==CN` 得到的 358 条不是同一口径。
