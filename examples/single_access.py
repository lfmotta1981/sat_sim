import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.elements import ClassicalOrbitalElements, coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible
from sat_sim.access.intervals import (
    compute_access_intervals,
    access_durations,
    max_gap,
    revisit_times
)


def main():
    # -------------------------------
    # Estação no solo (Svalbard-like)
    # -------------------------------
    station = GroundStation(
        lat_deg=79.0,
        lon_deg=17.5
    )

    # -------------------------------
    # Satélite SSO
    # -------------------------------
    coe = ClassicalOrbitalElements(
        a=R_EARTH + 550e3,
        e=0.0,
        i=98.0 * DEG2RAD,
        raan=0.0,
        argp=0.0,
        nu=0.0
    )

    r0, v0 = coe_to_rv(coe)

    # -------------------------------
    # Janela temporal
    # -------------------------------
    timeline = TimeArray(
        0.0,
        24 * 3600,   # 24 h
        30.0         # 30 s
    )

    rs, _ = propagate_orbit(
        r0,
        v0,
        timeline,
        use_j2=True
    )

    # -------------------------------
    # Critério de visibilidade
    # -------------------------------
    min_elev = 00.0 * DEG2RAD

    visible_times = []

    for r_eci, t in zip(rs, timeline.times):
        r_ecef = eci_to_ecef(r_eci, t)
        if is_visible(r_ecef, station, min_elev):
            visible_times.append(t)

    print(f"Instantes visíveis no dia: {len(visible_times)}")

    # -------------------------------
    # Intervalos de acesso
    # -------------------------------
    intervals = compute_access_intervals(
        visible_times,
        timeline.dt
    )

    print(f"Número de passes: {len(intervals)}")

    for i, (t0, t1) in enumerate(intervals):
        print(
            f"Passe {i+1:02d} | "
            f"início = {t0/3600:.2f} h | "
            f"duração = {(t1 - t0)/60:.1f} min"
        )

    # -------------------------------
    # Métricas
    # -------------------------------
    if intervals:
        durations = access_durations(intervals)
        print(f"Duração média: {np.mean(durations)/60:.1f} min")

        gap = max_gap(intervals, 0.0, timeline.times[-1] + timeline.dt)
        print(f"Maior gap sem acesso: {gap/3600:.2f} h")

        revisits = revisit_times(intervals)
        if revisits:
            print(f"Revisit médio: {np.mean(revisits)/3600:.2f} h")


if __name__ == "__main__":
    main()
