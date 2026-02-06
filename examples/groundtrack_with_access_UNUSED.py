import numpy as np
import matplotlib.pyplot as plt

from sat_sim.constants import R_EARTH, DEG2RAD
from sat_sim.time import TimeArray
from sat_sim.ground.stations import GroundStation
from sat_sim.orbits.elements import ClassicalOrbitalElements, coe_to_rv
from sat_sim.orbits.propagator import propagate_orbit
from sat_sim.frames.transforms import eci_to_ecef, ecef_to_latlon
from sat_sim.access.access import is_visible


def main():
    # -------------------------------
    # Estação (guardar lat/lon em graus para o plot)
    # -------------------------------
    station_lat = 79.0
    station_lon = 17.5

    station = GroundStation(
        lat_deg=station_lat,
        lon_deg=station_lon
    )

    # -------------------------------
    # Satélite SSO representativo
    # -------------------------------
    coe = ClassicalOrbitalElements(
        a=R_EARTH + 550e3,
        e=0.0,
        i=98.0 * DEG2RAD,
        raan=0.0,
        argp=0.0,
        nu=0.0
    )

    r0, v0 = coe_to_rv(coe)

    # -------------------------------
    # Janela temporal
    # -------------------------------
    timeline = TimeArray(
        0.0,
        24 * 3600,
        30.0
    )

    min_elev = 0.0 * DEG2RAD

    rs, _ = propagate_orbit(
        r0,
        v0,
        timeline,
        use_j2=True
    )

    lats = []
    lons = []
    access_lats = []
    access_lons = []

    for r_eci, t in zip(rs, timeline.times):
        r_ecef = eci_to_ecef(r_eci, t)

        lat, lon = ecef_to_latlon(r_ecef)

        lat_deg = lat * 180.0 / np.pi
        lon_deg = lon * 180.0 / np.pi

        lats.append(lat_deg)
        lons.append(lon_deg)

        if is_visible(r_ecef, station, min_elev):
            access_lats.append(lat_deg)
            access_lons.append(lon_deg)

    # -------------------------------
    # Plot
    # -------------------------------
    plt.figure(figsize=(10, 5))

    # Ground track
    plt.plot(
        lons,
        lats,
        color="lightgray",
        linewidth=1,
        label="Ground track"
    )

    # Pontos de acesso
    plt.scatter(
        access_lons,
        access_lats,
        color="red",
        s=12,
        label="Acesso à estação"
    )

    # Estação
    plt.scatter(
        station_lon,
        station_lat,
        color="blue",
        marker="^",
        s=80,
        label="Estação"
    )

    plt.xlabel("Longitude [deg]")
    plt.ylabel("Latitude [deg]")
    plt.title("Ground track SSO + pontos de acesso (24h)")
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
