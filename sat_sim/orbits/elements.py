import numpy as np
from dataclasses import dataclass
from sat_sim.constants import MU_EARTH

@dataclass
class ClassicalOrbitalElements:
    a: float
    e: float
    i: float
    raan: float
    argp: float
    nu: float


def coe_to_rv(coe: ClassicalOrbitalElements):
    a, e, i, raan, argp, nu = (
        coe.a, coe.e, coe.i,
        coe.raan, coe.argp, coe.nu
    )

    p = a * (1 - e**2)

    r_pf = np.array([
        p * np.cos(nu) / (1 + e * np.cos(nu)),
        p * np.sin(nu) / (1 + e * np.cos(nu)),
        0.0
    ])

    v_pf = np.array([
        -np.sqrt(MU_EARTH / p) * np.sin(nu),
        np.sqrt(MU_EARTH / p) * (e + np.cos(nu)),
        0.0
    ])

    def R3(theta):
        return np.array([
            [ np.cos(theta),  np.sin(theta), 0],
            [-np.sin(theta),  np.cos(theta), 0],
            [0, 0, 1]
        ])

    def R1(theta):
        return np.array([
            [1, 0, 0],
            [0, np.cos(theta),  np.sin(theta)],
            [0, -np.sin(theta), np.cos(theta)]
        ])

    Q = R3(-raan) @ R1(-i) @ R3(-argp)

    r = Q @ r_pf
    v = Q @ v_pf

    return r, v
