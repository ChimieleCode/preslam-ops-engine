from dataclasses import dataclass


@dataclass(frozen=True)
class Tendon:
    """
    Dataclass containing the data of tendon material
    """
    id : str
    fy : float
    fu : float
    E : float
    A : float
    epsilon_u : float

    @property
    def epsilon_y(self) -> float:
        return self.fy/self.E