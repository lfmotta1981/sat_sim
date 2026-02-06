import matplotlib.pyplot as plt

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.constellation import generate_constellation
from sat_sim.orbits.elements import coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible
from sat_sim.access.intervals import compute_access_intervals
from sat_sim.access.constellation_access import aggregate_constellation_access


def main():
    # -------------------------------
    # Configuração do cenário
    # -------------------------------
    station = GroundStation(
        lat_deg=79.0,
        lon_deg=17.5
    )

    timeline = TimeArray(
        0.0,
        24 * 3600,
        10.0
    )

    altitude = R_EARTH + 550e3
    inclination = 98.0 * DEG2RAD
    min_elev = 0.0 * DEG2RAD

    # Escolha da arquitetura (ex: 4x3 = 12 sats)
    constellation = generate_constellation(
        altitude=altitude,
        inclination=inclination,
        n_planes=4,
        sats_per_plane=3
    )

    # -------------------------------
    # Acessos por satélite
    # -------------------------------
    all_intervals = []

    for sat in constellation:
        r0, v0 = coe_to_rv(sat)

        rs, _ = propagate_orbit(
            r0,
            v0,
            timeline,
            use_j2=True
        )

        visible_times = []

        for r_eci, t in zip(rs, timeline.times):
            r_ecef = eci_to_ecef(r_eci, t)
            if is_visible(r_ecef, station, min_elev):
                visible_times.append(t)

        intervals = compute_access_intervals(
            visible_times,
            timeline.dt
        )

        all_intervals.append(intervals)

    # -------------------------------
    # Acesso agregado
    # -------------------------------
    agg_intervals = aggregate_constellation_access(all_intervals)

    # -------------------------------
    # Plot
    # -------------------------------
    fig, ax = plt.subplots(figsize=(10, 4))

    # Satélites individuais (cinza)
    y = 10
    for sat_intervals in all_intervals:
        for t0, t1 in sat_intervals:
            ax.broken_barh(
                [(t0 / 3600, (t1 - t0) / 3600)],
                (y, 0.8),
                facecolors="lightgray"
            )
        y += 1

    # Acesso agregado (azul)
    for t0, t1 in agg_intervals:
        ax.broken_barh(
            [(t0 / 3600, (t1 - t0) / 3600)],
            (0, 3),
            facecolors="tab:blue"
        )

    ax.set_xlabel("Tempo [h]")
    ax.set_yticks([1, 12])
    ax.set_yticklabels(["Constelação", "Satélites"])
    ax.set_title("Timeline de acesso — constelação 4×3 (SSO)")

    ax.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
