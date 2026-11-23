from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# Load the earthquake table from the same folder as this script.
project_dir = Path(__file__).resolve().parent
data_path = project_dir / "earthquake_country.csv"

quakes = pd.read_csv(data_path)

print("Loaded file:", data_path)
print("Earthquake records:", len(quakes))
# Conclusion: The earthquake records are available for mapping.


# Create Boolean masks for the three depth intervals.
shallow = quakes["Depth"] < 70

intermediate = (
    (quakes["Depth"] >= 70)
    & (quakes["Depth"] < 300)
)

deep = quakes["Depth"] >= 300

print("Shallow records:", shallow.sum())
print("Intermediate records:", intermediate.sum())
print("Deep records:", deep.sum())
print(
    "All records classified:",
    shallow.sum() + intermediate.sum() + deep.sum() == len(quakes)
)
# Conclusion: Each record is assigned to one of the three depth groups.


# Create a Pacific-centered world map with a dark background.
fig = plt.figure(
    figsize=(16, 8),
    facecolor="#091521"
)

ax = plt.axes(
    projection=ccrs.PlateCarree(central_longitude=180)
)
ax.set_global()
ax.set_facecolor("#102331")

ax.add_feature(
    cfeature.OCEAN.with_scale("110m"),
    facecolor="#102331",
    zorder=0
)

ax.add_feature(
    cfeature.LAND.with_scale("110m"),
    facecolor="#2B3D49",
    edgecolor="none",
    zorder=1
)

ax.coastlines(
    resolution="110m",
    color="#7895A3",
    linewidth=0.5,
    zorder=2
)

ax.gridlines(
    color="#496676",
    linewidth=0.4,
    alpha=0.5,
    zorder=2
)
# Conclusion: The world map is centered on the Pacific Ocean.


# Plot earthquake epicenters using a different color for each depth group.
ax.scatter(
    quakes.loc[shallow, "Longitude"],
    quakes.loc[shallow, "Latitude"],
    transform=ccrs.PlateCarree(),
    s=2,
    color="#FFC080",
    alpha=0.75,
    edgecolors="none",
    label="<70 km",
    zorder=3
)

ax.scatter(
    quakes.loc[intermediate, "Longitude"],
    quakes.loc[intermediate, "Latitude"],
    transform=ccrs.PlateCarree(),
    s=2,
    color="#65D7DA",
    alpha=0.75,
    edgecolors="none",
    label="70-<300 km",
    zorder=4
)

ax.scatter(
    quakes.loc[deep, "Longitude"],
    quakes.loc[deep, "Latitude"],
    transform=ccrs.PlateCarree(),
    s=2,
    color="#B494FF",
    alpha=0.75,
    edgecolors="none",
    label=">=300 km",
    zorder=5
)
# Conclusion: Epicenter colors represent the three depth intervals.


# Add the title and legend, then save and display the figure.
ax.set_title(
    "Global Earthquake Epicenters | 1965-2016",
    color="#E6EDF2",
    fontsize=20,
    pad=20
)

ax.text(
    1,
    1.02,
    f"{len(quakes):,} EVENTS",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    color="#A8BDC9",
    fontsize=11
)

ax.legend(
    loc="upper left",
    bbox_to_anchor=(0, -0.04),
    ncol=3,
    frameon=False,
    labelcolor="#E6EDF2",
    fontsize=12,
    markerscale=4
)

fig.subplots_adjust(
    left=0.03,
    right=0.97,
    top=0.90,
    bottom=0.14
)

output_path = project_dir / "global_earthquake_distribution.png"

fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    facecolor=fig.get_facecolor()
)

print("Saved figure:", output_path)

# Conclusion: The combined epicenter map is saved as a PNG.


# Compare the three depth groups and all events in a shared 2-by-2 map layout.
comparison_fig, comparison_axes = plt.subplots(
    2,
    2,
    figsize=(18, 11),
    subplot_kw={"projection": ccrs.PlateCarree(central_longitude=180)},
    facecolor="#091521"
)

