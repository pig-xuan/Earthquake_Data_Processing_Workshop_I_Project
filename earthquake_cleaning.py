import numpy as np
import pandas as pd


# 01. Read the source CSV and keep an independent working copy.
# 01. 读取原始 CSV，并创建独立的工作副本。
print("\n" + "=" * 72)
print("01 | Load data")
Earthquake_raw = pd.read_csv("data/07earthquake.csv")
earthquake = Earthquake_raw.copy()
print(f"Raw rows: {earthquake.shape[0]:,}")
print(f"Raw columns: {earthquake.shape[1]}")
print("Column names:", list(earthquake.columns))
# 结论：原始数据包含 23,412 条记录，原表保留用于核查。
# Conclusion: 23,412 source records were loaded; the raw table is retained.


# 02. Preview the records and inspect column types and non-null counts.
# 02. 预览记录，检查各列类型及非空数量。
print("\n" + "=" * 72)
print("02 | Preview and column information")
print("First five rows:")
print(earthquake.head())
print("\nColumn information:")
earthquake.info()
# 结论：Date、Time 和 Type 为文本，经纬度、深度和震级为数值列。
# Conclusion: Date, Time and Type are text; coordinates, depth and magnitude are numeric.


# 03. Summarize the distributions before making any changes.
# 03. 修改前先查看数值分布，识别需要进一步核查的取值。
print("\n" + "=" * 72)
print("03 | Raw numeric summary")
numeric_columns = ["Latitude", "Longitude", "Depth", "Magnitude"]
print(earthquake[numeric_columns].describe())
# 结论：原表深度范围为 -1.1 至 700 km，负值需核查。
# Conclusion: Raw depths range from -1.1 to 700 km; negative values need review.


# 04. Count recognized missing values in each source column.
# 04. 逐列统计 Pandas 识别的缺失值；此处不检查空白字符串。
print("\n" + "=" * 72)
print("04 | Missing-value check")
missing_counts = earthquake.isnull().sum()
print(missing_counts)
# 结论：原表共发现 0 个缺失单元格。
# Conclusion: 0 missing cells were found in the raw table.


# 05. Locate negative depths without changing the original measurements.
# 05. 定位负深度记录，保留原始测量值供后续核查。
print("\n" + "=" * 72)
print("05 | Negative depths in the raw table")
negative_depth = earthquake["Depth"] < 0
print(f"Negative-depth records: {negative_depth.sum()}")
print(earthquake.loc[negative_depth, ["Date", "Type", "Depth", "Magnitude"]])
# 结论：原表有 3 条负深度记录，本步骤仅查看，不修改。
# Conclusion: The raw table has 3 negative-depth records; their values are retained.


# 06. Count each event type using the fully populated Magnitude column.
# 06. 利用没有缺失值的震级列，统计各事件类型的记录数。
print("\n" + "=" * 72)
print("06 | Event-type counts")
type_counts = earthquake.groupby("Type")["Magnitude"].count()
print(type_counts)
# 结论：原表包含 4 种事件类型，需要按分析目标筛选。
# Conclusion: The raw table contains 4 event types; an analysis-specific filter is needed.


# 07. Keep Earthquake events and copy them before further assignments.
# 07. 保留 Earthquake 事件，并复制为独立表后再修改。
print("\n" + "=" * 72)
print("07 | Select Earthquake events")
earthquake_only = earthquake.loc[earthquake["Type"] == "Earthquake"].copy()
removed_count = len(earthquake) - len(earthquake_only)
print(f"Before: {len(earthquake):,}")
print(f"After: {len(earthquake_only):,}")
print(f"Excluded from the Earthquake subset: {removed_count}")
print("First five rows:")
print(earthquake_only.head())
# 结论：保留 23,232 条地震记录，筛出其他类型 180 条。
# Conclusion: 23,232 Earthquake records are retained; 180 other events are excluded.


# 08. Collect dates whose text length differs from MM/DD/YYYY.
# 08. 收集长度不等于 10 的日期；长度差异只作为格式核查线索。
print("\n" + "=" * 72)
print("08 | Locate unusual date formats")
unusual_dates = []
for date in earthquake_only["Date"]:
    if len(date) != 10:
        unusual_dates.append(date)
print(f"Records to inspect: {len(unusual_dates)}")
for date in unusual_dates:
    print(date)
# 结论：发现 3 条长度不同的日期，需查看原值后统一格式。
# Conclusion: 3 date strings have a different length and require format review.


