import argparse
import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.intervals import (
    compute_access_intervals,
    max_gap,
    revisit_times
)
from sat_sim.access.vdes_access import is_vdes_sat_uplink_available


def main():

    parser = argparse.ArgumentParser(
        description="VDES-SAT Local Availability"
    )

    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--duration", type=float, default=24.0)
    parser.add_argument("--dt", type=float, default=30.0)
    parser.add_argument("--altitude", type=float, default=550.0)
    parser.add_argument("--inclination", type=float, default=98.0)
    parser.add_argument("--n-planes", type=int, default=1)
    parser.add_argument("--sats-per-plane", type=int, default=1)

    args = parser.parse_args()

    station = GroundStation(
        lat_deg=args.lat,
        lon_deg=args.lon
    )

    timeline = TimeArray(
        0.0,
        args.duration * 3600.0,
        args.dt
    )

    constellation_coe = generate_constellation(
        altitude=R_EARTH + args.altitude * 1000.0,
        inclination=args.inclination * DEG2RAD,
        n_planes=args.n_planes,
        sats_per_plane=args.sats_per_plane
    )

    constellation = [coe_to_rv(coe) for coe in constellation_coe]

    # Propagar
    propagated = []
    for r0, v0 in constellation:
        rs, _ = propagate_orbit(r0, v0, timeline, use_j2=True)
        propagated.append(rs)

    closed_times = []

    for k, t in enumerate(timeline.times):

        closed_any = False

        for sat_idx, rs in enumerate(propagated):

            r_eci = rs[k]
            r_ecef = eci_to_ecef(r_eci, t)

            res = is_vdes_sat_uplink_available(
                r_sat_eci=r_eci,
                r_sat_ecef=r_ecef,
                station=station
            )

            if res.get("is_closed", False):
                closed_any = True
                break

        if closed_any:
            closed_times.append(t)

    availability = 100.0 * len(closed_times) / len(timeline.times)

    intervals = compute_access_intervals(closed_times, timeline.dt)

    if intervals:
        worst_gap = max_gap(intervals, 0.0, timeline.times[-1] + timeline.dt)
        revisits = revisit_times(intervals)
        mean_revisit = np.mean(revisits) if revisits else 0.0
    else:
        worst_gap = timeline.times[-1]
        mean_revisit = 0.0

    print("\n--- RESULTADO ---")
    print(f"Disponibilidade: {availability:.2f} %")
    print(f"Gap máximo: {worst_gap/60:.1f} min")
    print(f"Revisit médio: {mean_revisit/60:.1f} min")
    print("-----------------\n")


if __name__ == "__main__":
    main()
