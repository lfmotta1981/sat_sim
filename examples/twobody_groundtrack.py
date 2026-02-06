import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.elements import ClassicalOrbitalElements, coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef, ecef_to_latlon
from sat_sim.visualization.groundtrack import plot_groundtrack


def main():
    coe = ClassicalOrbitalElements(
        a=R_EARTH + 550e3,
        e=0.001,
        i=98.0 * DEG2RAD,
        raan=0.0,
        argp=0.0,
        nu=0.0
    )

    r0, v0 = coe_to_rv(coe)

    timeline = TimeArray(0.0, 24 * 3600, 30.0)

    rs, _ = propagate_orbit(r0, v0, timeline, use_j2=False)

    lats, lons = [], []

    for r_eci, t in zip(rs, timeline.times):
        r_ecef = eci_to_ecef(r_eci, t)
        lat, lon = ecef_to_latlon(r_ecef)
        lats.append(lat)
        lons.append(lon)

    plot_groundtrack(
        lats,
        lons,
        title="Ground Track — Two-Body Propagation"
    )


if __name__ == "__main__":
    main()
