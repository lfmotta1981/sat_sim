# sat_sim/rf/vdes/params.py
from dataclasses import dataclass

@dataclass
class VDESLinkParams:
    frequency_hz: float
    bandwidth_hz: float
    eirp_dbw: float
    gt_rx_db_per_k: float
    snr_min_db: float
    system_losses_db: float


VDES_SAT_UL = VDESLinkParams(
    frequency_hz=162e6,       # VDES VHF band
    bandwidth_hz=25e3,        # VDES channelization
    eirp_dbw=10.0,            # placeholder (ship TX, norm-limited)
    gt_rx_db_per_k=-5.0,      # satellite receiver
    snr_min_db=6.0,           # service-level requirement
    system_losses_db=2.0      # implementation losses
)

VDES_PARAMS = {
    "vdes_sat_uplink": VDES_SAT_UL
}
