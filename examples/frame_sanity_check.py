import numpy as np

from sat_sim.constants import R_EARTH
from sat_sim.frames.transforms import eci_to_ecef, ecef_to_latlon

def main():
    # Ponto fixo no espaço, sobre o equador
    r_eci = np.array([R_EARTH, 0.0, 0.0])

    for t in [0, 3600, 7200]:  # 0h, 1h, 2h
        r_ecef = eci_to_ecef(r_eci, t)
        lat, lon = ecef_to_latlon(r_ecef)

        print(f"t = {t/3600:.1f} h | lat = {lat:.2f} deg | lon = {lon:.2f} deg")

if __name__ == "__main__":
    main()
