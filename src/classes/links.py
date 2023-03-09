from dataclasses import dataclass
from typing import List

@dataclass
class KineticLink:
    """
    Dataclass containing information about the Kinetic Link
    """
    Fy : float
    E0 : float
    H_iso : float = 0
    H_kin : float = 0
    strain_limit : float = 10

@dataclass
class MultilinearElasticLink:
    """
    Dataclass containing information about the Tendon MultilinearElastic Link
    """
    strain : List[float]
    stress : List[float]

@dataclass
class GMSteelLink:
    """
    Dataclass containing information about the Giuffrè Menegotto Pinto Steel Link
    """
    Fy : float
    E0 : float
    b : float
    r0 : float = 20
    cr1 : float = 0.925
    cr2 : float = 0.15
    strain_limit : float = 10