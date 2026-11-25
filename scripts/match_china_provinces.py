import pandas as pd
import geopandas as gpd

from paths import COUNTRY_BOUNDARIES, PROVINCE_BOUNDARIES, TABLES_DIR

earthquake_only = pd.read_csv(TABLES_DIR / "earthquake_only.csv")
countries = gpd.read_file(COUNTRY_BOUNDARIES)
provinces = gpd.read_file(PROVINCE_BOUNDARIES)

print("Country boundary CRS:", countries.crs)
print("Province boundary CRS:", provinces.crs)
print("Number of earthquake records:", len(earthquake_only))

# Use longitude as x and latitude as y in WGS84.
points = gpd.points_from_xy(
    earthquake_only["Longitude"],
    earthquake_only["Latitude"]
)
quake_points = gpd.GeoDataFrame(
    earthquake_only, geometry=points, crs="EPSG:4326"
)

countries = countries.to_crs(quake_points.crs)
provinces = provinces.to_crs(quake_points.crs)

# Keep country-unmatched epicenters in the table for later ocean classification.
country_boundaries = countries[["ADMIN", "ADM0_A3", "geometry"]].rename(
    columns={"ADMIN": "country", "ADM0_A3": "country_code"}
)

quakes = gpd.sjoin(
    quake_points,
    country_boundaries,
    how="left",
    predicate="within"
).drop(columns="index_right")

if not quakes.index.is_unique or len(quakes) != len(quake_points):
    raise ValueError("Country matching returned more than one row for some points.")

quakes["country_matched_status"] = "unmatched"
quakes.loc[quakes["country_code"].notna(), "country_matched_status"] = "matched"

print("\nTop 10 countries by earthquake count:")
print(quakes.groupby("country").size().sort_values(ascending=False).head(10))
print("Country unmatched records:", quakes["country_code"].isna().sum())

# Match province boundaries only to records assigned to mainland China.
china_provinces = provinces.loc[
    provinces["adm0_a3"] == "CHN", ["name", "name_zh", "geometry"]
].copy()

china_provinces["province"] = china_provinces["name_zh"].fillna(
    china_provinces["name"]
)

china_mainland = quakes.loc[quakes["country_code"] == "CHN"].copy()
province_matches = gpd.sjoin(
    china_mainland,
    china_provinces[["province", "geometry"]],
    how="left",
    predicate="within"
)

if not province_matches.index.is_unique:
    raise ValueError("Some earthquake points matched more than one province.")

# Index alignment puts each province label back on its original earthquake row.
quakes["province"] = province_matches["province"]

# Include Hong Kong, Macao and Taiwan as province-level entries in this summary.
extra_regions = {
    "HKG": "香港特别行政区",
    "MAC": "澳门特别行政区",
    "TWN": "台湾"
}

for code, province_name in extra_regions.items():
    quakes.loc[quakes["country_code"] == code, "province"] = province_name

china_codes = ["CHN", "HKG", "MAC", "TWN"]
china_mask = quakes["country_code"].isin(china_codes)

quakes["province_matched_status"] = "not_applicable"
quakes.loc[china_mask, "province_matched_status"] = "unmatched"
quakes.loc[china_mask & quakes["province"].notna(), "province_matched_status"] = "matched"

china_quakes = quakes.loc[china_mask].copy()

province_counts = china_quakes.groupby("province").size().sort_values(
    ascending=False
)
province_unmatched = china_quakes["province"].isna().sum()

print("\nEarthquake counts by Chinese province-level region:")
print(province_counts)
print("China records:", len(china_quakes))
print("Province matched records:", province_counts.sum())
print("Province unmatched records:", province_unmatched)
print("All China records accounted for:",
      province_counts.sum() + province_unmatched == len(china_quakes))

quakes.drop(columns="geometry").to_csv(
    TABLES_DIR / "earthquake_country_province.csv",
    index=False,
    encoding="utf-8-sig"
)

china_quakes.drop(columns="geometry").to_csv(
    TABLES_DIR / "earthquake_china_province.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nSaved earthquake_country_province.csv")
print("Saved earthquake_china_province.csv")
