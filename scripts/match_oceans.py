"""Classify country-unmatched earthquake epicenters by ocean using Natural Earth."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

import geopandas as gpd
import pandas as pd
from shapely import area


from paths import BOUNDARIES_DIR, TABLES_DIR

BOUNDARY_VERSION = "ca96624a56bd078437bca8184e78163e5039ad19"
BOUNDARY_NAME = "ne_50m_geography_marine_polys"
BOUNDARY_FOLDER = BOUNDARIES_DIR / "marine"

# Group Southeast Asian seas with the Pacific and Mediterranean/Baltic seas with the Atlantic.
OCEAN_BY_BASIN = {
    "North Pacific Ocean": "Pacific Ocean",
    "South Pacific Ocean": "Pacific Ocean",
    "South East Asia Seas": "Pacific Ocean",
    "North Atlantic Ocean": "Atlantic Ocean",
    "South Atlantic Ocean": "Atlantic Ocean",
    "Mediterranean Region": "Atlantic Ocean",
    "Baltic Sea": "Atlantic Ocean",
    "Indian Ocean": "Indian Ocean",
    "Arctic Ocean": "Arctic Ocean",
    "Southern Ocean": "Southern Ocean",
    "Caspian Sea": "Inland Water",
}
RESULT_COLUMNS = ["ocean_name", "sea_name", "marine_basin", "ocean_match_status"]
LEGACY_COLUMNS = ["ocean_name_zh", "sea_name_zh"]


def read_github_json(url):
    request = Request(url, headers={"User-Agent": "earthquake-ocean-classifier"})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def get_boundary_file():
    """Use local boundary files and download only missing components."""
    BOUNDARY_FOLDER.mkdir(parents=True, exist_ok=True)
    for extension in ("shp", "shx", "dbf", "prj"):
        filename = f"{BOUNDARY_NAME}.{extension}"
        target = BOUNDARY_FOLDER / filename
        if target.is_file():
            continue

        print(f"Downloading {filename} ...", flush=True)
        metadata = read_github_json(
            "https://api.github.com/repos/nvkelso/natural-earth-vector/contents/"
            f"50m_physical/{filename}?ref={BOUNDARY_VERSION}"
        )
        payload = metadata
        if metadata.get("encoding") != "base64":
            payload = read_github_json(metadata["git_url"])
        content = base64.b64decode(payload["content"])
        # Verify the Git blob hash before replacing the cached boundary file.
        header = f"blob {len(content)}\0".encode()
        if hashlib.sha1(header + content).hexdigest() != metadata["sha"]:
            raise ValueError(f"Boundary checksum mismatch: {filename}")
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_bytes(content)
        temporary.replace(target)

    return BOUNDARY_FOLDER / f"{BOUNDARY_NAME}.shp"


def select_country_unmatched(earthquakes):
    # Prefer country names and codes because older exports may have incorrect status labels.
    country_fields = [
        column for column in ("country", "country_code", "coountry_code")
        if column in earthquakes.columns
    ]
    if country_fields:
        has_country = pd.Series(False, index=earthquakes.index)
        for column in country_fields:
            values = earthquakes[column].str.strip().str.lower()
            has_country |= ~values.isin(["", "nan", "none", "null"])
        return earthquakes.loc[~has_country].copy()

    if "country_matched_status" in earthquakes.columns:
        status = earthquakes["country_matched_status"].str.strip().str.lower()
        return earthquakes.loc[status == "unmatched"].copy()

    raise ValueError("Input must include country fields or country_matched_status.")


def main():
    default_input = TABLES_DIR / "earthquake_country_province.csv"
    if not default_input.is_file():
        default_input = TABLES_DIR / "earthquake_country.csv"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=default_input)
    args = parser.parse_args()

    earthquakes = pd.read_csv(args.input, dtype="string", keep_default_na=False)
    unmatched = select_country_unmatched(earthquakes)
    unmatched = unmatched.drop(columns=RESULT_COLUMNS + LEGACY_COLUMNS, errors="ignore")

    # Keep invalid coordinates in the export but exclude them from the spatial join.
    longitude = pd.to_numeric(unmatched["Longitude"], errors="coerce")
    latitude = pd.to_numeric(unmatched["Latitude"], errors="coerce")
    valid = (longitude.between(-180, 180) & latitude.between(-90, 90)).fillna(False)
    geometry = gpd.points_from_xy(longitude.loc[valid], latitude.loc[valid])
    quake_points = gpd.GeoDataFrame(unmatched.loc[valid], geometry=geometry, crs="EPSG:4326")

    # Check both +180 and -180 degrees because they represent the same meridian.
    antimeridian = valid & longitude.abs().eq(180).fillna(False)
    if antimeridian.any():
        alternate_points = quake_points.loc[antimeridian.loc[quake_points.index]].copy()
        alternate_points = alternate_points.set_geometry(gpd.points_from_xy(
            -longitude.loc[alternate_points.index], latitude.loc[alternate_points.index]
        ))
        quake_points = pd.concat([quake_points, alternate_points])

    marine_regions = gpd.read_file(
        get_boundary_file(), columns=["name", "oceanbasin"], encoding="utf-8"
    ).to_crs(quake_points.crs)
    marine_regions = marine_regions.rename(columns={"name": "sea_name", "oceanbasin": "marine_basin"})
    # Repair invalid polygons before testing which epicenters they contain.
    marine_regions["geometry"] = marine_regions.geometry.make_valid()
    marine_regions = marine_regions.loc[
        marine_regions.geometry.notna() & ~marine_regions.geometry.is_empty
    ].copy()
    marine_regions["ocean_name"] = marine_regions["marine_basin"].map(OCEAN_BY_BASIN)
    if marine_regions.empty or marine_regions["ocean_name"].isna().any():
        raise ValueError("The marine boundary file is empty or contains an unknown basin.")

    # Use planar area only to choose the more specific label within one ocean.
    marine_regions["polygon_area"] = area(marine_regions.geometry.array)

    # Use intersects to include epicenters exactly on a polygon boundary.
    matches = gpd.sjoin(quake_points[["geometry"]], marine_regions, how="inner", predicate="intersects")
    for column in ("ocean_name", "sea_name", "marine_basin"):
        unmatched[column] = pd.Series(pd.NA, index=unmatched.index, dtype="string")
    unmatched["ocean_match_status"] = "unmatched"
    unmatched.loc[~valid, "ocean_match_status"] = "invalid_coordinates"

    # Flag overlapping regions that disagree on the ocean instead of choosing arbitrarily.
    ocean_options = matches.groupby(level=0)["ocean_name"].nunique()
    ambiguous_indices = ocean_options.index[ocean_options > 1]
    ambiguous_matches = matches.loc[matches.index.isin(ambiguous_indices)]
    ambiguous_basins = ambiguous_matches.groupby(level=0)["marine_basin"].agg(
        lambda basins: " | ".join(sorted(set(basins)))
    )
    unmatched.loc[ambiguous_indices, "ocean_match_status"] = "ambiguous"
    unmatched.loc[ambiguous_indices, "marine_basin"] = ambiguous_basins

    # Prefer the smallest region only when all candidate polygons agree on the ocean.
    agreed = matches.loc[~matches.index.isin(ambiguous_indices)]
    agreed = agreed.sort_values(["polygon_area", "sea_name"])
    selected = agreed.loc[~agreed.index.duplicated()]
    unmatched.loc[selected.index, ["sea_name", "marine_basin"]] = selected[["sea_name", "marine_basin"]]

    ocean_matches = selected.loc[selected["ocean_name"] != "Inland Water"]
    unmatched.loc[ocean_matches.index, "ocean_name"] = ocean_matches["ocean_name"]
    unmatched.loc[ocean_matches.index, "ocean_match_status"] = "matched"
    unmatched.loc[selected.index[selected["ocean_name"] == "Inland Water"], "ocean_match_status"] = "inland_water"

    summary = (
        unmatched.groupby(["ocean_name", "ocean_match_status"], dropna=False)
        .size()
        .rename("earthquake_count")
        .reset_index()
        .sort_values("earthquake_count", ascending=False)
    )
    unresolved = unmatched.loc[unmatched["ocean_match_status"] != "matched"]
    matched_count = int((unmatched["ocean_match_status"] == "matched").sum())

    if summary["earthquake_count"].sum() != len(unmatched):
        raise ValueError("The summary does not account for every country-unmatched record.")

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    unmatched.to_csv(TABLES_DIR / "earthquake_ocean.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(TABLES_DIR / "earthquake_ocean_summary.csv", index=False, encoding="utf-8-sig")
    unresolved.to_csv(TABLES_DIR / "earthquake_ocean_unresolved.csv", index=False, encoding="utf-8-sig")

    print(f"Input earthquake records: {len(earthquakes):,}")
    print(f"Records without a country match: {len(unmatched):,}")
    print(f"Records matched to an ocean: {matched_count:,}")
    print(f"Records without an ocean assignment: {len(unresolved):,}")
    print(summary.fillna("").to_string(index=False))
    print("Saved earthquake_ocean.csv, earthquake_ocean_summary.csv, and earthquake_ocean_unresolved.csv.")


if __name__ == "__main__":
    main()
