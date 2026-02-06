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
    # Estação
    # -------------------------------
    station = GroundStation(
        lat_deg=79.0,
        lon_deg=17.5
    )

    # -------------------------------
    # Constelação (exemplo)
    # -------------------------------
    constellation = generate_constellation(
        altitude=R_EARTH + 550e3,
        inclination=98.0 * DEG2RAD,
        n_planes=3,
        sats_per_plane=4
    )

    # -------------------------------
    # Janela temporal
    # -------------------------------
    timeline = TimeArray(
        0.0,
        24 * 3600,
        30.0
    )

    min_elev = 10.0 * DEG2RAD

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
    # Plot timeline
    # -------------------------------
    plt.figure(figsize=(10, 2))

    for (t0, t1) in agg_intervals:
        plt.hlines(
            y=1,
            xmin=t0 / 60.0,
            xmax=t1 / 60.0,
            linewidth=6
        )

    plt.yticks([])
    plt.xlabel("Tempo [min]")
    plt.title("Timeline de acesso agregado — constelação (12 sats, SSO)")
    plt.xlim(0, 24 * 60)
    plt.grid(True, axis="x")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
