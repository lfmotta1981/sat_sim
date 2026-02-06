import numpy as np

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.orbits.elements import ClassicalOrbitalElements, coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit


def estimate_raan(r, v):
    h = np.cross(r, v)
    n = np.cross([0, 0, 1], h)
    return np.arctan2(n[1], n[0])


def main():
    coe = ClassicalOrbitalElements(
        a=R_EARTH + 550e3,
        e=0.001,
        i=98 * DEG2RAD,   # quase polar (efeito J2 forte)
        raan=0.0,
        argp=0.0,
        nu=0.0
    )

    r0, v0 = coe_to_rv(coe)

    timeline = TimeArray(
        0.0,
        7 * 24 * 3600,   # 7 dias
        60.0
    )

    rs, vs = propagate_orbit(r0, v0, timeline, use_j2=True)

    raans = [estimate_raan(r, v) for r, v in zip(rs, vs)]

    print(f"RAAN inicial [deg]: {raans[0] * 180/np.pi:.2f}")
    print(f"RAAN final   [deg]: {raans[-1] * 180/np.pi:.2f}")
    print(f"Drift total  [deg]: {(raans[-1] - raans[0]) * 180/np.pi:.2f}")


if __name__ == "__main__":
    main()
