import numpy as np
import pandas as pd


# Read the source CSV and keep an independent working copy.
print("\n" + "=" * 72)
print("Load data")
Earthquake_raw = pd.read_csv("/Users/guxuana/Desktop/Data Processing Workshop I /ProjectData/07earthquake.csv")
earthquake = Earthquake_raw.copy()
print(f"Raw rows: {earthquake.shape[0]:,}")
print(f"Raw columns: {earthquake.shape[1]}")
print("Column names:", list(earthquake.columns))
# Conclusion: 23,412 source records were loaded; the raw table is retained.


# Preview the records and inspect column types and non-null counts.
print("\n" + "=" * 72)
print("Preview and column information")
print("First five rows:")
print(earthquake.head())
print("\nColumn information:")
earthquake.info()
# Conclusion: Date, Time and Type are text; coordinates, depth and magnitude are numeric.


# Summarize the distributions before making any changes.
print("\n" + "=" * 72)
print("Raw numeric summary")
numeric_columns = ["Latitude", "Longitude", "Depth", "Magnitude"]
print(earthquake[numeric_columns].describe())
# Conclusion: Raw depths range from -1.1 to 700 km; negative values need review.


# Count recognized missing values in each source column.
print("\n" + "=" * 72)
print("Missing-value check")
missing_counts = earthquake.isnull().sum()
print(missing_counts)
# Conclusion: 0 missing cells were found in the raw table.


# Locate negative depths without changing the original measurements.
print("\n" + "=" * 72)
print("Negative depths in the raw table")
negative_depth = earthquake["Depth"] < 0
print(f"Negative-depth records: {negative_depth.sum()}")
print(earthquake.loc[negative_depth, ["Date", "Type", "Depth", "Magnitude"]])
# Conclusion: The raw table has 3 negative-depth records; their values are retained.


# Count each event type using the fully populated Magnitude column.
print("\n" + "=" * 72)
print("Event-type counts")
type_counts = earthquake.groupby("Type")["Magnitude"].count()
print(type_counts)
# Conclusion: The raw table contains 4 event types; an analysis-specific filter is needed.


# Keep Earthquake events and copy them before further assignments.
print("\n" + "=" * 72)
print("Select Earthquake events")
earthquake_only = earthquake.loc[earthquake["Type"] == "Earthquake"].copy()
removed_count = len(earthquake) - len(earthquake_only)
print(f"Before: {len(earthquake):,}")
print(f"After: {len(earthquake_only):,}")
print(f"Excluded from the Earthquake subset: {removed_count}")
print("First five rows:")
print(earthquake_only.head())
# Conclusion: 23,232 Earthquake records are retained; 180 other events are excluded.


# Collect dates whose text length differs from MM/DD/YYYY.
print("\n" + "=" * 72)
print("Locate unusual date formats")
unusual_dates = []
for date in earthquake_only["Date"]:
    if len(date) != 10:
        unusual_dates.append(date)
print(f"Records to inspect: {len(unusual_dates)}")
for date in unusual_dates:
    print(date)
# Conclusion: 3 date strings have a different length and require format review.


# Convert the inspected ISO date strings to MM/DD/YYYY using slicing.
print("\n" + "=" * 72)
print("Standardize date strings")
changed_date_rows = []
for idx in earthquake_only.index:
    date = earthquake_only.loc[idx, "Date"]
    if date in unusual_dates:
        new_date = date[5:7] + "/" + date[8:10] + "/" + date[0:4]
        earthquake_only.loc[idx, "Date"] = new_date
        changed_date_rows.append(idx)
        print(f"Row index {idx}: {date} -> {new_date}")
# Conclusion: 3 date strings were standardized; source records remain in the raw table.


# Inspect time strings longer than an ordinary whole-second time.
print("\n" + "=" * 72)
print("Locate unusual time formats")
unusual_times = []
for time in earthquake_only["Time"]:
    if len(time) > 8:
        unusual_times.append(time)
print(f"Records to inspect: {len(unusual_times)}")
for time in unusual_times:
    print(time)
# Conclusion: 3 longer time strings were found; all are full ISO timestamps in this file.


# Extract the time part while preserving fractional seconds.
print("\n" + "=" * 72)
print("Standardize time strings")
changed_time_rows = []
for idx in earthquake_only.index:
    time = earthquake_only.loc[idx, "Time"]
    if time in unusual_times:
        new_time = time[11:-1]
        earthquake_only.loc[idx, "Time"] = new_time
        changed_time_rows.append(idx)
        print(f"Row index {idx}: {time} -> {new_time}")
