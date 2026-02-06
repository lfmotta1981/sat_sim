from typing import List, Tuple

def merge_intervals(
    intervals: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """
    Une intervalos sobrepostos.
    """
    if not intervals:
        return []

    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]

        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged

def aggregate_constellation_access(
    all_intervals: List[List[Tuple[float, float]]]
) -> List[Tuple[float, float]]:
    """
    Recebe lista de intervalos por satélite
    e retorna intervalos agregados da constelação.
    """
    flat = []
    for sat_intervals in all_intervals:
        flat.extend(sat_intervals)

    return merge_intervals(flat)
