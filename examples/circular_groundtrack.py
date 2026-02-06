import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.circular import propagate_circular_orbit
from sat_sim.frames.transforms import eci_to_ecef, ecef_to_latlon
from sat_sim.visualization.groundtrack import plot_groundtrack


def main():
    altitude = 550e3  # 550 km
    a = R_EARTH + altitude

    inclination = 98.0 * DEG2RAD
    raan = 0.0 * DEG2RAD

    timeline = TimeArray(
        t0=0.0,
        tf=24 * 3600,
        dt=30.0
    )

    lats = []
    lons = []

    for t in timeline.times:
        r_eci = propagate_circular_orbit(a, inclination, raan, t)
        r_ecef = eci_to_ecef(r_eci, t)
        lat, lon = ecef_to_latlon(r_ecef)

        lats.append(lat)
        lons.append(lon)

    plot_groundtrack(
        lats,
        lons,
        title="Ground Track — Circular Orbit (550 km, i=98°)"
    )


if __name__ == "__main__":
    main()
