# examples/single_access_vdes.py

import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.elements import ClassicalOrbitalElements, coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.vdes_access import is_vdes_sat_uplink_available


def main():
    station = GroundStation(
        lat_deg=79.0,
        lon_deg=17.5
    )

    coe = ClassicalOrbitalElements(
        a=R_EARTH + 550e3,
        e=0.0,
        i=98.0 * DEG2RAD,
        raan=0.0,
        argp=0.0,
        nu=0.0
    )

    r0, v0 = coe_to_rv(coe)

    timeline = TimeArray(
        0.0,
        24 * 3600,
        30.0
    )

    rs, _ = propagate_orbit(
        r0,
        v0,
        timeline,
        use_j2=True
    )

    visible_times = []

    for r_eci, t in zip(rs, timeline.times):
        r_ecef = eci_to_ecef(r_eci, t)

        res = is_vdes_sat_uplink_available(
            r_sat_eci=r_eci,
            r_sat_ecef=r_ecef,
            station=station
        )

        if res.get("is_closed", False):
            visible_times.append(t)

    print(f"Instantes com uplink fechado: {len(visible_times)}")

    if visible_times:
        duration_min = len(visible_times) * timeline.dt / 60.0
        print(f"Duração total ≈ {duration_min:.1f} min")
        print(f"Primeiro acesso em t = {visible_times[0]/60:.1f} min")
    else:
        print("Nenhum acesso VDES-SAT uplink nesta janela.")


if __name__ == "__main__":
    main()
