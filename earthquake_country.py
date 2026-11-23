import pandas as pd
import numpy as np
import geopandas as gpd

countries = gpd.read_file(
    '/Users/guxuana/Desktop/Data Processing Workshop I /earthquake/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp'
)
earthquake_only = pd.read_csv('/Users/guxuana/Desktop/Data Processing Workshop I /earthquake/earthquake_only.csv')

print("First five records:")
print(countries.head())

print("Column names:")
print(countries.columns)

print("Coordinate reference system:", countries.crs)
# Conclusion: The boundary table provides country attributes and polygon geometries.

points = gpd.points_from_xy(earthquake_only["Longitude"],earthquake_only["Latitude"])
quake_points = gpd.GeoDataFrame(earthquake_only, geometry = points, crs = "EPSG:4326" )

print("First five earthquake points:")
print(quake_points[["Longitude", "Latitude", "geometry"]].head())

print("Coordinate reference system:", quake_points.crs)
print("Number of earthquake points:", len(quake_points))
print()

print(countries.columns)
quakes_crs = countries.to_crs(quake_points.crs)
quakes_with_country = gpd.sjoin(quake_points, countries[["ADMIN", "ADM0_A3", "geometry"]], how = "left", predicate = "within")
print(quakes_with_country[["Longitude", "Latitude", "ADMIN", "ADM0_A3"]].head())
print("Records before matching:", len(quake_points))
print("Records after matching:", len(quakes_with_country))
# Conclusion: Country attributes are attached to points located within country polygons.

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
# Conclusion: Country counts summarize matched records, with unmatched records counted separately.

earthquake_country = quakes_with_country.rename(columns ={"ADMIN" : "country", "ADM0_A3": "coountry_code"})
earthquake_country["country_matched_status"] = "unmatched"
earthquake_country.loc[matched_mask, "countery_matched_status"] = "matched"
export_data = earthquake_country.drop(columns= ["geometry", "index_right"])
export_data.to_csv("earthquake_country.csv", index = False)
