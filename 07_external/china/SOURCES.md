# 07_external/china 数据来源说明

本目录是 BNBU DS 2043 项目选项 07（地震）的**中国优先外部数据原始收集结果**，只做官方/公开仓库下载、格式原样保存，以及（在没有可免登录整包文件时）对公开查询页做必要的分页拼接（仅去掉重复表头），**未做清洗、筛选、去重数据行、时区转换、地理编码、可视化或建模**。收集过程没有修改或覆盖 `ProjectData` 原始数据、既有 `acquired` 档案，也没有改动 `/workspace/07_fine_clean/`，以及 `/workspace/07_external/catalogs/`、`/impact/`、`/context/`、`/nbs/` 下的任何既有文件。

- 检索时间：2026-11-16 12:35–13:02 CST（UTC+8，Asia/Shanghai）。GitHub 发行包于 12:35:47 CST 落盘；正式目录公开查询于 12:41:57–13:02:04 CST 分页拉取并写成 CSV。
- 用户代理：`BNBU-DS2043-earthquake-external-collection/1.0 (academic course project; educational use)`（GitHub 与 data.earthquake.cn 均使用该 UA，网站接受且未改用浏览器 UA）。
- 可复现脚本：`retrieve_china_catalogs.py`（仅用于正式目录的公开 HTML 查询分页；GitHub 发行包为直接下载）。
- 本次运行日志与机器可读清单：`retrieve_log.txt`、`retrieval_manifest.json`。
- 下列行数、时间范围、字节数与 sha256 均为落盘后实测。

## 目录树

```
07_external/china/
├── SOURCES.md
├── retrieve_china_catalogs.py
├── retrieve_log.txt
├── retrieval_manifest.json
├── china-geospatial-data-UTF8.zip          # GitHub v0.4.0 官方 UTF-8 发行包原文
├── catalogs/
│   └── 07_cenc_zhengshi_m55_2009_latest.csv
├── blocks/
│   ├── CN-block-L1.gmt
│   ├── CN-block-L1-deduced.gmt
│   └── CN-block-L2.gmt
├── faults/
│   └── CN-faults.gmt
└── github/
    ├── README.md
    ├── README-en.md
    └── Changelog.md
```

发行包中的 `CN-border-*.gmt`、`ten-dash-line.gmt`、`geo3al.gmt` **仍保留在 zip 内**，本目录未再单独解出，以免与本次「地块 + 断层」收集范围混淆。

---

## 1. 国家地震台网地震目录（优先项，未能取得整包）

来源机构：中国地震台网中心 / 国家地震科学数据中心。

- 数据集介绍页：https://data.earthquake.cn/datashare/report.shtml?PAGEID=datasourcelist&dt=40280d0453e414e40153e44861dd0002
- 页面所载：数据名称「国家地震台网地震目录」；时间范围「1970 年至今」；空间范围「国内外」；摘要「1970年1月1日以来国家地震台网测定的全球地震目录，每月更新」；共享方式「在线下载」；页面显示数据量约 155,000 条（本次打开时为 155000 条）。
- 介绍页上的「在线下载」指向：`https://data.earthquake.cn/datashare/report.shtml?PAGEID=resourcedirect&dtid=40280d0453e414e40153e44861dd0002&orgid=a370b883-f16d-4c1d-ba06-4f78a96a98bc&dataLevel=datatwo`
- 直接下载入口：`https://data.earthquake.cn/datashare/report.shtml?PAGEID=resourcedownload&dtid=40280d0453e414e40153e44861dd0002`

**受阻情况（已停止该项的整包下载，未注册、未登录、未绕过访问控制、未使用他人账号）：**

- 2026-11-16 12:37:00 CST，对 `PAGEID=resourcedownload&dtid=40280d0453e414e40153e44861dd0002` 的 GET 返回 **HTTP 302**，`Location: http://data.earthquake.cn/datashare/login.jsp`。这是登录墙。
- 同一次会话中，`PAGEID=resourcedirect` 且 `dataLevel=datatwo` 返回的是用户/订单流程页面（含 `PAGEID=userup`、`datashareajax.do?method=orderCheck`，可见文字包括「验证码已发送」），不是可保存的目录文件。`dataLevel=datatwo` 与该中心《数据服务流程》中「二级数据需注册高级用户」的分级相符。
- 未发现该「每月更新、1970 年至今」产品的免登录公开查询页。同一门户上可公开浏览的是下面第 2 节的正式目录（2009 年起），以及未收入本目录的「1970至2017年CSN地震目录」（见文末已知缺口）。

许可 / 引用（介绍页规范，原文照录用途）：

