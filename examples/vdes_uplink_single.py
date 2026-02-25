# examples/vdes_uplink_single.py
from sat_sim.rf.vdes.link_budget import compute_vdes_sat_uplink
import numpy as np

print("Elevation [deg] | SNR [dB] | Margin [dB]")

for elev_deg in range(5, 91, 5):
    distance_km = 900 / np.sin(np.deg2rad(elev_deg))
    off_boresight = np.deg2rad(90 - elev_deg)

    r = compute_vdes_sat_uplink(
        distance_m=distance_km * 1000,
        off_boresight_rad=off_boresight
    )

    print(
        f"{elev_deg:3d} | "
        f"{r['snr_db']:7.2f} | "
        f"{r['margin_db']:7.2f}"
    )
