# sat_sim/rf/vdes/antenna.py

def satellite_rx_gain(off_boresight_rad: float) -> float:
    """
    Ganho RX do satélite para VDES-SAT uplink.

    Modelo atual:
    - Wide-beam / quasi-omnidirecional
    - Não penaliza off-boresight
    """
    return 0.0  # dBi
