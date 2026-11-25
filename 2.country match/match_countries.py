from pathlib import Path

import pandas as pd
import geopandas as gpd


STAGE_DIR = Path(__file__).resolve().parent
CLEANED_DATA = STAGE_DIR.parent / "1.datacleaning" / "earthquake_only.csv"
COUNTRY_BOUNDARIES = STAGE_DIR / "boundaries" / "ne_50m_admin_0_countries.zip"


countries = gpd.read_file(COUNTRY_BOUNDARIES)
earthquake_only = pd.read_csv(CLEANED_DATA)

print("First five records:")
print(countries.head())

print("Column names:")
print(countries.columns)

print("Coordinate reference system:", countries.crs)

# Use longitude as x and latitude as y in WGS84.
points = gpd.points_from_xy(earthquake_only["Longitude"],earthquake_only["Latitude"])
quake_points = gpd.GeoDataFrame(earthquake_only, geometry = points, crs = "EPSG:4326" )

print("First five earthquake points:")
print(quake_points[["Longitude", "Latitude", "geometry"]].head())

print("Coordinate reference system:", quake_points.crs)
print("Number of earthquake points:", len(quake_points))
print()

print(countries.columns)
# Both layers must use the same coordinate reference system for a spatial join.
countries = countries.to_crs(quake_points.crs)
# Keep unmatched epicenters in the left join; within excludes exact boundary points.
quakes_with_country = gpd.sjoin(quake_points, countries[["ADMIN", "ADM0_A3", "geometry"]], how = "left", predicate = "within")
print(quakes_with_country[["Longitude", "Latitude", "ADMIN", "ADM0_A3"]].head())
print("Records before matching:", len(quake_points))
print("Records after matching:", len(quakes_with_country))

not_match = quakes_with_country["ADMIN"].isnull().sum()
print(quakes_with_country["ADMIN"].isnull().sum())
match_rate = ( len(quake_points) - not_match ) / len(quake_points) * 100
print(f"Country match rate: {match_rate:.2f}%")
print("Row count unchanged:", len(quakes_with_country) == len(quake_points))
unmatched_mask = quakes_with_country["ADMIN"].isnull()
print(quakes_with_country.loc[unmatched_mask,["Longitude", "Latitude", "Magnitude", "ADMIN"]].head())
print()

matched_mask = ~quakes_with_country["ADMIN"].isnull()
matched_quakes = quakes_with_country.loc[matched_mask].copy()
country_counts = matched_quakes.groupby("ADMIN")["Magnitude"].count().sort_values(ascending = False)
print(countries.head(10))

matched_total = country_counts.sum()
unmatched_total = (~matched_mask).sum()

print("Matched records:", matched_total)
print("Unmatched records:", unmatched_total)
print("Country total matches matched rows:",
      matched_total == len(matched_quakes))
print("All records accounted for:",
      matched_total + unmatched_total == len(quake_points))

earthquake_country = quakes_with_country.rename(columns ={"ADMIN" : "country", "ADM0_A3": "country_code"})
earthquake_country["country_matched_status"] = "unmatched"
earthquake_country.loc[matched_mask, "country_matched_status"] = "matched"
export_data = earthquake_country.drop(columns= ["geometry", "index_right"])
export_data.to_csv(STAGE_DIR / "earthquake_country.csv", index=False)
