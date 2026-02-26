import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible
from sat_sim.access.intervals import (
    compute_access_intervals,
    max_gap,
    revisit_times,
)


def run_sweep_local_geom_analysis(
    station_lat_deg,
    station_lon_deg,
    altitude_km,
    inclination_deg,
    duration_h,
    dt_s,
    min_elev_deg,
    n_max,
):
    """
    Varre arquiteturas até n_max satélites e avalia desempenho geométrico.

    Retorna lista de dicionários:
        {
            "n_planes": int,
            "sats_per_plane": int,
            "total_sats": int,
            "worst_gap_min": float,
            "availability_percent": float,
            "mean_revisit_min": float,
            "mean_pass_duration_min": float,
            "n_passes": int,
        }
    """

    station = GroundStation(
        lat_deg=station_lat_deg,
        lon_deg=station_lon_deg
    )

    timeline = TimeArray(
        0.0,
        duration_h * 3600.0,
        dt_s
    )

    min_elev_rad = min_elev_deg * DEG2RAD

    results = []

    for n_planes in range(1, n_max + 1):
        for sats_per_plane in range(1, n_max + 1):

            total_sats = n_planes * sats_per_plane
            if total_sats > n_max:
                continue

            constellation_coe = generate_constellation(
                altitude=R_EARTH + altitude_km * 1000.0,
                inclination=inclination_deg * DEG2RAD,
                n_planes=n_planes,
                sats_per_plane=sats_per_plane,
            )

            constellation = [
                coe_to_rv(coe) for coe in constellation_coe
            ]

            # Propagação de todos satélites
            propagated = []
            for r0, v0 in constellation:
                rs, _ = propagate_orbit(
                    r0,
                    v0,
                    timeline,
                    use_j2=True
                )
                propagated.append(rs)

            visible_times = []

            # Avaliação geométrica agregada
            for k, t in enumerate(timeline.times):

                visible_any = False

                for rs in propagated:
                    r_eci = rs[k]
                    r_ecef = eci_to_ecef(r_eci, t)

                    if is_visible(r_ecef, station, min_elev_rad):
                        visible_any = True
                        break

                if visible_any:
                    visible_times.append(t)

            availability = 100.0 * len(visible_times) / len(timeline.times)

            intervals = compute_access_intervals(
                visible_times,
                timeline.dt
            )

            if intervals:
                worst_gap_s = max_gap(
                    intervals,
                    0.0,
                    timeline.times[-1] + timeline.dt
                )

                revisits = revisit_times(intervals)
                mean_revisit_s = np.mean(revisits) if revisits else 0.0

                durations = [
                    (t1 - t0) for (t0, t1) in intervals
                ]
                mean_pass_duration_s = (
                    np.mean(durations) if durations else 0.0
                )

                n_passes = len(intervals)

            else:
                worst_gap_s = timeline.times[-1]
                mean_revisit_s = 0.0
                mean_pass_duration_s = 0.0
                n_passes = 0

            results.append({
                "n_planes": n_planes,
                "sats_per_plane": sats_per_plane,
                "total_sats": total_sats,
                "worst_gap_min": worst_gap_s / 60.0,
                "availability_percent": availability,
                "mean_revisit_min": mean_revisit_s / 60.0,
                "mean_pass_duration_min": mean_pass_duration_s / 60.0,
                "n_passes": n_passes,
            })

    return results
