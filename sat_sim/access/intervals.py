from typing import List, Tuple

def compute_access_intervals(
    visible_times: List[float],
    dt: float
) -> List[Tuple[float, float]]:
    """
    Converte instantes visíveis em intervalos de acesso.

    Retorna lista de (t_start, t_end), em segundos.
    """
    if not visible_times:
        return []

    intervals = []
    t_start = visible_times[0]
    t_prev = visible_times[0]

    for t in visible_times[1:]:
        if t - t_prev <= dt * 1.01:
            t_prev = t
        else:
            intervals.append((t_start, t_prev + dt))
            t_start = t
            t_prev = t

    intervals.append((t_start, t_prev + dt))
    return intervals

def access_durations(intervals):
    """Retorna lista de durações (s)."""
    return [end - start for start, end in intervals]


def max_gap(intervals, t_start, t_end):
    """
    Retorna o maior gap sem acesso dentro da janela.
    """
    if not intervals:
        return t_end - t_start

    gaps = []

    # Gap inicial
    gaps.append(intervals[0][0] - t_start)

    # Gaps entre acessos
    for (s1, e1), (s2, _) in zip(intervals[:-1], intervals[1:]):
        gaps.append(s2 - e1)

    # Gap final
    gaps.append(t_end - intervals[-1][1])

    return max(gaps)


def revisit_times(intervals):
    """
    Retorna tempos entre inícios de acessos consecutivos.
    """
    if len(intervals) < 2:
        return []

    return [
        intervals[i+1][0] - intervals[i][0]
        for i in range(len(intervals) - 1)
    ]
