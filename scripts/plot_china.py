import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd


from paths import COUNTRY_BOUNDARIES, FIGURES_DIR, PROVINCE_BOUNDARIES, TABLES_DIR


EXTENT = [70, 139, 15, 56]
LON_LAT = ccrs.PlateCarree()
BACKGROUND = "#091521"
OCEAN = "#102331"
LAND = "#2B3D49"
TEXT = "#E6EDF2"
MUTED = "#A8BDC9"
DEPTH_GROUPS = [
    ("Shallow", "<70 km", "#FFC080"),
    ("Intermediate", "70 to <300 km", "#65D7DA"),
    ("Deep", "≥300 km", "#B494FF"),
]
CREDIT = "Earthquake data: 07earthquake.csv  ·  Boundaries: Natural Earth"


# Share the extent, grid and boundaries across all map panels.
def draw_basemap(ax, countries, provinces):
    ax.set_extent(EXTENT, crs=LON_LAT)
    ax.set_facecolor(OCEAN)
    ax.add_geometries(
        countries.geometry, crs=LON_LAT, facecolor=LAND,
        edgecolor="#75919F", linewidth=0.5, zorder=1,
    )
    ax.add_geometries(
        provinces.geometry, crs=LON_LAT, facecolor="none",
        edgecolor="#668391", linewidth=0.38, zorder=2,
    )
    grid = ax.gridlines(
        crs=LON_LAT, draw_labels=True, xlocs=[80, 90, 100, 110, 120, 130],
        ylocs=[20, 30, 40, 50], linewidth=0.4, color="#587482",
        alpha=0.45, x_inline=False, y_inline=False,
    )
    grid.top_labels = False
    grid.right_labels = False
    grid.xlabel_style = {"color": MUTED, "size": 8}
    grid.ylabel_style = {"color": MUTED, "size": 8}
    ax.spines["geo"].set_edgecolor("#496676")


# Match the depth colors used by the global earthquake maps.
def plot_epicenters(ax, records, color, layer, size):
    return ax.scatter(
        records["Longitude"], records["Latitude"],
        transform=LON_LAT, s=size, color=color,
        alpha=0.85, edgecolors="none", zorder=3 + layer,
    )


def main():
    quakes = pd.read_csv(TABLES_DIR / "earthquake_china_province.csv")
    countries = gpd.read_file(COUNTRY_BOUNDARIES).to_crs("EPSG:4326")
    countries = countries.cx[EXTENT[0]:EXTENT[1], EXTENT[2]:EXTENT[3]]
    provinces = gpd.read_file(PROVINCE_BOUNDARIES).to_crs("EPSG:4326")
    provinces = provinces.loc[provinces["adm0_a3"].eq("CHN")]

    depth = quakes["Depth"]
    masks = [depth.lt(70), depth.ge(70) & depth.lt(300), depth.ge(300)]
    groups = [quakes.loc[mask] for mask in masks]
    if sum(len(group) for group in groups) != len(quakes):
        raise ValueError("Some earthquake records are missing a depth classification.")
    min_lon, max_lon, min_lat, max_lat = EXTENT
    in_extent = quakes["Longitude"].between(min_lon, max_lon) & quakes["Latitude"].between(min_lat, max_lat)
    if not in_extent.all():
        raise ValueError("Some earthquake coordinates are missing or outside the map extent.")

    years = f"{quakes['year'].min()}–{quakes['year'].max()}"
    subtitle = f"{years}  ·  {len(quakes):,} events  ·  Catalog magnitude ≥{quakes['Magnitude'].min():g}"
    # Include every depth group in the legend, even when a group has no events.
    legend_handles = [
        Line2D([], [], marker="o", linestyle="none", color=color, markersize=6, label=label)
        for _, label, color in DEPTH_GROUPS
    ]
    for (name, _, _), group in zip(DEPTH_GROUPS, groups):
        print(f"{name} records: {len(group):,}")

    # Show all depth groups together before comparing them in separate panels.
    fig, ax = plt.subplots(
        figsize=(13, 8.7), subplot_kw={"projection": LON_LAT}, facecolor=BACKGROUND,
    )
    fig.subplots_adjust(left=0.065, right=0.965, bottom=0.13, top=0.86)
    draw_basemap(ax, countries, provinces)
    for layer, ((_, _, color), group) in enumerate(zip(DEPTH_GROUPS, groups)):
        plot_epicenters(ax, group, color, layer, size=13)

    fig.suptitle("Earthquake epicenters across China", color=TEXT, fontsize=23, y=0.96)
    fig.text(0.5, 0.904, subtitle, ha="center", color=MUTED, fontsize=11)
    fig.legend(
        handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, 0.055),
        ncol=3, frameon=False, labelcolor=TEXT, fontsize=11,
    )
    fig.text(0.5, 0.027, CREDIT, ha="center", color=MUTED, fontsize=9)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / "china_earthquake_distribution.png"
    fig.savefig(output_path, dpi=300, facecolor=BACKGROUND)
    print("Saved combined map:", output_path)

    # Keep depth colors consistent between the individual and combined panels.
    panel_fig, axes = plt.subplots(
        2, 2, figsize=(14.5, 10), subplot_kw={"projection": LON_LAT},
        facecolor=BACKGROUND,
    )
    panel_fig.subplots_adjust(
        left=0.053, right=0.972, bottom=0.135, top=0.855, wspace=0.11, hspace=0.23,
    )
    for panel in axes.flat:
        draw_basemap(panel, countries, provinces)

    combined = axes[1, 1]
    for layer, ((name, label, color), group) in enumerate(zip(DEPTH_GROUPS, groups)):
        panel = axes.flat[layer]
        plot_epicenters(panel, group, color, layer, size=9)
        plot_epicenters(combined, group, color, layer, size=9)
        panel.set_title(f"{name}  ·  {label}", loc="left", color=TEXT, fontsize=12, pad=8)
        panel.set_title(f"{len(group):,} events", loc="right", color=MUTED, fontsize=9, pad=8)

    combined.set_title("All earthquakes", loc="left", color=TEXT, fontsize=12, pad=8)
    combined.set_title(f"{len(quakes):,} events", loc="right", color=MUTED, fontsize=9, pad=8)
    panel_fig.suptitle("Earthquake epicenters across China by depth", color=TEXT, fontsize=23, y=0.96)
    panel_fig.text(0.5, 0.905, subtitle, ha="center", color=MUTED, fontsize=11)
    panel_fig.legend(
        handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, 0.055),
        ncol=3, frameon=False, labelcolor=TEXT, fontsize=11,
    )
    panel_fig.text(0.5, 0.028, CREDIT, ha="center", color=MUTED, fontsize=9)
    panel_path = FIGURES_DIR / "china_earthquake_depth_panels.png"
    panel_fig.savefig(panel_path, dpi=300, facecolor=BACKGROUND)
    print("Saved four-panel map:", panel_path)
    plt.close(fig)
    plt.close(panel_fig)


if __name__ == "__main__":
    main()
