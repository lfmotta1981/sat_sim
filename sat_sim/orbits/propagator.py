import numpy as np
from sat_sim.orbits.dynamics import acceleration_total

def rk4_step(r, v, dt, use_j2=False):

    def f(state):
        r, v = state[:3], state[3:]
        a = acceleration_total(r, use_j2=use_j2)
        return np.hstack((v, a))

    state = np.hstack((r, v))

    k1 = f(state)
    k2 = f(state + 0.5 * dt * k1)
    k3 = f(state + 0.5 * dt * k2)
    k4 = f(state + dt * k3)

    new_state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

    return new_state[:3], new_state[3:]


def propagate_orbit(r0, v0, timeline, use_j2=False):
    r = r0.copy()
    v = v0.copy()

    rs, vs = [], []

    for _ in timeline.times:
        rs.append(r)
        vs.append(v)
        r, v = rk4_step(r, v, timeline.dt, use_j2=use_j2)

    return np.array(rs), np.array(vs)