# Conclusion: 3 time strings were standardized with fractional seconds preserved.


# Concatenate each date and time with a separating space.
print("\n" + "=" * 72)
print("Combine date and time")
earthquake_only["event_time_text"] = earthquake_only["Date"] + " " + earthquake_only["Time"]
print(earthquake_only[["Date", "Time", "event_time_text"]].head())
# Conclusion: event_time_text has been created and is still a text column.


# Parse mixed time formats and interpret timezone-naive times as UTC.
print("\n" + "=" * 72)
print("Parse datetime values")
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
# Conclusion: 0 timestamps failed parsing; the analysis uses UTC.


# Extract calendar fields from the datetime column.
print("\n" + "=" * 72)
print("Extract year and month")
earthquake_only["year"] = earthquake_only["event_time"].dt.year
earthquake_only["month"] = earthquake_only["event_time"].dt.month
print(earthquake_only[["event_time", "year", "month"]].head())
year_min = earthquake_only["year"].min()
year_max = earthquake_only["year"].max()
year_count = len(earthquake_only["year"].unique())
print(f"Year range: {year_min} - {year_max}")
print(f"Distinct years: {year_count}")
# Conclusion: Records span 1965-2016 across 52 years; this alone does not establish catalog completeness.


# Count events by year, rank them, and reconcile the total.
print("\n" + "=" * 72)
print("Annual counts and reconciliation")
annual_count = earthquake_only.groupby("year")["Magnitude"].count()
print("First five years:")
print(annual_count.head())
print("\nTop five years by record count:")
print(annual_count.sort_values(ascending=False).head())
annual_total = annual_count.sum()
print(f"Annual total: {annual_total:,}")
print("Matches Earthquake row count:", annual_total == len(earthquake_only))
# Conclusion: Annual counts total 23,232 records; the Earthquake table contains 23,232.


# Move the month index level into columns and check the table total.
print("\n" + "=" * 72)
print("Year-by-month table")
monthly_count = earthquake_only.groupby(["year", "month"])["Magnitude"].count()
monthly_table = monthly_count.unstack().sort_index(ascending=False)
print("Latest five years:")
print(monthly_table.head())
monthly_total = monthly_table.sum().sum()
print(f"Table shape: {monthly_table.shape}")
print(f"Monthly total: {monthly_total:,}")
print("Matches Earthquake row count:", monthly_total == len(earthquake_only))
# Conclusion: The monthly table totals 23,232 records; each cell counts one year-month combination.


# Check finite numeric values and reduce the Boolean array by column.
print("\n" + "=" * 72)
print("Numeric finiteness check")
numeric_values = earthquake_only[numeric_columns].to_numpy()
finite_mask = np.isfinite(numeric_values)
finite_by_column = np.all(finite_mask, axis=0)
print(pd.Series(finite_by_column, index=numeric_columns, name="all_finite"))
print(f"Non-finite cells: {(~finite_mask).sum()}")
# Conclusion: The four numeric columns contain 0 non-finite values; range validity requires separate checks.


# Combine four parenthesized comparisons to validate coordinate bounds.
print("\n" + "=" * 72)
print("Coordinate range check")
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
# Conclusion: 23,232 records satisfy coordinate bounds; 0 are out of range.


# Add Boolean flags without deleting or replacing source measurements.
print("\n" + "=" * 72)
print("Depth and magnitude flags")
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
# Conclusion: 3 negative-depth, 4 zero-depth and 738 M>=7 events are flagged; source values are retained.


# Classify events by depth, count each group, and reconcile the total.
print("\n" + "=" * 72)
print("Depth-band classification and counts")
earthquake_only["shallow"] = earthquake_only["Depth"] < 70
earthquake_only["intermediate"] = (
    (earthquake_only["Depth"] >= 70)
    & (earthquake_only["Depth"] < 300)
)
earthquake_only["deep"] = earthquake_only["Depth"] >= 300

earthquake_only.loc[earthquake_only["shallow"], "depth_band"] = "shallow"
earthquake_only.loc[earthquake_only["intermediate"], "depth_band"] = "intermediate"
earthquake_only.loc[earthquake_only["deep"], "depth_band"] = "deep"
shallow_count = earthquake_only["shallow"].sum()
intermediate_count = earthquake_only["intermediate"].sum()
deep_count = earthquake_only["deep"].sum()
depth_total = shallow_count + intermediate_count + deep_count
print(f"Shallow (depth < 70 km): {shallow_count:,}")
print(f"Intermediate (70 <= depth < 300 km): {intermediate_count:,}")
print(f"Deep (depth >= 300 km): {deep_count:,}")
print(f"Total classified records: {depth_total:,}")
print("Matches Earthquake row count:", depth_total == len(earthquake_only))
# Conclusion: The depth groups contain 18,480, 3,425 and 1,327 records, totaling 23,232.


