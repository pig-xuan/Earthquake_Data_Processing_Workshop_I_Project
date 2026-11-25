# 地震目录数据处理与可视化

DS 2043 Data Processing Workshop I · 2026 Fall · 选题 07

项目以 1965–2016 年的 USGS 地震目录为输入，完成数据清洗、国家和中国省级区域匹配、海域分类、K-means 聚类及制图。课程 B 部分的 Notebook、扩展目录和提交材料见 [B 部分提交与复现说明](reports/part-b/B部分_提交说明.md)。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| [`data/`](data/) | 课程原始数据 `07earthquake.csv` 以及 Natural Earth 边界文件 |
| [`scripts/`](scripts/) | 清洗、地理匹配、聚类和绘图脚本 |
| [`results/tables/`](results/tables/) | 清洗后的目录、地理匹配、海域统计和聚类结果 |
| [`results/figures/`](results/figures/) | 全球和中国震中分布图、深度分组图及聚类图 |
| [`reports/part-b/`](reports/part-b/) | B 部分提交包、文件清单、复现说明和结果分析 |

## 安装与运行

使用 Python 3.13。克隆项目后，在仓库根目录安装依赖。

```bash
git clone https://github.com/pig-xuan/Earthquake_Data_Processing_Workshop_I_Project.git
cd Earthquake_Data_Processing_Workshop_I_Project
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

下面的顺序可以从原始 CSV 重新生成全部结果。脚本使用相对于仓库的输入和输出路径，因此也可以在其他目录用脚本的绝对路径执行。绘图脚本直接保存 PNG。

```bash
python scripts/clean_earthquakes.py
python scripts/match_countries.py
python scripts/match_china_provinces.py
python scripts/match_oceans.py
python scripts/cluster_earthquakes.py
python scripts/plot_world.py
python scripts/plot_china.py
python scripts/plot_clusters.py
```

| 脚本 | 生成文件或用途 |
| --- | --- |
| `clean_earthquakes.py` | `earthquake_only.csv`。加 `--inspect` 可只打印前 19 步清洗检查，不写入 CSV |
| `match_countries.py` | `earthquake_country.csv`，按国家边界匹配 |
| `match_china_provinces.py` | `earthquake_country_province.csv` 和 `earthquake_china_province.csv` |
| `match_oceans.py` | `earthquake_ocean.csv`、`earthquake_ocean_summary.csv` 和 `earthquake_ocean_unresolved.csv`。默认读取全球国家与省级匹配表，也可用 `--input` 指定其他匹配表 |
| `cluster_earthquakes.py` | `earthquake_kmeans.csv`。将经纬度转成单位球面坐标，再用 NumPy 实现的 K-means 分为 6 组 |
| `plot_world.py` | 从清洗表生成全球震中分布图和深度分组图 |
| `plot_china.py` | 从中国省级匹配表生成中国震中分布图和深度分组图 |
| `plot_clusters.py` | 从聚类表生成全球聚类分布和年度计数图 |

主要脚本所需边界数据随仓库提供，依赖装好后可以离线运行。B 部分提交包包含独立的 Notebook 流程和 1965–2024 年扩展目录，使用的海域边界和分类口径见该提交包的说明。

## 数据与检查结果

原始课程 CSV 有 23,412 条记录，涵盖 1965–2016 年，字段为日期、时间、纬度、经度、事件类型、深度（km）和震级。清洗在副本上筛选 `Earthquake` 事件，统一日期时间格式，保留零基原始行号 `source_row`，并给深度和震级添加标记。原始 CSV 及经纬度、深度和震级测量值保持原样。

| 检查项 | 结果 |
| --- | ---: |
| 原始记录 / 地震记录 | 23,412 / 23,232 |
| 非地震事件 | 180 |
| 格式异常的日期 / 时间文本 | 3 / 3 |
| 时间解析失败 / 坐标越界 | 0 / 0 |
| 年度与年月统计合计 | 均为 23,232 |
| 负深度 / 零深度 / M ≥ 7 | 3 / 4 / 738 |
| 匹配到国家或地区 / 未匹配 | 4,781 / 18,451 |

国家和省级匹配按 Natural Earth 多边形的内部进行空间连接。海域分类只处理国家匹配为空的记录，对边界重叠且海洋归属不一致的震中标记 `ambiguous`，并将未得到海洋归属的记录一并保存在待复核表中。地图深度区间为浅源（低于 70 km）、中源（70 至低于 300 km）和深源（至少 300 km）。

## 结果预览

![1965–2016 年全球地震震中分布](results/figures/global_earthquake_distribution.png)

[中国地震深度分组图](results/figures/china_earthquake_depth_panels.png) · [全球 K-means 聚类图](results/figures/earthquake_kmeans_visualization.png) · [海域统计表](results/tables/earthquake_ocean_summary.csv)
