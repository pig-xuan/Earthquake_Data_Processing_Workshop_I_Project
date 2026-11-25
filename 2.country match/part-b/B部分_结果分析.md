# B部分结果分析与方法说明

## 数据口径

本部分研究中国省份分布，并分别制作全球和中国震级Top30。所有结果限定地震事件、M≥5.5。
历史目录覆盖1965—2016；第二套使用已有USGS下载数据，按UTC发生时间选取1965-01-01（含）至2025-01-01（不含）。它不包含2025、2026年发生的地震，但下载和目录修订可能发生在2024年之后，因此不是“截至2024年的目录快照”。两套数据分别处理，不直接拼接。

## 国家和省份如何确定

使用事件的Longitude与Latitude建立Shapely点，坐标顺序为经度、纬度。逐一检查Natural Earth国家多边形和geoBoundaries中国省级多边形的covers结果；covers包含多边形边界。
仅有一个候选时标记matched；没有候选标记unmatched；多个候选标记multiple_matches，并保留候选名称。保留上述原始陆地匹配字段；新增海域展示标签，不使用最近国家或最近省份强制归属。
中国子集采用唯一匹配所提供省级边界的记录，不依赖国家匹配结果。边界是静态版本，未重建每一年行政边界。原名称Guangzhou Province修正为Guangdong Province，重复的Ningxia名称也按历史代码统一。

## 统计与排名规则

省份按年份分组计数，补齐全部34个省级单元与各年份组合。零表示目录中没有符合条件且唯一匹配的事件，不能解释为当地没有任何地震。
Top30按震级降序排列，同震级按UTC发生时间、source_row升序决定展示顺序。固定展示30条，magnitude_rank保留并列名次，并报告阈值处未入选的同震级记录。不同震级类型沿用目录数值，不视为已经统一换算成同一种震级标度。

## 两套目录概览

| 目录 | 全球事件数 | 省界唯一匹配数 | 国家唯一匹配数 | 统计年份数 |
| --- | --- | --- | --- | --- |
| 历史目录（1965—2016） | 23232 | 396 | 4781 | 52 |
| USGS目录子集（1965—2024） | 28044 | 473 | 5653 | 60 |

## 历史目录（1965—2016）

共有 23,232 条地震记录。唯一匹配省界 396 条；唯一匹配国家边界 4,781 条，国家多个匹配 0 条。未匹配国家记录 18,451 条仍保留在全球事件表及全球排名中。

### 省份记录分布

| 省份（边界源名称） | 次数 |
| --- | --- |
| Xinjiang Uyghur Autonomous Region | 94 |
| Tibet Autonomous Region | 70 |
| Yunnan Province | 54 |
| Qinghai Province | 48 |
| Sichuan Province | 47 |
| Taiwan Province | 42 |

以上六个省级单元占省界唯一匹配记录的 89.6%。两套目录都显示，新疆、西藏的记录数居前，云南、四川、青海及台湾也较集中。这里的次数是震中落入所用多边形的目录次数，不代表受灾次数或未来风险。统计使用边界数据源的范围和名称。

省界匹配事件数最高的年份为 2008 年，共 32 条。某年次数集中可能包含同一地区的地震序列，不能仅凭年度次数认定为多个相互独立的大地震。

### 国家／地区累计记录

| country_ne | event_count |
| --- | --- |
| Indonesia | 527 |
| Papua New Guinea | 462 |
| Chile | 406 |
| China | 347 |
| Argentina | 233 |
| United States of America | 228 |

本表和原国家地图仍为陆地匹配口径。海上事件另按EEZ关联国家或海域名称统计，见下方新增海域分析；不能把陆地表当成完整的国家相关地震总量。

### 全球 Top 30

| Date | Magnitude | location_label | location_type |
| --- | --- | --- | --- |
| 12/26/2004 | 9.1 | Indonesia EEZ | eez_single |
| 03/11/2011 | 9.1 | Japan EEZ | eez_single |
| 02/27/2010 | 8.8 | Chile EEZ | eez_single |

固定展示30条，第30条震级为 8；阈值同震级另有 10 条未入选。日期采用月/日/年。
### 中国 Top 30

| Date | Magnitude | province |
| --- | --- | --- |
| 05/12/2008 | 7.9 | Sichuan Province |
| 11/14/2001 | 7.8 | Qinghai Province |
| 11/06/1988 | 7.7 | Yunnan Province |

