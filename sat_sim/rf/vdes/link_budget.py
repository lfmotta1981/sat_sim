# sat_sim/rf/vdes/link_budget.py

import numpy as np
from sat_sim.constants import C_LIGHT, K_BOLTZMANN
from sat_sim.rf.vdes.antenna import satellite_rx_gain


def compute_vdes_sat_uplink(
    distance_m: float,
    off_boresight_rad: float = 0.0,
    tx_eirp_dbw: float = 14.0,
    frequency_hz: float = 162e6,
    bandwidth_hz: float = 25e3,
    gt_sat_db: float = -5.0,
    cn_required_db: float = 6.0,
):
    wavelength = C_LIGHT / frequency_hz

    fspl_db = (
        20 * np.log10(4 * np.pi * distance_m / wavelength)
    )

    rx_gain_db = satellite_rx_gain(off_boresight_rad)

    cn_db = (
        tx_eirp_dbw
        + rx_gain_db
        + gt_sat_db
        - fspl_db
        - 10 * np.log10(K_BOLTZMANN * bandwidth_hz)
    )

    margin_db = cn_db - cn_required_db

    return {
        "cn_db": cn_db,
        "margin_db": margin_db,
        "is_closed": margin_db >= 0.0
    }
