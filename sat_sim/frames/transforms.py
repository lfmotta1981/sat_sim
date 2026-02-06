import numpy as np
from sat_sim.constants import OMEGA_EARTH
from sat_sim.constants import RAD2DEG

def rotation_matrix_z(theta: float) -> np.ndarray:
    """Rotação em torno do eixo Z."""
    return np.array([
        [ np.cos(theta),  np.sin(theta), 0.0],
        [-np.sin(theta),  np.cos(theta), 0.0],
        [0.0,             0.0,            1.0]
    ])

def eci_to_ecef(r_eci: np.ndarray, t: float) -> np.ndarray:
    """
    Converte vetor posição ECI → ECEF.
    t em segundos desde época inicial.
    """
    theta = OMEGA_EARTH * t
    R = rotation_matrix_z(theta)
    return R @ r_eci

def ecef_to_latlon(r_ecef: np.ndarray):
    """
    Converte ECEF → latitude / longitude (Terra esférica).
    Retorna graus.
    """
    x, y, z = r_ecef
    r = np.linalg.norm(r_ecef)

    lat = np.arcsin(z / r)
    lon = np.arctan2(y, x)

    return lat * RAD2DEG, lon * RAD2DEG