固定展示30条，第30条震级为 6.7；阈值同震级另有 0 条未入选。日期采用月/日/年。

## USGS目录子集（1965—2024）

共有 28,044 条地震记录。唯一匹配省界 473 条；唯一匹配国家边界 5,653 条，国家多个匹配 0 条。未匹配国家记录 22,391 条仍保留在全球事件表及全球排名中。

### 省份记录分布

| 省份（边界源名称） | 次数 |
| --- | --- |
| Xinjiang Uyghur Autonomous Region | 109 |
| Tibet Autonomous Region | 85 |
| Yunnan Province | 62 |
| Sichuan Province | 60 |
| Qinghai Province | 58 |
| Taiwan Province | 51 |

以上六个省级单元占省界唯一匹配记录的 89.9%。两套目录都显示，新疆、西藏的记录数居前，云南、四川、青海及台湾也较集中。这里的次数是震中落入所用多边形的目录次数，不代表受灾次数或未来风险。统计使用边界数据源的范围和名称。

省界匹配事件数最高的年份为 2008 年，共 32 条。某年次数集中可能包含同一地区的地震序列，不能仅凭年度次数认定为多个相互独立的大地震。

### 国家／地区累计记录

| country_ne | event_count |
| --- | --- |
| Indonesia | 636 |
| Papua New Guinea | 570 |
| Chile | 465 |
| China | 413 |
| Peru | 280 |
| Argentina | 277 |

本表和原国家地图仍为陆地匹配口径。海上事件另按EEZ关联国家或海域名称统计，见下方新增海域分析；不能把陆地表当成完整的国家相关地震总量。

### 全球 Top 30

| Date | Magnitude | location_label | location_type |
| --- | --- | --- | --- |
| 12/26/2004 | 9.1 | Indonesia EEZ | eez_single |
| 03/11/2011 | 9.1 | Japan EEZ | eez_single |
| 02/27/2010 | 8.8 | Chile EEZ | eez_single |

固定展示30条，第30条震级为 8.1；阈值同震级另有 2 条未入选。日期采用月/日/年。
### 中国 Top 30

| Date | Magnitude | province |
| --- | --- | --- |
| 05/12/2008 | 7.9 | Sichuan Province |
| 11/14/2001 | 7.8 | Qinghai Province |
| 11/06/1988 | 7.7 | Yunnan Province |

固定展示30条，第30条震级为 6.7；阈值同震级另有 3 条未入选。日期采用月/日/年。

## 两套目录的比较与解释

两套目录的全球Top30前三条均为2004-12-26（M9.1）、2011-03-11（M9.1）、2010-02-27（M8.8）；中国子集前三条均为2008-05-12（M7.9）、2001-11-14（M7.8）、1988-11-06（M7.7）。日期和震级由当前输出表读取，事件名称没有另行推断。

全球Top30的入选阈值从M8.0变为M8.1，中国子集仍为M6.7。不能把差异全部归因于2017—2024的新事件：新目录在1965—2016这个重叠区间有 24,444 条全球记录、427 条省界匹配记录，而旧历史目录分别为23,232和396条。目录补录、修订或来源处理差异也会影响比较。尚未逐事件对齐，因此不声称已经分解这些变化的具体原因。

## 海域标签与全事件统计（更新）


海上位置按已确认的规则处理：原陆地国家唯一匹配优先；其余事件检查Marine Regions EEZ v12多边形，显示如 `Japan EEZ` 的关联国家标签；未覆盖EEZ但落入IHO Sea Areas v3多边形的事件按相应海域命名，如 `North Pacific Ocean`。重叠EEZ保留全部关联国家，作为单一组合类别计数，不重复加入各国总数。

`country_ne`及`country_match_status`保留原陆地匹配结果，以便审计；图表使用新的`location_label`。`eez_countries`、`eez_territories`、`eez_mrgids`、`sea_area`与`sea_mrgids`记录来源。若陆地50m、EEZ及海域均未覆盖，再用用户已提供的Natural Earth 5.1.2数据库中的10m国家多边形复核小岛与沿岸点，成功者标记`land_refined_10m`，不修改原始陆地匹配字段。EEZ关联不等于领土主权；海域名称也不说明是否处于公海。边界采用静态源版本，未重建每个历史年份的海域划分。

