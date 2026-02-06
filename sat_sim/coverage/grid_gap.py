import numpy as np

from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.access import is_visible
from sat_sim.access.intervals import (
    compute_access_intervals,
    max_gap
)
from sat_sim.ground.stations import GroundStation


def compute_grid_max_gap(
    *,
    constellation,
    timeline,
    propagate_fn,
    min_elevation_rad,
    lat_grid_deg,
    lon_grid_deg
):
    """
    Calcula o gap máximo (em segundos) para cada célula do grid.
    Retorna array [n_lat, n_lon].
    """

    n_lat = len(lat_grid_deg)
    n_lon = len(lon_grid_deg)

    max_gap_grid = np.zeros((n_lat, n_lon))

    # Estações virtuais
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

    t_end = timeline.times[-1] + timeline.dt

    # Loop por célula
    for i in range(n_lat):
        for j in range(n_lon):
            station = stations[i][j]

            visible_times = []

            for k, t in enumerate(timeline.times):
                for rs in sat_states:
                    r_ecef = eci_to_ecef(rs[k], t)
                    if is_visible(r_ecef, station, min_elevation_rad):
                        visible_times.append(t)
                        break

            intervals = compute_access_intervals(
                visible_times,
                timeline.dt
            )

            gap = max_gap(intervals, 0.0, t_end)
            max_gap_grid[i, j] = gap

    return max_gap_grid
