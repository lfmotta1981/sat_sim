import numpy as np
from sat_sim.constants import MU_EARTH

def mean_motion(a: float) -> float:
    """
    Mean motion (rad/s) for circular orbit.
    """
    return np.sqrt(MU_EARTH / a**3)


def propagate_circular_orbit(
    a: float,
    inclination: float,
    raan: float,
    t: float
) -> np.ndarray:
    """
    Retorna posição ECI [m] de uma órbita circular.
    Argument of latitude = n * t
    """

    n = mean_motion(a)
    u = n * t  # argumento de latitude

    # órbita no plano orbital
    r_orb = np.array([
        a * np.cos(u),
        a * np.sin(u),
        0.0
    ])

    # rotações: R3(-RAAN) R1(-i)
    R3 = np.array([
        [ np.cos(-raan), np.sin(-raan), 0],
        [-np.sin(-raan), np.cos(-raan), 0],
        [0, 0, 1]
    ])

    R1 = np.array([
        [1, 0, 0],
        [0, np.cos(-inclination), np.sin(-inclination)],
        [0, -np.sin(-inclination), np.cos(-inclination)]
    ])

    return R3 @ R1 @ r_orb