- 中文发表的成果：数据来源于中国地震台网中心 国家地震科学数据中心(http://data.earthquake.cn)。
- 英文发表的成果：The data set is provided by China Earthquake Networks Center, National Earthquake Data Center.（http://data.earthquake.cn）.
- 联系邮箱：datashare@seis.ac.cn。

本项**没有**在 `catalogs/` 下落盘任何文件。

---

## 2. 中国地震台网正式地震目录（公开查询分页拼接）

来源机构：中国地震台网中心 / 国家地震科学数据中心。

查询页：https://data.earthquake.cn/datashare/report.shtml?PAGEID=earthquake_zhengshi

页面说明：中国地震局「十五」重大工程项目「中国数字地震观测网络」于 2008 年 4 月通过国家验收；从 **2009 年 1 月 1 日** 开始实现国家地震台网和区域地震台网的统一编目，产出统一的中国地震台网地震目录。正式目录覆盖「对中国台网可监测到的所有国内外地震」。日期控件 `minDate` 为 `2009-1-1`。

页面表头将发震时间明确标为 **「发震日期（北京时间）」**。所有时间值均按官网原文保存，**未做 UTC 转换，也未改写未补零的月份**（7,324 行中有 5,533 行月份为一位数，例如 `2009-1-01 14:27:51`；日、时、分、秒均为两位）。不要把这些字符串误当作 UTC。

### 为何不用官方「数据下载」整包

查询页上的「数据下载」会调用 `textdownload()`：若浏览器没有 `username` 与 `userid` cookie，即跳转到 `login.jsp?backurl=report.shtml?PAGEID=earthquake_zhengshi`；登录后才触发 Excel 导出（`DISPLAY_TYPE=3` / `exportData`）。本次**没有**调用该导出，也没有创建账号。

公开查询本身（`DISPLAY_TYPE=1` 的 HTML 结果表）无需登录即可浏览。因此本文件是按查询条件分页抓取公开表格、去掉重复表头后拼接而成的 CSV，不是官方 Excel 原件。字段名与单元格内容均保持页面原文。

### 查询参数

共同参数（GET `https://data.earthquake.cn/datashare/report.shtml`）：

- `DISPLAY_TYPE=1`
- `PAGEID=earthquake_zhengshi`
- `minM=5.5`，`maxM=10`
- `begtime=2009-01-01`，`endtime=2026-11-16`（仅日期；站点把结束日期展开为当日 `23:59:59`，表单回显为 `2026-11-16 23:59:59`）
- `minLat=-90.0`，`maxLat=90.0`，`minLon=-180.0`，`maxLon=180.0`
- `minDepths=0`，`maxDepths=1000`
- `location=`，`locationselect=`（空，全球）

第 1 页不带分页参数，由页面返回总条数与总页数。第 2 页起附加：

- `catalog_PAGENO={页码}`
- `catalog_RECORDCOUNT={总条数}`
- `catalog_PAGECOUNT={总页数}`
- `catalog_ALLDATASETS_RECORDCOUNT=catalog__default_default_default_key__default_default_default_key={总条数};`

站点固定每页 20 条。首页声明 **共 7,324 条 / 367 页**。拼接后行数与声明一致。站点按发震时间降序排列（新到旧）；CSV 保持该官方顺序，未重排。`序号` 为这次完整查询窗口中的 1–7324，连续无缺号。拼接时只去掉各页重复表头，未丢弃任何数据行。期间第 225 页之后曾出现一次连接中断，重试后成功，未发现缺页。

检索时间：2026-11-16 12:41:57–13:02:04 CST（UTC+8）。

### `catalogs/07_cenc_zhengshi_m55_2009_latest.csv`

- 用途：与本地主样本震级下限对齐的中国台网正式目录对照样本（全球范围，M≥5.5，自 2009-01-01 起）。
- 行数：7,324（与页面 `catalog_RECORDCOUNT=7324` 一致）；列数：9。
- 官方列：`序号,发震日期（北京时间）,经度(°),纬度(°),震源深度(Km),震级类型,震级,震中位置,事件类型`。
- 时间覆盖（按官方北京时间解析）：`2009-01-01 14:27:51`–`2025-11-29 14:05:00`。文件首行（最新）为 `2025-11-29 14:05:00`，末行（最老）官方字符串为 `2009-1-01 14:27:51`。
- 震级覆盖：`震级` 列全部可解析为数值，范围 5.5–8.8。这是查询下限 `minM=5.5` 之后官网返回的结果，下载后未再按震级筛选。
- `震级类型` 实测分布（未过滤）：Ms 6003，mB 1234，mb 55，Mw 26，ML 4，Ms7 2。
- `事件类型` 实测分布：天然地震 7,324（本窗口无其他类型）。
- 深度：数值 2.0–680.0 km；另有 1 行官方深度为 `-`（序号 2030，`2020-8-19 06:23:42`，印度尼西亚，Ms 7.3），原文保留。
- 经纬度范围（全球）：经度 −180.0–180.0，纬度 −77.2–87.0。
- 64 行「震中位置」在页面上已被截断为含 `...` 的短文本，CSV 按页面显示保存，不是后处理截断。
- 查询窗口虽然到 2026-11-16，但 **2026 年无记录**；2025 年有 365 条，最晚到 2025-11-29。正式目录明显滞后于检索当日，缺 2025-11-29 之后至 2026-11-16 的事件。
- 按年条数（北京时间年份）：2009 432，2010 563，2011 694，2012 416，2013 423，2014 508，2015 445，2016 416，2017 343，2018 424，2019 404，2020 382，2021 541，2022 382，2023 321，2024 265，2025 365，2026 0。
- 大小：589,134 bytes（约 575.3 KB）
- sha256：`61820116e0375d0a721086fa1c51900f703c36857922ef6b0be97347d7696dd2`

引用方式与第 1 节相同（中国地震台网中心 国家地震科学数据中心，http://data.earthquake.cn）。

---

## 3. CN-block 与 CN-faults（GitHub 公开发行包）

来源：GMT 中文社区整理的「中国地理空间数据集」，供 Generic Mapping Tools (GMT) 使用。这是**社区矢量化 / 格式转换成果，不是中国地震局官方 GIS 导出，也不是经协议申请的 CAFD 官方矢量包**。仓库未附带 LICENSE 文件；README 写明数据由用户提供、由 GMT 中文社区维护。

- 仓库：https://github.com/gmt-china/china-geospatial-data
- 发行版页：https://github.com/gmt-china/china-geospatial-data/releases
- 采用版本：最新发行 **v0.4.0**（GitHub 发布于 2024-12-25T12:28:08Z，即 2024-12-25 20:28:08 CST；UTF-8 资源更新于 2024-12-25T12:47:48Z，即 2024-12-25 20:47:48 CST）。标签提交 `ccdac30`。
- 精确 URL：https://github.com/gmt-china/china-geospatial-data/releases/download/v0.4.0/china-geospatial-data-UTF8.zip
- 文档：https://docs.gmt-china.org/latest/dataset/CN-block/ ，https://docs.gmt-china.org/latest/dataset/CN-faults/
- 检索时间：2026-11-16 12:35:47 CST（UTC+8）。
- 完整发行包 `china-geospatial-data-UTF8.zip`：22,930,612 bytes（约 21.86 MiB），sha256 `4262a3348c32b36af06a6dcf7d86eeb339b5a5ed58564d16dd14892182b958f6`。包内另有中国国界与地质图等本次未单独解出的图层。
- 仓库 README / Changelog 副本（与 zip 内文件一致）保存在 `github/`：
  - `github/README.md`：1,817 bytes，sha256 `e936e5a07adb7ccc71f3f4310267181b9a1d6c1f16c5b8cd7db81e80458d82cf`
  - `github/README-en.md`：1,921 bytes，sha256 `cc423ddf133f0cdcb37c9d3edfe5c67e5c663ea75d437ed3ab138aaff728571f`
  - `github/Changelog.md`：503 bytes，sha256 `c382a65cb3ae6160dadfc38452fd082d1c914505e4c59a9ccc23e0c845ebad39`

### 3.1 活动地块边界 — `blocks/`

文档说明：CN-block 由社区根据王辉等（2003）文中「中国大陆及周边地区活动地块划分图」（图 1）矢量化并做格式转换，**不是**官方地块 GIS 产品。

本目录解出的文件（UTF-8，GMT 折线，段头为 `>`）：

- `blocks/CN-block-L1.gmt`：一级地块边界。8 段，501 个坐标行，509 行，8,957 bytes，sha256 `30d7fabbea95040fed596a37dfd07970c6e7699187c27ad064471db25ef5d5cd`
- `blocks/CN-block-L1-deduced.gmt`：一级地块推断边界。10 段，259 个坐标行，269 行，4,547 bytes，sha256 `2b363ded86fe6dad7511bdef7651fe814b90cea2361fa4c51c2c7c30fcb85151`
- `blocks/CN-block-L2.gmt`：二级地块边界。25 段，961 个坐标行，986 行，19,215 bytes，sha256 `189b81655411225ad3d7a1860829835ad23b843c239134529bbad9f2d8d98c33`

文档要求引用：

- 张培震, 邓起东, 张国民, 等. 中国大陆的强震活动与活动地块. 中国科学D辑, 2003, 33(z1):12-20.
- 张国民, 马宏生, 王辉, 等. 中国大陆活动地块边界带与强震活动. 地球物理学报, 2005, (03):602-610.
- 王辉, 张国民, 吴云, 等. 中国大陆活动地块变形与地震活动的关系. 中国地震, 2003, (03):243-254.

### 3.2 中国断层 — `faults/CN-faults.gmt`

文档说明（https://docs.gmt-china.org/latest/dataset/CN-faults/ ，文档页注明 2025-12-11 更新）：CN-faults **来自中国活断层数据库 2023 版（CAFDv2023）**，2024 年 7 月由中国地震局地质研究所徐锡伟研究团队发布；原始数据 DOI 为 https://doi.org/10.12031/activefault.china.400.2023.db 。社区为解决原始 shapefile 中少量空几何导致 GMT 中断的问题，删除了 3 个几何错误要素（FID 5784、6429、8424），再用 `ogr2ogr` 转为 OGR/GMT 格式。**本文件是社区转换后的 GMT 文本，不是经协议申请的 CAFD2023 官方矢量数据包**；本次也没有提交官方申请表。

v0.4.0 的修订说明是「更新中国区域断层数据 CN-faults」。

- 格式：OGR/GMT LineString。属性字段：`FZN_Ch, FZN_En, FN_Ch, FN_En, FSN_Ch, FSN_En, Fea_Ch, Fea_En, AGE, AGE_Des, RefE`。
- 实测：232,549 行；段头 `>` 10,534 条；带 `# @D` 属性的记录 8,995 条（每条 11 个字段）；其中 7,078 条有中文断层名 `FN_Ch`；坐标行 213,015。
- 大小：7,927,992 bytes（约 7.56 MB）
- sha256：`7f5871f4af76a8f3cdc9c4190956fc7c33469ed4d05bb103ff68214f51ee7ea8`

文档要求引用：

- Wu, X., Xu, X., Yu, G., Ren, J., Yang, X., Chen, G., Xu, C., Du, K., Huang, X., Yang, H., Li, K., and Hao, H.: The China Active Faults Database (CAFD) and its web system, *Earth Syst. Sci. Data*, 16, 3391–3417, https://doi.org/10.5194/essd-16-3391-2024, 2024.

---

## 4. 明确未收集的内容

- 未申请、未下载需离线申请或签署协议的官方数据：全国活动断层矢量数据、中国及其邻区活动断层数据 CAFD2023 官方包、地震活动断层探察数据中心申请表。
- 未转录或再清洗国家统计局年鉴文件，也未重下 USGS、GCMT、GEM、PB2002、NCEI。
- 未收集速报目录（`PAGEID=earthquake_subao`）。正式目录的公开查询已成功，无需改用速报。
- 未开始分析或新建分析用 notebook。

---

## 5. 已知缺口

- **1965–1969 年**：本地主样本自 1965 年起，但国家台网目录官方表述从 1970 年 1 月 1 日开始，正式目录从 2009 年 1 月 1 日开始。本目录**没有**覆盖 1965–1969 的中国官方目录。
- **1970–2008 年**：优先项「国家地震台网地震目录」整包因登录墙未能取得；正式目录从 2009 年起，因此本目录也没有 1970–2008 的中国官方目录行。
- **2025-11-29 之后至检索当日（2026-11-16）**：正式目录公开查询在该时段 M≥5.5 为「无数据」，存在约 11.5 个月的官方滞后。
- **国家地震台网地震目录（1970 年至今、每月更新）全文**：仍须注册/登录（以及可能的高级用户或订单流程）后才能从官方「在线下载」取得，本次未做。
- **1970–2017 年 CSN 目录（未收入，仅作探测记录）**：同一门户的公开查询页 https://data.earthquake.cn/datashare/report.shtml?PAGEID=earthquake_csn 无需登录即可浏览。页面写明数据自 1970-01-01 至 2017-08-31，共 163,922 个事件，**发震时刻为国际时 (GMT)**，与正式目录的北京时间不同，也与「每月更新至当下」的国家台网目录不是同一产品。本次用 `minM=5.5`、`maxM=10`、全球范围查询，页面声明 24,853 条、1,243 页。其「数据下载」同样会跳转登录页。为避免把冻结的 CSN 目录误标成优先项国家台网目录，且该查询页达一千余页，本次**没有**拼接下载。若后续需要补 1970–2017，应单独收集并明确标注为 CSN、时间为国际时。