# 09. Convert the inspected ISO date strings to MM/DD/YYYY using slicing.
# 09. 用字符串切片整理已核查的 ISO 日期，并通过行索引写回。
print("\n" + "=" * 72)
print("09 | Standardize date strings")
changed_date_rows = []
for idx in earthquake_only.index:
    date = earthquake_only.loc[idx, "Date"]
    if date in unusual_dates:
        new_date = date[5:7] + "/" + date[8:10] + "/" + date[0:4]
        earthquake_only.loc[idx, "Date"] = new_date
        changed_date_rows.append(idx)
        print(f"Row index {idx}: {date} -> {new_date}")
# 结论：已统一 3 条日期文本，原始记录仍保存在原表中。
# Conclusion: 3 date strings were standardized; source records remain in the raw table.


# 10. Inspect time strings longer than an ordinary whole-second time.
# 10. 查看超过普通时分秒长度的字符串；较长不代表数据无效。
print("\n" + "=" * 72)
print("10 | Locate unusual time formats")
unusual_times = []
for time in earthquake_only["Time"]:
    if len(time) > 8:
        unusual_times.append(time)
print(f"Records to inspect: {len(unusual_times)}")
for time in unusual_times:
    print(time)
# 结论：发现 3 条较长的时间文本，本文件中均为完整 ISO 时间戳。
# Conclusion: 3 longer time strings were found; all are full ISO timestamps in this file.


# 11. Extract the time part while preserving fractional seconds.
# 11. 提取 T 后、Z 前的时间，保留小数秒；Z 的 UTC 口径将在解析时恢复。
print("\n" + "=" * 72)
print("11 | Standardize time strings")
changed_time_rows = []
for idx in earthquake_only.index:
    time = earthquake_only.loc[idx, "Time"]
    if time in unusual_times:
        new_time = time[11:-1]
        earthquake_only.loc[idx, "Time"] = new_time
        changed_time_rows.append(idx)
        print(f"Row index {idx}: {time} -> {new_time}")
# 结论：已整理 3 条时间文本，小数秒得到保留。
# Conclusion: 3 time strings were standardized with fractional seconds preserved.


# 12. Concatenate each date and time with a separating space.
# 12. 将日期、空格和时间按行拼接，生成完整的日期时间文本。
print("\n" + "=" * 72)
print("12 | Combine date and time")
earthquake_only["event_time_text"] = earthquake_only["Date"] + " " + earthquake_only["Time"]
print(earthquake_only[["Date", "Time", "event_time_text"]].head())
# 结论：已生成 event_time_text，此列目前仍是文本。
# Conclusion: event_time_text has been created and is still a text column.


# 13. Parse mixed time formats and interpret timezone-naive times as UTC.
# 13. 解析混合时间格式；假设无时区标记的普通时间也是 UTC。
print("\n" + "=" * 72)
print("13 | Parse datetime values")
earthquake_only["event_time"] = pd.to_datetime(
    earthquake_only["event_time_text"],
    format="mixed",
    dayfirst=False,
    errors="coerce",
    utc=True,
)
invalid_time = earthquake_only["event_time"].isnull()
print("Parsed dtype:", earthquake_only["event_time"].dtype)
print(earthquake_only[["event_time_text", "event_time"]].head())
print(f"Failed parses: {invalid_time.sum()}")
if invalid_time.any():
    print("Records that failed parsing:")
    print(earthquake_only.loc[invalid_time, ["Date", "Time", "event_time_text"]])
# 结论：日期时间解析失败 0 条，统一采用 UTC 时间口径。
# Conclusion: 0 timestamps failed parsing; the analysis uses UTC.


# 14. Extract calendar fields from the datetime column.
# 14. 通过 dt 访问器提取年份和月份，并检查年份覆盖。
print("\n" + "=" * 72)
print("14 | Extract year and month")
earthquake_only["year"] = earthquake_only["event_time"].dt.year
earthquake_only["month"] = earthquake_only["event_time"].dt.month
print(earthquake_only[["event_time", "year", "month"]].head())
year_min = earthquake_only["year"].min()
year_max = earthquake_only["year"].max()
year_count = len(earthquake_only["year"].unique())
print(f"Year range: {year_min} - {year_max}")
print(f"Distinct years: {year_count}")
# 结论：记录覆盖 1965 至 2016 年，共 52 个年份；这不单独证明目录完整。
# Conclusion: Records span 1965-2016 across 52 years; this alone does not establish catalog completeness.


