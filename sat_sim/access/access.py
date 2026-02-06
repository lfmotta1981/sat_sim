from sat_sim.access.geometry import elevation_angle
import numpy as np


def is_visible(
    r_sat_ecef,
    station,
    min_elevation_rad
) -> bool:
    r_gs = station.position_ecef()
    zenith = station.zenith_unit_vector()

    rho = r_sat_ecef - r_gs
    rho_hat = rho / np.linalg.norm(rho)

    sin_e = np.dot(rho_hat, zenith)
    # Evita erro numérico fora de [-1, 1]
    sin_e = np.clip(sin_e, -1.0, 1.0)
    
    elev = np.arcsin(sin_e)

    return elev >= min_elevation_rad