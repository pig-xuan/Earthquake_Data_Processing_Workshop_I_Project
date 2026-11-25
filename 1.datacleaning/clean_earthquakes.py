import argparse
from pathlib import Path

import numpy as np
import pandas as pd


STAGE_DIR = Path(__file__).resolve().parent
RAW_DATA = STAGE_DIR / "07earthquake.csv"


# Return the mean, median, extrema and quartiles in the order used below.
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


def main():
    parser = argparse.ArgumentParser(description="Clean the earthquake catalog.")
    parser.add_argument("--inspect", action="store_true", help="Print steps 01–19 without exporting a CSV.")
    args = parser.parse_args()

    print("\n" + "=" * 72)
    print("01 | Load data")
    Earthquake_raw = pd.read_csv(RAW_DATA)
    earthquake = Earthquake_raw.copy()
    print(f"Raw rows: {earthquake.shape[0]:,}")
    print(f"Raw columns: {earthquake.shape[1]}")
    print("Column names:", list(earthquake.columns))


    print("\n" + "=" * 72)
    print("02 | Preview and column information")
    print("First five rows:")
    print(earthquake.head())
    print("\nColumn information:")
    earthquake.info()


    print("\n" + "=" * 72)
    print("03 | Raw numeric summary")
    numeric_columns = ["Latitude", "Longitude", "Depth", "Magnitude"]
    print(earthquake[numeric_columns].describe())


    # Missing-value detection does not flag blank strings.
    print("\n" + "=" * 72)
    print("04 | Missing-value check")
    missing_counts = earthquake.isnull().sum()
    print(missing_counts)


    # Keep negative depths as recorded; flag them later for review.
    print("\n" + "=" * 72)
    print("05 | Negative depths in the raw table")
    negative_depth = earthquake["Depth"] < 0
    print(f"Negative-depth records: {negative_depth.sum()}")
    print(earthquake.loc[negative_depth, ["Date", "Type", "Depth", "Magnitude"]])


    print("\n" + "=" * 72)
    print("06 | Event-type counts")
    type_counts = earthquake.groupby("Type")["Magnitude"].count()
    print(type_counts)


    # Work on a copy so filtering and date fixes leave the raw table intact.
    print("\n" + "=" * 72)
    print("07 | Select Earthquake events")
    earthquake_only = earthquake.loc[earthquake["Type"] == "Earthquake"].copy()
    removed_count = len(earthquake) - len(earthquake_only)
    print(f"Before: {len(earthquake):,}")
    print(f"After: {len(earthquake_only):,}")
    print(f"Excluded from the Earthquake subset: {removed_count}")
    print("First five rows:")
    print(earthquake_only.head())


    # Use text length to find unusual date formats, not to validate dates.
    print("\n" + "=" * 72)
    print("08 | Locate unusual date formats")
    unusual_dates = []
    for date in earthquake_only["Date"]:
        if len(date) != 10:
            unusual_dates.append(date)
    print(f"Records to inspect: {len(unusual_dates)}")
    for date in unusual_dates:
        print(date)


    # The unusual dates are ISO timestamps; rearrange YYYY-MM-DD into MM/DD/YYYY.
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


    # Longer time strings may be full ISO timestamps rather than invalid values.
    print("\n" + "=" * 72)
    print("10 | Locate unusual time formats")
    unusual_times = []
    for time in earthquake_only["Time"]:
        if len(time) > 8:
            unusual_times.append(time)
    print(f"Records to inspect: {len(unusual_times)}")
    for time in unusual_times:
        print(time)


    # Remove the ISO date and trailing Z while preserving fractional seconds.
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


    print("\n" + "=" * 72)
    print("12 | Combine date and time")
    earthquake_only["event_time_text"] = earthquake_only["Date"] + " " + earthquake_only["Time"]
    print(earthquake_only[["Date", "Time", "event_time_text"]].head())


    # Treat source times without a timezone as UTC and parse dates as month-first.
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


    # Put months in columns so each row summarizes one year.
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


    # Finite values still need separate checks for valid coordinate ranges.
    print("\n" + "=" * 72)
    print("17 | Numeric finiteness check")
    numeric_values = earthquake_only[numeric_columns].to_numpy()
    finite_mask = np.isfinite(numeric_values)
    finite_by_column = np.all(finite_mask, axis=0)
    print(pd.Series(finite_by_column, index=numeric_columns, name="all_finite"))
    print(f"Non-finite cells: {(~finite_mask).sum()}")


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


    # Flag unusual measurements without replacing or removing the source values.
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

    if args.inspect:
        return

    # Use [70, 300) km for intermediate events; negative depths remain in the shallow group.
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

    # Keep the original row index so exported records can be traced to the source.
    earthquake_only["source_row"] = earthquake_only.index
    output_file = STAGE_DIR / "earthquake_only.csv"
    earthquake_only.to_csv(output_file, index=False)
    print(f"Exported file: {output_file}")
    print("Exported rows:", len(earthquake_only))
    print("Exported columns:", earthquake_only.shape[1])


if __name__ == "__main__":
    main()
