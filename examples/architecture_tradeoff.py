import csv
import argparse
import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.access.architecture import evaluate_architecture


# -------------------------------------------------
# Ground station catalog (default: sternula)
# -------------------------------------------------
STATION_CATALOG = {
    "sternula": (57.02868, 9.94350),
    "svalbard": (79.0, 17.5),
    "kiruna": (67.9, 21.1),
    "troll": (-72.0, 2.5),
    "alaska": (64.8, -147.5),
}


def build_station(args):
    if args.lat is not None and args.lon is not None:
        return GroundStation(lat_deg=args.lat, lon_deg=args.lon)

    if args.station:
        if args.station not in STATION_CATALOG:
            raise ValueError(f"Estação '{args.station}' não está no catálogo")
        lat, lon = STATION_CATALOG[args.station]
        return GroundStation(lat_deg=lat, lon_deg=lon)

    lat, lon = STATION_CATALOG["sternula"]
    return GroundStation(lat_deg=lat, lon_deg=lon)


def generate_configs_from_total(total_sats):
    """
    Gera arquiteturas (n_planes, sats_per_plane)
    tais que n_planes * sats_per_plane = total_sats
    """
    configs = []
    for n_planes in range(1, total_sats + 1):
        if total_sats % n_planes != 0:
            continue
        sats_per_plane = total_sats // n_planes
        configs.append((n_planes, sats_per_plane))
    return configs


def main():
    # -------------------------------
    # CLI
    # -------------------------------
    parser = argparse.ArgumentParser(
        description="Architecture trade-off (single ground station)"
    )

    parser.add_argument("--station", type=str)
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)

    parser.add_argument(
        "--altitude",
        type=float,
        default=550.0,
        help="Altitude orbital [km]"
    )

    parser.add_argument(
        "--inclination",
        type=float,
        default=98.0,
        help="Inclinação orbital [deg]"
    )

    parser.add_argument(
        "--min-elev",
        type=float,
        default=0.0,
        help="Elevação mínima [deg]"
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=24.0,
        help="Duração da simulação [h]"
    )

    parser.add_argument(
        "--dt",
        type=float,
        default=30.0,
        help="Passo temporal [s]"
    )

    parser.add_argument(
        "--total-sats",
        type=int,
        help="Número total de satélites (gera arquiteturas automaticamente)"
    )

    args = parser.parse_args()

    # -------------------------------
    # Estação
    # -------------------------------
    station = build_station(args)

    # -------------------------------
    # Tempo
    # -------------------------------
    timeline = TimeArray(
        0.0,
        args.duration * 3600.0,
        args.dt
    )

    # -------------------------------
    # Órbita
    # -------------------------------
    altitude = R_EARTH + args.altitude * 1000.0
    inclination = args.inclination * DEG2RAD
    min_elev = args.min_elev * DEG2RAD

    # -------------------------------
    # Arquiteturas
    # -------------------------------
    if args.total_sats:
        configs = generate_configs_from_total(args.total_sats)
        print(f"Avaliando arquiteturas com {args.total_sats} satélites")
    else:
        configs = [
            (1, 1),
        ]
        print("Avaliando arquiteturas default")

    results = []

    print(
        "Planes | Sats/Plane | Total | Max Gap (min) | Revisit (min)"
    )
    print("-" * 60)

    for n_planes, sats_per_plane in configs:
        result = evaluate_architecture(
            station=station,
            altitude=altitude,
            inclination=inclination,
            n_planes=n_planes,
            sats_per_plane=sats_per_plane,
            timeline=timeline,
            min_elevation_rad=min_elev,
        )

        max_gap_min = result["max_gap_s"] / 60.0
        revisit_min = result["mean_revisit_s"] / 60.0

        print(
            f"{n_planes:6d} | "
            f"{sats_per_plane:10d} | "
            f"{n_planes * sats_per_plane:5d} | "
            f"{max_gap_min:10.2f} | "
            f"{revisit_min:10.2f}"
        )

        results.append({
            "n_planes": n_planes,
            "sats_per_plane": sats_per_plane,
            "total_sats": n_planes * sats_per_plane,
            "max_gap_min": max_gap_min,
            "mean_revisit_min": revisit_min,
            "n_accesses": result["n_accesses"],
        })

    # -------------------------------
    # CSV
    # -------------------------------
    with open("architecture_tradeoff.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\nResultados salvos em: architecture_tradeoff.csv")


if __name__ == "__main__":
    main()
