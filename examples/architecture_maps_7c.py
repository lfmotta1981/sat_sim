import os
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.coverage.grid import compute_grid_coverage
from sat_sim.coverage.grid_gap import compute_grid_max_gap

ROI = {
    "type": "point",
    "lat": 79.0,
    "lon": 17.5
}

def draw_roi(ax, roi):
    if roi["type"] == "point":
        ax.scatter(
            roi["lon"],
            roi["lat"],
            color="blue",
            s=80,
            marker="x",
            transform=ccrs.PlateCarree()
        )

    elif roi["type"] == "lat_band":
        lat = roi["lat_min"]
        ax.axhspan(lat, 90, color="blue", alpha=0.15, transform=ccrs.PlateCarree())
        ax.axhspan(-90, -lat, color="blue", alpha=0.15, transform=ccrs.PlateCarree())

    elif roi["type"] == "box":
        lats = [roi["lat_min"], roi["lat_max"], roi["lat_max"], roi["lat_min"], roi["lat_min"]]
        lons = [roi["lon_min"], roi["lon_min"], roi["lon_max"], roi["lon_max"], roi["lon_min"]]
        ax.plot(lons, lats, color="blue", linewidth=2, transform=ccrs.PlateCarree())

def plot_coverage_map(
    coverage_min,
    lat_grid,
    lon_grid,
    roi,
    title,
    filename,
    vmax
):
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()

    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="white")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)

    im = ax.imshow(
        coverage_min,
        extent=[-180, 180, -90, 90],
        origin="lower",
        transform=ccrs.PlateCarree(),
        cmap="RdYlGn",
        vmin=0,
        vmax=vmax,
        alpha=0.9
    )

    plt.colorbar(im, ax=ax, label="Cobertura [min / 24h]")
    draw_roi(ax, roi)

    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def plot_gap_map(
    max_gap_min,
    lat_grid,
    lon_grid,
    roi,
    title,
    filename,
    vmax
):
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()

    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="white")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)

    im = ax.imshow(
        max_gap_min,
        extent=[-180, 180, -90, 90],
        origin="lower",
        transform=ccrs.PlateCarree(),
        cmap="RdYlGn_r",
        vmin=0,
        vmax=vmax,
        alpha=0.9
    )

    plt.colorbar(im, ax=ax, label="Gap máximo [min]")
    draw_roi(ax, roi)

    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def main():
    # -------------------------------
    # Ranking (copiado manualmente)
    # -------------------------------
    results = [
        {
            "n_planes": 2,
            "sats_per_plane": 2,
            "total_sats": 4,
            "worst_gap_roi_min": 35.0,
            "mean_coverage_min": 420.0,
            "min_coverage_min": 180.0
        },
        {
            "n_planes": 1,
            "sats_per_plane": 4,
            "total_sats": 4,
            "worst_gap_roi_min": 48.0,
            "mean_coverage_min": 310.0,
            "min_coverage_min": 120.0
        }
    ]

    top_n = 2
    output_dir = "results/maps"
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------
    # Configuração global
    # -------------------------------
    timeline = TimeArray(
        0.0,
        24 * 3600,
        60.0
    )

    lat_grid = np.arange(-90, 91, 10)
    lon_grid = np.arange(-180, 181, 10)

    min_elev = 10.0 * DEG2RAD
    total_minutes = (timeline.times[-1] + timeline.dt) / 60.0

    # -------------------------------
    # Loop nas Top N arquiteturas
    # -------------------------------
    for rank, arch in enumerate(results[:top_n], start=1):
        print(f"Gerando mapas para arquitetura {arch['n_planes']}×{arch['sats_per_plane']}")

        # Pasta da arquitetura
        folder = os.path.join(
            output_dir,
            f"rank_{rank:02d}_{arch['n_planes']}x{arch['sats_per_plane']}"
        )
        os.makedirs(folder, exist_ok=True)

        # -------------------------------
        # Constelação
        # -------------------------------
        constellation_coe = generate_constellation(
            altitude=R_EARTH + 550e3,
            inclination=98.0 * DEG2RAD,
            n_planes=arch["n_planes"],
            sats_per_plane=arch["sats_per_plane"]
        )

        constellation = [coe_to_rv(coe) for coe in constellation_coe]

        # -------------------------------
        # Cobertura
        # -------------------------------
        coverage = compute_grid_coverage(
            constellation=constellation,
            timeline=timeline,
            propagate_fn=lambda r0, v0, tl: propagate_orbit(
                r0, v0, tl, use_j2=True
            ),
            min_elevation_rad=min_elev,
            lat_grid_deg=lat_grid,
            lon_grid_deg=lon_grid
        )


        coverage_min = coverage * total_minutes

        plot_coverage_map(
            coverage_min,
            lat_grid,
            lon_grid,
            ROI,
            title=f"Cobertura — {arch['n_planes']}×{arch['sats_per_plane']}",
            filename=os.path.join(folder, "coverage.png"),
            vmax=total_minutes
        )

        # -------------------------------
        # Gap máximo
        # -------------------------------
        max_gap = compute_grid_max_gap(
            constellation=constellation,
            timeline=timeline,
            propagate_fn=lambda r0, v0, tl: propagate_orbit(
                r0, v0, tl, use_j2=True
            ),
            min_elevation_rad=min_elev,
            lat_grid_deg=lat_grid,
            lon_grid_deg=lon_grid
        )


        max_gap_min = max_gap / 60.0

        plot_gap_map(
            max_gap_min,
            lat_grid,
            lon_grid,
            ROI,
            title=f"Gap máximo — {arch['n_planes']}×{arch['sats_per_plane']}",
            filename=os.path.join(folder, "max_gap.png"),
            vmax=total_minutes
        )

if __name__ == "__main__":
    main()
