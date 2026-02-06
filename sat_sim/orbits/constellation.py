import numpy as np
from sat_sim.orbits.elements import ClassicalOrbitalElements


def generate_constellation(
    altitude: float,
    inclination: float,
    n_planes: int,
    sats_per_plane: int,
    raan0: float = 0.0
):
    """
    Gera uma constelação tipo Walker (parametrização explícita).

    Retorna lista de ClassicalOrbitalElements.
    """

    delta_raan = 2 * np.pi / n_planes
    delta_phase = 2 * np.pi / sats_per_plane

    sats = []

    for p in range(n_planes):
        raan = raan0 + p * delta_raan

        for s in range(sats_per_plane):
            nu = s * delta_phase

            coe = ClassicalOrbitalElements(
                a=altitude,
                e=0.0,
                i=inclination,
                raan=raan,
                argp=0.0,
                nu=nu
            )

            sats.append(coe)

    return sats
