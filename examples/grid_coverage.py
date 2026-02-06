import numpy as np
import matplotlib.pyplot as plt

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.coverage.grid import compute_grid_coverage


def main():
    # -------------------------------
    # Constelação
    # -------------------------------
    n_planes = 1
    sats_per_plane = 1

    constellation_coe = generate_constellation(
        altitude=R_EARTH + 550e3,
        inclination=98.0 * DEG2RAD,
        n_planes=n_planes,
        sats_per_plane=sats_per_plane
    )

    constellation = [
        coe_to_rv(coe) for coe in constellation_coe
    ]

    # -------------------------------
    # Tempo
    # -------------------------------
    timeline = TimeArray(
        0.0,
        24 * 3600,
        60.0
    )

    min_elev = 10.0 * DEG2RAD

    # -------------------------------
    # Grid
    # -------------------------------
    lat_grid = np.arange(-90, 91, 10)
    lon_grid = np.arange(-180, 181, 10)

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

    # Converter para minutos
    total_minutes = (timeline.times[-1] + timeline.dt) / 60.0
    coverage_minutes = coverage * total_minutes

    # -------------------------------
    # Plot — MAPA FUNCIONAL LEVE
    # -------------------------------
    plt.figure(figsize=(11, 5))

    plt.imshow(
        coverage_minutes,
        extent=[-180, 180, -90, 90],
        origin="lower",
        aspect="auto",
        cmap="RdYlGn",
        vmin=0,
        vmax=total_minutes,
        alpha=0.9
    )

    cbar = plt.colorbar()
    cbar.set_label("Cobertura [min em 24h]")

    # -------------------------------
    # Grade geográfica
    # -------------------------------
    for lon in range(-180, 181, 30):
        plt.axvline(lon, color="black", linewidth=0.3, alpha=0.4)

    for lat in range(-90, 91, 30):
        plt.axhline(lat, color="black", linewidth=0.3, alpha=0.4)

    # -------------------------------
    # Linhas físicas de referência
    # -------------------------------
    plt.axhline(0, color="black", linewidth=1.0, alpha=0.7)
    plt.text(-175, 2, "Equador", fontsize=8)

    plt.axhline(66.5, color="black", linewidth=0.8, alpha=0.7)
    plt.axhline(-66.5, color="black", linewidth=0.8, alpha=0.7)
    plt.text(-175, 68, "Círculo Polar N", fontsize=8)
    plt.text(-175, -64, "Círculo Polar S", fontsize=8)

    # -------------------------------
    # Labels
    # -------------------------------
    plt.xlabel("Longitude [deg]")
    plt.ylabel("Latitude [deg]")
    plt.title(
        f"Cobertura temporal — constelação {n_planes}×{sats_per_plane} (SSO)\n"
        "(cada célula = estação virtual)"
    )

    plt.xlim(-180, 180)
    plt.ylim(-90, 90)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
