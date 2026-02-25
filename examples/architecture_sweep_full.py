import numpy as np
import csv
import argparse
import os

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.coverage.grid import compute_grid_coverage
from sat_sim.coverage.grid_gap import compute_grid_max_gap


# -------------------------------------------------
# ROI helper
# -------------------------------------------------
def parse_roi(roi_str):
    """
    Parse ROI no formato:
      point:lat,lon
    """
    kind, values = roi_str.split(":")
    if kind != "point":
        raise ValueError("Somente ROI do tipo 'point' é suportada neste passo")

    lat, lon = map(float, values.split(","))
    return {
        "type": "point",
        "lat": lat,
        "lon": lon
    }


def worst_gap_in_roi(max_gap_map, lat_grid, lon_grid, roi):
    """
    Retorna o worst gap (min) na ROI definida.
    """
    if roi["type"] == "point":
        lat0 = roi["lat"]
        lon0 = roi["lon"]

        i = np.argmin(np.abs(lat_grid - lat0))
        j = np.argmin(np.abs(lon_grid - lon0))

        return max_gap_map[i, j]

    else:
        raise ValueError("ROI type não suportado neste passo")


def run_sweep(
    N_max,
    altitude_km,
    inclination_deg,
    roi
):
    # -------------------------------
    # Configurações globais
    # -------------------------------
    timeline = TimeArray(
        0.0,
        24 * 3600,
        60.0
    )

    min_elev = 0.0 * DEG2RAD

    lat_grid = np.arange(-90, 91, 10)
    lon_grid = np.arange(-180, 181, 10)

    total_minutes = (timeline.times[-1] + timeline.dt) / 60.0

    results = []

    altitude = R_EARTH + altitude_km * 1000.0
    inclination = inclination_deg * DEG2RAD

    # -------------------------------
    # Varredura de arquiteturas
    # -------------------------------
    for n_planes in range(1, N_max + 1):
        for sats_per_plane in range(1, N_max + 1):
            total_sats = n_planes * sats_per_plane
            if total_sats > N_max:
                continue

            print(f"Rodando arquitetura {n_planes}×{sats_per_plane} ({total_sats} sats)")

            constellation_coe = generate_constellation(
                altitude=altitude,
                inclination=inclination,
                n_planes=n_planes,
                sats_per_plane=sats_per_plane
            )

            constellation = [coe_to_rv(coe) for coe in constellation_coe]

            # -------------------------------
            # Cobertura
            # -------------------------------
            coverage = compute_grid_coverage(
                constellation=constellation,
                timeline=timeline,
                propagate_fn=lambda r0, v0, tl: propagate_orbit(
                    r0, v0, tl, use_j2=True
                ),
                min_elevation_rad=min_elev,
                lat_grid_deg=lat_grid,
                lon_grid_deg=lon_grid
            )

            coverage_min = coverage * total_minutes

            mean_cov = np.mean(coverage_min)
            min_cov = np.min(coverage_min)

            # -------------------------------
            # Gap máximo
            # -------------------------------
            max_gap = compute_grid_max_gap(
                constellation=constellation,
                timeline=timeline,
                propagate_fn=lambda r0, v0, tl: propagate_orbit(
                    r0, v0, tl, use_j2=True
                ),
                min_elevation_rad=min_elev,
                lat_grid_deg=lat_grid,
                lon_grid_deg=lon_grid
            )

            max_gap_min = max_gap / 60.0

            # -------------------------------
            # Critério primário (ROI)
            # -------------------------------
            worst_gap_roi = worst_gap_in_roi(
                max_gap_min,
                lat_grid,
                lon_grid,
                roi
            )

            results.append({
                "n_planes": n_planes,
                "sats_per_plane": sats_per_plane,
                "total_sats": total_sats,
                "worst_gap_roi_min": worst_gap_roi,
                "mean_coverage_min": mean_cov,
                "min_coverage_min": min_cov,
            })

    # -------------------------------
    # Ranking
    # -------------------------------
    results.sort(
        key=lambda r: (
            r["worst_gap_roi_min"],
            -r["mean_coverage_min"]
        )
    )

    # -------------------------------
    # CSV
    # -------------------------------
    os.makedirs("results", exist_ok=True)
    output_path = os.path.join(
        "results",
        "architecture_sweep_roi_results.csv"
    )

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResultados salvos em: {output_path}")
   
    # -------------------------------
    # Resumo
    # -------------------------------
    print("\nRanking final (ROI):")
    for r in results:
        print(
            f'{r["n_planes"]}×{r["sats_per_plane"]} | '
            f'{r["total_sats"]:2d} sats | '
            f'gap ROI = {r["worst_gap_roi_min"]:6.1f} min | '
            f'mean cov = {r["mean_coverage_min"]:6.1f} min'
        )

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Architecture sweep (ROI-based)"
    )

    parser.add_argument(
        "--n-max",
        type=int,
        default=1,
        help="Número máximo total de satélites (default: 1)"
    )

    parser.add_argument(
        "--altitude",
        type=float,
        default=550.0,
        help="Altitude orbital [km] (default: 550)"
    )

    parser.add_argument(
        "--inclination",
        type=float,
        default=98.0,
        help="Inclinação orbital [deg] (default: 98)"
    )

    parser.add_argument(
        "--roi",
        type=str,
        default="point:57.02868,9.94350",
        help="ROI no formato point:lat,lon (default: Sternula)"
    )

    args = parser.parse_args()

    roi = parse_roi(args.roi)

    run_sweep(
        N_max=args.n_max,
        altitude_km=args.altitude,
        inclination_deg=args.inclination,
        roi=roi
    )


if __name__ == "__main__":
    main()
