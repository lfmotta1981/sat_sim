import numpy as np

class TimeArray:
    """
    Representa uma linha do tempo discreta do simulador.
    Tempo é sempre contado em segundos desde t0.
    """

    def __init__(self, t0: float, tf: float, dt: float):
        self.t0 = float(t0)
        self.tf = float(tf)
        self.dt = float(dt)

        self.times = np.arange(t0, tf + dt, dt)

    def __len__(self):
        return len(self.times)