# 15. Count events by year, rank them, and reconcile the total.
# 15. 按年计数、降序排名，并核对年度合计与地震总行数。
print("\n" + "=" * 72)
print("15 | Annual counts and reconciliation")
annual_count = earthquake_only.groupby("year")["Magnitude"].count()
print("First five years:")
print(annual_count.head())
print("\nTop five years by record count:")
print(annual_count.sort_values(ascending=False).head())
annual_total = annual_count.sum()
print(f"Annual total: {annual_total:,}")
print("Matches Earthquake row count:", annual_total == len(earthquake_only))
# 结论：年度计数合计 23,232 条，地震表共 23,232 条。
# Conclusion: Annual counts total 23,232 records; the Earthquake table contains 23,232.


# 16. Move the month index level into columns and check the table total.
# 16. 将月份索引展开为列，形成年度月份表并核对总数。
print("\n" + "=" * 72)
print("16 | Year-by-month table")
monthly_count = earthquake_only.groupby(["year", "month"])["Magnitude"].count()
monthly_table = monthly_count.unstack().sort_index(ascending=False)
print("Latest five years:")
print(monthly_table.head())
monthly_total = monthly_table.sum().sum()
print(f"Table shape: {monthly_table.shape}")
print(f"Monthly total: {monthly_total:,}")
print("Matches Earthquake row count:", monthly_total == len(earthquake_only))
# 结论：年月表合计 23,232 条，各单元格表示对应年月的记录数。
# Conclusion: The monthly table totals 23,232 records; each cell counts one year-month combination.


# 17. Check finite numeric values and reduce the Boolean array by column.
# 17. 检查数值是否有限，沿 axis=0 汇总为每列一个判断结果。
print("\n" + "=" * 72)
print("17 | Numeric finiteness check")
numeric_values = earthquake_only[numeric_columns].to_numpy()
finite_mask = np.isfinite(numeric_values)
finite_by_column = np.all(finite_mask, axis=0)
print(pd.Series(finite_by_column, index=numeric_columns, name="all_finite"))
print(f"Non-finite cells: {(~finite_mask).sum()}")
# 结论：四个数值列共有 0 个非有限值；此检查不判断数值是否合理。
# Conclusion: The four numeric columns contain 0 non-finite values; range validity requires separate checks.


# 18. Combine four parenthesized comparisons to validate coordinate bounds.
# 18. 将四个带括号的比较条件用 & 连接，检查经纬度边界。
print("\n" + "=" * 72)
print("18 | Coordinate range check")
valid_coordinates = (
    (earthquake_only["Latitude"] <= 90)
    & (earthquake_only["Latitude"] >= -90)
    & (earthquake_only["Longitude"] >= -180)
    & (earthquake_only["Longitude"] <= 180)
)
print(f"Valid records: {valid_coordinates.sum():,}")
print(f"Out-of-range records: {(~valid_coordinates).sum()}")
print("All records pass:", valid_coordinates.all())
if (~valid_coordinates).any():
    print(earthquake_only.loc[~valid_coordinates, ["Latitude", "Longitude"]])
# 结论：23,232 条记录满足经纬度范围，越界 0 条。
# Conclusion: 23,232 records satisfy coordinate bounds; 0 are out of range.


# 19. Add Boolean flags without deleting or replacing source measurements.
# 19. 添加布尔标记，不删除记录，也不替换原始深度和震级。
print("\n" + "=" * 72)
print("19 | Depth and magnitude flags")
earthquake_only["is_negative_depth"] = earthquake_only["Depth"] < 0
earthquake_only["is_zero_depth"] = earthquake_only["Depth"] == 0
earthquake_only["is_m7_plus"] = earthquake_only["Magnitude"] >= 7
negative_count = earthquake_only["is_negative_depth"].sum()
zero_count = earthquake_only["is_zero_depth"].sum()
m7_count = earthquake_only["is_m7_plus"].sum()
print(f"Negative depth: {negative_count}")
print(f"Zero depth: {zero_count}")
print(f"Magnitude >= 7: {m7_count}")
print("\nNegative-depth details:")
print(earthquake_only.loc[earthquake_only["is_negative_depth"], ["Date", "Depth", "Magnitude"]])
# 结论：负深度 3 条、零深度 4 条、M≥7 事件 738 条，源值均保留。
# Conclusion: 3 negative-depth, 4 zero-depth and 738 M>=7 events are flagged; source values are retained.