comparison_fig.subplots_adjust(
    left=0.035,
    right=0.965,
    top=0.85,
    bottom=0.13,
    wspace=0.08,
    hspace=0.22
)

for panel in comparison_axes.flat:
    panel.set_global()
    panel.set_facecolor("#102331")
    panel.add_feature(
        cfeature.OCEAN.with_scale("110m"),
        facecolor="#102331",
        zorder=0
    )
    panel.add_feature(
        cfeature.LAND.with_scale("110m"),
        facecolor="#2B3D49",
        edgecolor="none",
        zorder=1
    )
    panel.coastlines(
        resolution="110m",
        color="#7895A3",
        linewidth=0.4,
        zorder=2
    )
    panel.gridlines(
        color="#496676",
        linewidth=0.35,
        alpha=0.5,
        zorder=2
    )
    panel.spines["geo"].set_edgecolor("#496676")

panel_groups = [
    (shallow, "#FFC080", "Shallow | <70 km", "<70 km"),
    (intermediate, "#65D7DA", "Intermediate | 70-<300 km", "70-<300 km"),
    (deep, "#B494FF", "Deep | >=300 km", ">=300 km")
]

combined_panel = comparison_axes[1, 1]

for group_index, (mask, color, title, label) in enumerate(panel_groups):
    group_panel = comparison_axes.flat[group_index]
    group_panel.scatter(
        quakes.loc[mask, "Longitude"],
        quakes.loc[mask, "Latitude"],
        transform=ccrs.PlateCarree(),
        s=2,
        color=color,
        alpha=0.8,
        edgecolors="none",
        zorder=3
    )
    group_panel.set_title(
        title,
        loc="left",
        color="#E6EDF2",
        fontsize=13,
        pad=12
    )
    group_panel.text(
        1,
        1.025,
        f"{mask.sum():,} events",
        transform=group_panel.transAxes,
        ha="right",
        va="bottom",
        color="#A8BDC9",
        fontsize=10
    )
    combined_panel.scatter(
        quakes.loc[mask, "Longitude"],
        quakes.loc[mask, "Latitude"],
        transform=ccrs.PlateCarree(),
        s=2,
        color=color,
        alpha=0.8,
        edgecolors="none",
        label=label,
        zorder=3 + group_index
    )

combined_panel.set_title(
    "All earthquakes",
    loc="left",
    color="#E6EDF2",
    fontsize=13,
    pad=12
)
combined_panel.text(
    1,
    1.025,
    f"{len(quakes):,} events",
    transform=combined_panel.transAxes,
    ha="right",
    va="bottom",
    color="#A8BDC9",
    fontsize=10
)

comparison_fig.suptitle(
    "Global Earthquake Epicenters by Depth",
    color="#E6EDF2",
    fontsize=24,
    y=0.965
)
comparison_fig.text(
    0.5,
    0.915,
    "1965-2016 | Pacific-centered maps | Magnitude >=5.5",
    ha="center",
    color="#A8BDC9",
    fontsize=12
)

legend_handles, legend_labels = combined_panel.get_legend_handles_labels()
comparison_fig.legend(
    legend_handles,
    legend_labels,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.045),
    ncol=3,
    frameon=False,
    labelcolor="#E6EDF2",
    fontsize=12,
    markerscale=4,
    columnspacing=3
)
comparison_fig.text(
    0.5,
    0.025,
    "Data: 07earthquake.csv | Basemap: Natural Earth | Depth groups include flagged source values",
    ha="center",
    color="#A8BDC9",
    fontsize=9
)
# Conclusion: The panels compare shallow, intermediate, deep and combined epicenters on identical maps.


# Save the four-panel comparison as an additional high-resolution PNG and display both figures.
comparison_output_path = project_dir / "global_earthquake_depth_panels.png"
comparison_fig.savefig(
    comparison_output_path,
    dpi=300,
    bbox_inches="tight",
    facecolor=comparison_fig.get_facecolor()
)
print("Saved four-panel figure:", comparison_output_path)

plt.show()
# Conclusion: Both the original combined map and the new four-panel comparison are generated.
