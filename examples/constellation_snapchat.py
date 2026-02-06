import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.frames.geo import ecef_to_latlon


def main():
    # -------------------------------
    # Constelação
    # -------------------------------
    n_planes = 4
    sats_per_plane = 3

    constellation_coe = generate_constellation(
        altitude=R_EARTH + 550e3,
        inclination=98.0 * DEG2RAD,
        n_planes=n_planes,
        sats_per_plane=sats_per_plane
    )

    constellation = [coe_to_rv(coe) for coe in constellation_coe]

    # -------------------------------
    # Tempo (snapshot)
    # -------------------------------
    t0 = 0.0
    timeline = TimeArray(t0, t0, 1.0)

    lats = []
    lons = []

    for r0, v0 in constellation:
        rs, _ = propagate_orbit(
            r0,
            v0,
            timeline,
            use_j2=False
        )

        r_ecef = eci_to_ecef(rs[0], t0)
        lat, lon = ecef_to_latlon(r_ecef)

        lats.append(lat)
        lons.append(lon)

    # -------------------------------
    # Plot com Cartopy
    # -------------------------------
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_global()

    # Continentes e costas
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="white")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)

    # Grade
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.5
    )
    gl.top_labels = False
    gl.right_labels = False

    # Satélites
    ax.scatter(
        lons,
        lats,
        color="red",
        s=50,
        transform=ccrs.PlateCarree(),
        label="Satélites"
    )

    ax.set_title(
        f"Snapshot da constelação — {n_planes}×{sats_per_plane} (t = 0)",
        fontsize=12
    )

    ax.legend(loc="lower left")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
