from dataclasses import dataclass


@dataclass(frozen=True)
class Steel:
    """
    Dataclass containing the data of steel material
    """
    id : str
    fy : float
    fu : float
    E : float
    epsilon_u : float

    @property
    def epsilon_y(self) -> float:
        return self.fy / self.E

    @property
    def hardening_ratio(self) -> float:
        return (((self.fu - self.fy) * self.epsilon_y)
                / ((self.epsilon_u - self.epsilon_y) * self.fy))
    
    def stress_from_strain(self, strain : float) -> float:
        """
        Computes the stress given the strain

        Args:
            strain (float): strain value

        Returns:
            float: stress value
        """
        if abs(strain) <= self.epsilon_y:
            return strain * self.E
        
        else:
            stress_sign = abs(strain)/strain
            return stress_sign * self.fy * (1 + self.hardening_ratio * (strain / self.epsilon_y - 1))
    
    