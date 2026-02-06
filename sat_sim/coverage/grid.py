import numpy as np

from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible
from sat_sim.ground.stations import GroundStation


def compute_grid_coverage(
    *,
    constellation,
    timeline,
    propagate_fn,
    min_elevation_rad,
    lat_grid_deg,
    lon_grid_deg
):
    """
    Calcula a fração de tempo coberta em cada ponto do grid.
    Retorna array [n_lat, n_lon] com valores em [0,1].
    """

    n_lat = len(lat_grid_deg)
    n_lon = len(lon_grid_deg)

    coverage = np.zeros((n_lat, n_lon))
    total_steps = len(timeline.times)

    # Pré-criar estações do grid
    stations = [
        [
            GroundStation(lat_deg=lat, lon_deg=lon)
            for lon in lon_grid_deg
        ]
        for lat in lat_grid_deg
    ]

    # Propagar todos os satélites uma vez
    sat_states = []

    for sat in constellation:
        r0, v0 = sat
        rs, _ = propagate_fn(r0, v0, timeline)
        sat_states.append(rs)

    # Loop temporal
    for k, t in enumerate(timeline.times):
        for i in range(n_lat):
            for j in range(n_lon):
                station = stations[i][j]

                visible = False

                for rs in sat_states:
                    r_ecef = eci_to_ecef(rs[k], t)
                    if is_visible(r_ecef, station, min_elevation_rad):
                        visible = True
                        break

                if visible:
                    coverage[i, j] += 1

    return coverage / total_steps
