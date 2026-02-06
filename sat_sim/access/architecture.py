import numpy as np

from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible
from sat_sim.access.intervals import (
    compute_access_intervals,
    max_gap,
    revisit_times
)
from sat_sim.access.constellation_access import aggregate_constellation_access


def evaluate_architecture(
    *,
    station,
    altitude,
    inclination,
    n_planes,
    sats_per_plane,
    timeline,
    min_elevation_rad,
    use_j2=True
):
    """
    Avalia uma arquitetura de constelação e retorna métricas globais.
    """

    constellation = generate_constellation(
        altitude=altitude,
        inclination=inclination,
        n_planes=n_planes,
        sats_per_plane=sats_per_plane
    )

    all_intervals = []

    for sat in constellation:
        r0, v0 = coe_to_rv(sat)

        rs, _ = propagate_orbit(
            r0,
            v0,
            timeline,
            use_j2=use_j2
        )

        visible_times = []

        for r_eci, t in zip(rs, timeline.times):
            r_ecef = eci_to_ecef(r_eci, t)
            if is_visible(r_ecef, station, min_elevation_rad):
                visible_times.append(t)

        intervals = compute_access_intervals(
            visible_times,
            timeline.dt
        )

        all_intervals.append(intervals)

    agg_intervals = aggregate_constellation_access(all_intervals)

    t_end = timeline.times[-1] + timeline.dt

    gap = max_gap(agg_intervals, 0.0, t_end)

    revisits = revisit_times(agg_intervals)
    mean_revisit = np.mean(revisits) if revisits else np.inf

    return {
        "n_planes": n_planes,
        "sats_per_plane": sats_per_plane,
        "total_sats": n_planes * sats_per_plane,
        "max_gap_s": gap,
        "mean_revisit_s": mean_revisit,
        "n_accesses": len(agg_intervals),
    }
