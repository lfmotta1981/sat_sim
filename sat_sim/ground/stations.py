import numpy as np
from sat_sim.constants import DEG2RAD, R_EARTH

class GroundStation:
    def __init__(self, lat_deg: float, lon_deg: float):
        self.lat = lat_deg * DEG2RAD
        self.lon = lon_deg * DEG2RAD

    def position_ecef(self) -> np.ndarray:
        """
        Retorna posição ECEF da estação (Terra esférica).
        """
        x = R_EARTH * np.cos(self.lat) * np.cos(self.lon)
        y = R_EARTH * np.cos(self.lat) * np.sin(self.lon)
        z = R_EARTH * np.sin(self.lat)

        return np.array([x, y, z])

    def zenith_unit_vector(self) -> np.ndarray:
        """
        Vetor unitário normal local (zenith).
        """
        r = self.position_ecef()
        return r / np.linalg.norm(r)
