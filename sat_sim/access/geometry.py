import numpy as np

def elevation_angle(
    r_sat_ecef: np.ndarray,
    r_gs_ecef: np.ndarray,
    zenith_unit: np.ndarray
) -> float:
    """
    Retorna elevação [rad] do satélite visto da estação.
    """
    rho = r_sat_ecef - r_gs_ecef
    rho_hat = rho / np.linalg.norm(rho)

    sin_e = np.dot(rho_hat, zenith_unit)
    return np.arcsin(sin_e)
