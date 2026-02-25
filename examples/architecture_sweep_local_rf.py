import argparse
import numpy as np
import csv
import os

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.intervals import compute_access_intervals, max_gap
from sat_sim.access.vdes_access import is_vdes_sat_uplink_available


# -------------------------------------------------
# Default station (sternula)
# -------------------------------------------------
DEFAULT_LAT = 57.02868
DEFAULT_LON = 9.94350


# -------------------------------------------------
# RF local metrics
# -------------------------------------------------
def compute_local_rf_metrics(
    station,
    altitude,
    inclination,
    n_planes,
    sats_per_plane,
    timeline,
):
    constellation_coe = generate_constellation(
        altitude=altitude,
        inclination=inclination,
        n_planes=n_planes,
        sats_per_plane=sats_per_plane,
    )

    constellation = [coe_to_rv(coe) for coe in constellation_coe]

    visible_times = []

    for r0, v0 in constellation:

        rs, _ = propagate_orbit(
            r0,
            v0,
            timeline,
            use_j2=True,
        )

        for r_eci, t in zip(rs, timeline.times):

            r_ecef = eci_to_ecef(r_eci, t)

            res = is_vdes_sat_uplink_available(
                r_sat_eci=r_eci,
                r_sat_ecef=r_ecef,
                station=station,
            )

            if res.get("is_closed", False):
                visible_times.append(t)

    visible_times = sorted(set(visible_times))

    intervals = compute_access_intervals(
        visible_times,
        timeline.dt,
    )

    total_time = timeline.times[-1] + timeline.dt

    availability = (
        len(visible_times) * timeline.dt / total_time
    )

    gap = max_gap(
        intervals,
        0.0,
        total_time,
    )

    return {
        "availability_percent": availability * 100.0,
        "worst_gap_min": gap / 60.0,
    }


# -------------------------------------------------
# CSV writer (with metadata header)
# -------------------------------------------------
def save_csv(results, filename, simulation_metadata):

    os.makedirs("results", exist_ok=True)
    filepath = os.path.join("results", filename)

    with open(filepath, "w", newline="") as f:

        f.write("# Local RF Architecture Sweep\n")
        for key, value in simulation_metadata.items():
            f.write(f"# {key}: {value}\n")
        f.write("#\n")

        writer = csv.DictWriter(
            f,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nCSV salvo em: {filepath}")


# -------------------------------------------------
# Sweep
# -------------------------------------------------
def run_sweep_local_rf(
    n_max,
    lat,
    lon,
    altitude,
    inclination,
    timeline,
    max_gap_requirement=None,
    min_availability_requirement=None,
    output_filename="architecture_sweep_local_rf.csv",
):

    station = GroundStation(
        lat_deg=lat,
        lon_deg=lon,
    )

    results = []

    for n_planes in range(1, n_max + 1):
        for sats_per_plane in range(1, n_max + 1):

            total_sats = n_planes * sats_per_plane

            if total_sats > n_max:
                continue

            print(f"Rodando {n_planes}×{sats_per_plane} ({total_sats} sats)")

            metrics = compute_local_rf_metrics(
                station=station,
                altitude=altitude,
                inclination=inclination,
                n_planes=n_planes,
                sats_per_plane=sats_per_plane,
                timeline=timeline,
            )

            results.append({
                "n_planes": n_planes,
                "sats_per_plane": sats_per_plane,
                "total_sats": total_sats,
                "availability_percent": metrics["availability_percent"],
                "worst_gap_min": metrics["worst_gap_min"],
            })

    results.sort(key=lambda r: r["worst_gap_min"])

    metadata = {
        "Latitude [deg]": lat,
        "Longitude [deg]": lon,
        "Altitude [km]": altitude / 1000.0,
        "Inclination [deg]": inclination / DEG2RAD,
        "Duration [h]": timeline.times[-1] / 3600.0,
        "Time step [s]": timeline.dt,
        "N_max": n_max,
        "Max gap requirement [min]": max_gap_requirement,
        "Min availability requirement [%]": min_availability_requirement,
    }

    save_csv(results, output_filename, metadata)

    # -------------------------------------------------
    # Filtragem por requisitos
    # -------------------------------------------------
    if max_gap_requirement is not None or min_availability_requirement is not None:

        filtered = results

        if max_gap_requirement is not None:
            filtered = [
                r for r in filtered
                if r["worst_gap_min"] <= max_gap_requirement
            ]

        if min_availability_requirement is not None:
            filtered = [
                r for r in filtered
                if r["availability_percent"] >= min_availability_requirement
            ]

        if filtered:
            filtered_filename = output_filename.replace(
                ".csv",
                "_filtered.csv"
            )
            save_csv(filtered, filtered_filename, metadata)

            print("\nArquiteturas que atendem aos requisitos:\n")
            for r in filtered:
                print(
                    f"{r['n_planes']}×{r['sats_per_plane']} | "
                    f"{r['total_sats']} sats | "
                    f"gap = {r['worst_gap_min']:.1f} min | "
                    f"availability = {r['availability_percent']:.1f}%"
                )
        else:
            print("\nNenhuma arquitetura atende aos requisitos.")


# -------------------------------------------------
# CLI
# -------------------------------------------------
def main():

    parser = argparse.ArgumentParser(
        description="Local RF architecture sweep (VDES uplink)"
    )

    parser.add_argument("--lat", type=float, default=DEFAULT_LAT)
    parser.add_argument("--lon", type=float, default=DEFAULT_LON)

    parser.add_argument("--n-max", type=int, default=8)

    parser.add_argument("--altitude", type=float, default=550.0)
    parser.add_argument("--inclination", type=float, default=98.0)

    parser.add_argument("--duration", type=float, default=24.0)
    parser.add_argument("--dt", type=float, default=30.0)

    parser.add_argument("--max-gap", type=float, default=None)
    parser.add_argument("--min-availability", type=float, default=None)

    parser.add_argument(
        "--output",
        type=str,
        default="architecture_sweep_local_rf.csv",
        help="Nome do CSV de saída"
    )

    args = parser.parse_args()

    timeline = TimeArray(
        0.0,
        args.duration * 3600.0,
        args.dt,
    )

    altitude = R_EARTH + args.altitude * 1000.0
    inclination = args.inclination * DEG2RAD

    run_sweep_local_rf(
        n_max=args.n_max,
        lat=args.lat,
        lon=args.lon,
        altitude=altitude,
        inclination=inclination,
        timeline=timeline,
        max_gap_requirement=args.max_gap,
        min_availability_requirement=args.min_availability,
        output_filename=args.output,
    )


if __name__ == "__main__":
    main()
