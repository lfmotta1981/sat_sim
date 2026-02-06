import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.elements import ClassicalOrbitalElements, coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible


def main():
    # Estação tipo Svalbard
    station = GroundStation(
        lat_deg=79.0,
        lon_deg=17.5
    )

    # Satélite SSO
    coe = ClassicalOrbitalElements(
        a=R_EARTH + 550e3,
        e=0.0,
        i=98.0 * DEG2RAD,
        raan=0.0 * DEG2RAD,
        argp=0.0,
        nu=0.0
    )

    r0, v0 = coe_to_rv(coe)

    timeline = TimeArray(
        0.0,
        24 * 3600,
        30.0
    )

    rs, _ = propagate_orbit(
        r0,
        v0,
        timeline,
        use_j2=True
    )

    min_elev = 0.0 * DEG2RAD

    visible_times = []

    for r_eci, t in zip(rs, timeline.times):
        r_ecef = eci_to_ecef(r_eci, t)

        if is_visible(r_ecef, station, min_elev):
            visible_times.append(t)

    print(f"Total de instantes visíveis no dia: {len(visible_times)}")

    # --------- AGRUPAR EM PASSES ----------
    passes = []
    current_pass = []

    for t in visible_times:
        if not current_pass:
            current_pass.append(t)
        elif t - current_pass[-1] <= timeline.dt + 1e-6:
            current_pass.append(t)
        else:
            passes.append(current_pass)
            current_pass = [t]

    if current_pass:
        passes.append(current_pass)

    print(f"Número de passes no dia: {len(passes)}")

    for i, p in enumerate(passes):
        start_min = p[0] / 60.0
        duration_min = len(p) * timeline.dt / 60.0

        print(
            f"Passe {i+1:02d} | "
            f"início = {start_min:6.1f} min | "
            f"duração ≈ {duration_min:5.1f} min"
        )


if __name__ == "__main__":
    main()
