import numpy as np
from sat_sim.constants import MU_EARTH, R_EARTH, J2

def acceleration_twobody(r: np.ndarray) -> np.ndarray:
    norm_r = np.linalg.norm(r)
    return -MU_EARTH * r / norm_r**3


def acceleration_j2(r: np.ndarray) -> np.ndarray:
    """
    Aceleração perturbativa J2 em ECI.
    """
    x, y, z = r
    r_norm = np.linalg.norm(r)

    factor = (3.0 / 2.0) * J2 * MU_EARTH * R_EARTH**2 / r_norm**5

    zx2 = 5.0 * z**2 / r_norm**2

    ax = factor * x * (zx2 - 1.0)
    ay = factor * y * (zx2 - 1.0)
    az = factor * z * (zx2 - 3.0)

    return np.array([ax, ay, az])


def acceleration_total(r: np.ndarray, use_j2: bool = False) -> np.ndarray:
    a = acceleration_twobody(r)
    if use_j2:
        a += acceleration_j2(r)
    return a
