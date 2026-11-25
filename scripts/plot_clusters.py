import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.affinity import translate


from paths import COUNTRY_BOUNDARIES, FIGURES_DIR, TABLES_DIR

# Plot only records that received a cluster assignment.
quakes = pd.read_csv(TABLES_DIR / "earthquake_kmeans.csv")
quakes = quakes.dropna(subset=["Cluster"]).copy()
quakes["Cluster"] = quakes["Cluster"].astype(int)

world = gpd.read_file(COUNTRY_BOUNDARIES).to_crs("EPSG:4326")

# Share cluster colors across the map and yearly counts.
palette = ["#46d6d0", "#ffc075", "#bea3ff",
           "#ff8294", "#77d896", "#70b0ff"]
clusters = sorted(quakes["Cluster"].unique())
colors = {cluster: palette[i] for i, cluster in enumerate(clusters)}

background = "#0b1522"
panel = "#102332"
text = "#eff5fb"
muted = "#aec3d3"
grid = "#2b4559"

fig, (ax_map, ax_year) = plt.subplots(
    2, 1, figsize=(13, 8),
    height_ratios=[2, 1],
    layout="constrained"
)
fig.patch.set_facecolor(background)

for ax in (ax_map, ax_year):
    ax.set_facecolor(panel)
    ax.tick_params(colors=muted)
    for spine in ax.spines.values():
        spine.set_color(grid)

# Repeat the basemap at +360 degrees to match the wrapped longitudes.
world.plot(ax=ax_map, color="#283d4c", edgecolor="#4a6273", linewidth=0.25)
shifted = world.geometry.apply(lambda geometry: translate(geometry, xoff=360))
shifted.plot(ax=ax_map, color="#283d4c", edgecolor="#4a6273", linewidth=0.25)

for cluster in clusters:
    group = quakes[quakes["Cluster"] == cluster]
    # Wrap longitudes into [-30, 330) to keep the Pacific in one piece.
    map_lon = (group["Longitude"] + 30) % 360 - 30

    ax_map.scatter(
        map_lon, group["Latitude"],
        s=2.5, color=colors[cluster], alpha=0.8, linewidths=0,
        label=f"Cluster {cluster} ({len(group):,})"
    )

ax_map.set_xlim(-30, 330)
ax_map.set_ylim(-90, 90)
ax_map.set_aspect("auto")
ax_map.set_xlabel("")
ax_map.set_ylabel("")
ax_map.set_xticks([])
ax_map.set_yticks([])
ax_map.set_title("Global earthquake clusters", color=text, loc="left")
ax_map.legend(
    loc="upper left", bbox_to_anchor=(0, -0.02),
    ncol=6, frameon=False, labelcolor=muted, markerscale=3
)

# Fill missing years with zero so gaps remain visible on the timeline.
annual = quakes.groupby(["year", "Cluster"]).size().unstack(fill_value=0)
all_years = range(annual.index.min(), annual.index.max() + 1)
annual = annual.reindex(all_years, fill_value=0)

bottom = pd.Series(0, index=annual.index)

for cluster in clusters:
    ax_year.bar(
        annual.index, annual[cluster],
        bottom=bottom, color=colors[cluster], width=0.85
    )
    bottom = bottom + annual[cluster]

ax_year.set_title("Annual counts by cluster", color=text, loc="left")
ax_year.set_ylabel("Earthquake count", color=muted)
ax_year.set_axisbelow(True)
ax_year.grid(axis="y", color=grid, linewidth=0.6)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
output_file = FIGURES_DIR / "earthquake_kmeans_visualization.png"
fig.savefig(output_file, dpi=200, facecolor=background)
plt.close(fig)

print(f"Saved: {output_file}")
