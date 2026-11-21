# B部分提交与复现说明

先阅读 `B部分_结果分析.md`；1965—2024版按 `运行顺序_1965-2024.md` 中00—07运行。

历史版顺序：
1. math_china_historical.ipynb：省份匹配。
2. 全球省份匹配——历史、.ipynb：实际执行的是全球国家匹配。
3. 省份年份统计表——历史.ipynb。
4. 中国各省累计地震次数图.ipynb。
5. 全球地震统计图——历史.ipynb。
6. 中国与全球的top30震级图和表.ipynb。
7. dense_regions——历史.ipynb（附加3D图）。

解压后从DPW2目录启动Jupyter，选择装有pandas、numpy、matplotlib、shapely的Python内核；Pandas需支持format="mixed"（2.x或更新版本）。不要把其他Python版本的.python-deps目录加入内核路径。历史版按单元格顺序运行，新版按00—07文件顺序运行。

数据来源：历史原始07earthquake.csv经项目清洗后的historical_cleaned.csv；USGS数据为latest_cleaned.csv的时间子集。边界来源、下载参数和归属信息见data/metadata。PB2002不属于本次四地区3D图的必要输入。
省界源文件为geoBoundaries CHN ADM1；国家边界为Natural Earth 1:50m。未匹配记录保留；国家统计不包含海域强制归属。

结果：历史主要CSV和PNG在outputs；1965—2024结果在outputs/catalog_1965_2024；附加3D在各自dense_regions目录。
代码与输入已打包，历史与新版数据不要合并。图表结果已生成；新版代码已逐单元格执行验证，历史表已核验统计总数、年份列及排名数量，本次未重新执行全部历史Notebook。
范围差异及未包含的预测工作见结果分析最后一节。

## 海域更新运行说明

两套全球匹配前先运行 `00A_download_marine_boundaries.ipynb`（首次需联网下载完整边界）。新增 `marine_locations.py` 为海域匹配和汇总模块。所有代码、输出标签及图中文字使用英文。
然后重新运行全球国家匹配、全球和中国Top30、全球统计图Notebook。新版顺序为00 → 00A → 01/02 → 03—07；历史版先00A，再按原顺序。
新增输出：`*_location_totals.csv`、`*_location_year_counts.csv`、`*_location_review.csv`、`*_location_counts.png`。旧`*_country_totals.csv`和国家地图明确保留为陆地口径；全事件海域统计作为补充输出。
Marine Regions完整原始边界不放入提交包；下载脚本和来源元数据随包提供。省份统计与中国Top30口径保持不变。
