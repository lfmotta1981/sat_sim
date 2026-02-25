# sat_sim/access/vdes_access.py

import numpy as np
from sat_sim.rf.vdes.link_budget import compute_vdes_sat_uplink


def is_vdes_sat_uplink_available(
    r_sat_eci: np.ndarray,
    r_sat_ecef: np.ndarray,
    station,
):
    r_gs = station.position_ecef()

    rho = r_sat_ecef - r_gs
    distance_m = np.linalg.norm(rho)
    rho_hat = rho / distance_m

    zenith = r_gs / np.linalg.norm(r_gs)
    sin_elev = np.dot(rho_hat, zenith)

    if sin_elev <= 0.0:
        return {
            "is_closed": False,
            "reason": "below_horizon"
        }

    result = compute_vdes_sat_uplink(
        distance_m=distance_m,
        off_boresight_rad=0.0
    )

    return result
