import math
from typing import List
import numpy as np

G = 9.81


def spectral_acceleration(time_series: List[float], time_step: float,
                          period: float = 0.01, csi: float = 0.05) -> float:
    """
    Computes the spectral acceleration using direct integration

    Args:
        time_series (List[float]): time series
        time_step (float): time step of time series
        period (float, optional): period. Defaults to 0.01.
        csi (float, optional): critical damping ratio. Defaults to 0.05.

    Returns:
        float: spectral acceleration
    """                         
    # TH
    base_acc = np.array(time_series)

    base_acc_g = base_acc/G

    # SDOF params
    omega_0 = 2 * math.pi / period
    unit_mass = 1
    force = -unit_mass * base_acc_g * G
    k = unit_mass * omega_0**2
    c = 2 * csi * unit_mass * omega_0

    # Integration params
    A = unit_mass / time_step**2
    B = c / (2 * time_step)

    u_r = np.zeros(len(base_acc))
    a_r = np.zeros(len(base_acc))

    # Relative displacements
    for i in range(1, len(base_acc) - 1):
        u_r[i + 1] = 1/(A + B) * (force[i] - u_r[i] * (k - 2*A) - u_r[i - 1] * (A - B))

    # Relative accelerations
    for i in range(1, len(base_acc) - 1):
        a_r[i] = (u_r[i + 1] + u_r[i - 1] - 2*u_r[i]) / (time_step**2 * G)

    return np.max(abs(a_r + base_acc_g))



    
