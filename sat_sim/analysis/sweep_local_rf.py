import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.analysis.local_rf_metrics import compute_local_rf_metrics


def run_sweep_local_rf_analysis(
    station_lat_deg,
    station_lon_deg,
    altitude_km,
    inclination_deg,
    duration_h,
    dt_s,
    n_max,
    max_gap_requirement_min=None,
):
    """
    Varre arquiteturas até n_max satélites.
    Retorna lista de dicionários com métricas.
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
                sats_per_plane=sats_per_plane
            )

            constellation = [
                coe_to_rv(coe) for coe in constellation_coe
            ]

            metrics = compute_local_rf_metrics(
                constellation=constellation,
                timeline=timeline,
                station=station,
                propagate_fn=lambda r0, v0, tl: propagate_orbit(
                    r0, v0, tl, use_j2=True
                ),
            )

            worst_gap_min = metrics["worst_gap_s"] / 60.0
            availability_pct = metrics["availability_percent"]

            if max_gap_requirement_min is not None:
                if worst_gap_min > max_gap_requirement_min:
                    continue

            results.append({
                "n_planes": n_planes,
                "sats_per_plane": sats_per_plane,
                "total_sats": total_sats,
                "worst_gap_min": worst_gap_min,
                "availability_percent": availability_pct,
            })

    return results
