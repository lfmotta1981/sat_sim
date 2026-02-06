import numpy as np

from sat_sim.constants import R_EARTH


def ecef_to_latlon(r_ecef: np.ndarray):
    """
    Converte vetor ECEF (m) para latitude e longitude geocêntricas (graus).

    Retorna:
        lat_deg, lon_deg
    """
    x, y, z = r_ecef

    r_xy = np.sqrt(x**2 + y**2)

    lat = np.arctan2(z, r_xy)
    lon = np.arctan2(y, x)

    lat_deg = np.degrees(lat)
    lon_deg = np.degrees(lon)

    return lat_deg, lon_deg
