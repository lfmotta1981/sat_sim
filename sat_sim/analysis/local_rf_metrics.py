# sat_sim/analysis/local_rf_metrics.py

import numpy as np

from sat_sim.frames.transforms import eci_to_ecef
from sat_sim.access.intervals import (
    compute_access_intervals,
    max_gap,
    revisit_times
)
from sat_sim.access.vdes_access import is_vdes_sat_uplink_available


def compute_local_rf_metrics(
    constellation,
    timeline,
    station,
    propagate_fn
):
    """
    Calcula métricas RF locais:
    - disponibilidade (%)
    - gap máximo (s)
    - revisit médio (s)
    """

    # Propagar todos satélites
    propagated = []
    for r0, v0 in constellation:
        rs, _ = propagate_fn(r0, v0, timeline)
        propagated.append(rs)

    closed_times = []

    for k, t in enumerate(timeline.times):

        closed_any = False

        for rs in propagated:

            r_eci = rs[k]
            r_ecef = eci_to_ecef(r_eci, t)

            res = is_vdes_sat_uplink_available(
                r_sat_eci=r_eci,
                r_sat_ecef=r_ecef,
                station=station
            )

            if res.get("is_closed", False):
                closed_any = True
                break

        if closed_any:
            closed_times.append(t)

    availability = 100.0 * len(closed_times) / len(timeline.times)

    intervals = compute_access_intervals(
        closed_times,
        timeline.dt
    )

    if intervals:
        worst_gap = max_gap(
            intervals,
            0.0,
            timeline.times[-1] + timeline.dt
        )
        revisits = revisit_times(intervals)
        mean_revisit = np.mean(revisits) if revisits else 0.0
    else:
        worst_gap = timeline.times[-1]
        mean_revisit = 0.0

    return {
        "availability_percent": availability,
        "worst_gap_s": worst_gap,
        "mean_revisit_s": mean_revisit
    }