全球Top30仍在全部事件中按震级排序，新增位置标签不改变入选事件。中国Top30及省份统计继续采用原来的唯一省界匹配子集，未将海上EEZ事件混入中国省份或中国Top30。


### 历史目录


| location_type | event_count |
| --- | --- |
| eez_single | 14899 |
| land_country | 4781 |
| sea_area | 2258 |
| eez_multiple | 1179 |
| land_refined_10m | 59 |
| boundary_review | 56 |


全事件位置类别中记录较多的前六项：


| location_type | location_label | event_count |
| --- | --- | --- |
| eez_single | Indonesia EEZ | 2477 |
| eez_single | Japan EEZ | 1524 |
| eez_single | United States EEZ | 1265 |
| eez_single | Tonga EEZ | 1177 |
| eez_single | Papua New Guinea EEZ | 1081 |
| eez_single | New Zealand EEZ | 922 |


全球Top30前五条的新标签：


| Date | Magnitude | location_label |
| --- | --- | --- |
| 12/26/2004 | 9.1 | Indonesia EEZ |
| 03/11/2011 | 9.1 | Japan EEZ |
| 02/27/2010 | 8.8 | Chile EEZ |
| 02/04/1965 | 8.7 | United States EEZ |
| 03/28/2005 | 8.6 | Indonesia |


无EEZ或IHO覆盖、需要边界复核的记录有 56 条；若存在，显示坐标和Boundary review，不强行指定海洋。重叠与复核记录已单独导出至 `historical_location_review.csv`。


### 1965—2024目录


| location_type | event_count |
| --- | --- |
| eez_single | 17847 |
| land_country | 5653 |
| sea_area | 2874 |
| eez_multiple | 1534 |
| boundary_review | 68 |
| land_refined_10m | 68 |


全事件位置类别中记录较多的前六项：


| location_type | location_label | event_count |
| --- | --- | --- |
| eez_single | Indonesia EEZ | 2900 |
| eez_single | Japan EEZ | 1833 |
| eez_single | United States EEZ | 1551 |
| eez_single | Tonga EEZ | 1421 |
| eez_single | Papua New Guinea EEZ | 1250 |
| eez_single | New Zealand EEZ | 1154 |


全球Top30前五条的新标签：


| Date | Magnitude | location_label |
| --- | --- | --- |
| 12/26/2004 | 9.1 | Indonesia EEZ |
| 03/11/2011 | 9.1 | Japan EEZ |
| 02/27/2010 | 8.8 | Chile EEZ |
| 02/04/1965 | 8.7 | United States EEZ |
| 03/28/2005 | 8.6 | Indonesia |


无EEZ或IHO覆盖、需要边界复核的记录有 68 条；若存在，显示坐标和Boundary review，不强行指定海洋。重叠与复核记录已单独导出至 `catalog_1965_2024_location_review.csv`。


### 边界来源和复现

- [Marine Regions官方数据下载页](https://www.marineregions.org/downloads.php)：EEZ v12与IHO Sea Areas v3。
- [官方WFS说明](https://www.marineregions.org/webservices.php)：下载完整多边形，WFS 1.0.0、EPSG:4326，经度在前。
- [许可与来源说明](https://www.marineregions.org/disclaimer.php)：按CC BY注明VLIZ来源，提供方请求引用官方下载服务。提交包包含下载代码、来源元数据与事件匹配结果，不再分发完整海域边界数据。
- 文件SHA-256、要素数、服务时间戳及下载URL保存在`data/metadata/marine_boundaries_sources.json`。运行`00A_download_marine_boundaries.ipynb`准备边界，再运行两套全球匹配、Top30和全球统计Notebook。


## 附加3D图

固定对比历史版编号1、6、11、16对应的四个10°网格：瓦努阿图及邻近海域、日本东北—北海道及邻近海域、台湾—琉球西南部及邻近海域、菲律宾中北部及东侧海域。编号是历史版标识，不是新目录排名。
颜色区分浅源（<70km）、中源（70至<300km）和深源（≥300km），点面积随震级增大。经纬度网格非等面积，3D比例为示意，不能据此直接推断断层倾角或单位面积风险。

## 提交范围说明

按本次明确要求，第二套分析截至2024年，未扩展至2026年。最初任务文字要求最新目录分析包含2026年截至下载日记录；若最终评分仍采用该要求，需要与老师确认时间范围。本材料不包含泊松回归或五年均值预测，二者不在已给出的B分工内。