# Calculate magnitude statistics using NumPy.
print("\n" + "=" * 72)
print("Magnitude statistics with NumPy")
magnitude = earthquake_only["Magnitude"].to_numpy()
magnitude_mean = np.mean(magnitude)
magnitude_median = np.median(magnitude)
magnitude_percent = np.percentile(magnitude, [25, 50, 75])
magnitude_max = np.max(magnitude)
magnitude_min = np.min(magnitude)
print(f"Mean magnitude: {magnitude_mean:.4f}")
print(f"Median magnitude: {magnitude_median:g}")
print(f"Minimum magnitude: {magnitude_min:g}")
print(f"Maximum magnitude: {magnitude_max:g}")
print(f"25th percentile: {magnitude_percent[0]:g}")
print(f"50th percentile: {magnitude_percent[1]:g}")
print(f"75th percentile: {magnitude_percent[2]:g}")
print("Median matches 50th percentile:", magnitude_median == magnitude_percent[1])
# Conclusion: Magnitudes range from 5.5 to 9.1, and the median equals the 50th percentile.


# Define a reusable function that returns five numeric summary results.
def summarize_numeric(values):
    values_mean = np.mean(values)
    values_median = np.median(values)
    values_max = np.max(values)
    values_min = np.min(values)
    values_percent = np.percentile(values, [25, 50, 75])
    percentiles = []
    for percentile in values_percent:
        percentiles.append(percentile)
    return values_mean, values_median, values_max, values_min, percentiles
# Conclusion: The function returns mean, median, maximum, minimum and a list of the 25th, 50th and 75th percentiles.


# Call the summary function and unpack its results for labeled output.
print("\n" + "=" * 72)
print("Magnitude summary from the reusable function")
summary_mean, summary_median, summary_max, summary_min, summary_percentiles = summarize_numeric(magnitude)
print(f"Mean magnitude: {summary_mean:.4f}")
print(f"Median magnitude: {summary_median:g}")
print(f"Maximum magnitude: {summary_max:g}")
print(f"Minimum magnitude: {summary_min:g}")
print(f"25th percentile: {summary_percentiles[0]:g}")
print(f"50th percentile: {summary_percentiles[1]:g}")
print(f"75th percentile: {summary_percentiles[2]:g}")
# Conclusion: The function returns the same statistics as the direct NumPy calculations above.


# Preview processed records and validate counts, timestamps, labels, and coordinates.
print("\n" + "=" * 72)
print("Final data validation")
print("First five processed records:")
print(earthquake_only[["event_time", "Depth", "Magnitude", "depth_band", "year", "month"]].head().to_string())
print(f"\nData shape: {earthquake_only.shape}")
print(f"Earthquake records: {len(earthquake_only):,}")
print("Matches expected 23,232 records:", len(earthquake_only) == 23232)
print("Year values complete:", earthquake_only["year"].count() == len(earthquake_only))
print(f"Annual total: {annual_count.sum():,}")
print("Annual total matches row count:", annual_count.sum() == len(earthquake_only))
print(f"Monthly total: {monthly_table.sum().sum():,}")
print("Monthly total matches row count:", monthly_table.sum().sum() == len(earthquake_only))
print(f"Depth-band total: {depth_total:,}")
print("Depth-band total matches row count:", depth_total == len(earthquake_only))
print("Missing event times:", earthquake_only["event_time"].isnull().sum())
print("Missing depth labels:", earthquake_only["depth_band"].isnull().sum())
print("All numeric values are finite:", np.all(finite_mask))
print("All coordinates are within bounds:", valid_coordinates.all())
# Conclusion: All displayed checks pass for 23,232 records, with matching group totals and no missing timestamps or depth labels.

# The final data
earthquake_only["source_row"] = earthquake_only.index
earthquake_only.to_csv("earthquake_only.csv", index = False)
print("Exported file: earthquake_cleaned.csv")
print("Exported rows:", len(earthquake_only))
print("Exported columns:", earthquake_only.shape[1])
# Conclusion: The cleaned records are exported with source row indices.

