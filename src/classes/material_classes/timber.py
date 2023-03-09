from dataclasses import dataclass


@dataclass(frozen=True)
class Timber:
    """
    Dataclas containing the data of timber material
    """
    id : str
    fc : float
    E : float
    G : float
    Eperp : float

    @property
    def epsilon_y(self):
        return self.fc/self.E
    
    def epsilon_lim(self, k_con : float) -> float:
        """
        Deformation limit for timber given the stiffnes constant of the connection

        Args:
            k_con (float): stiffness constant of the connection (below 1)

        Returns:
            float: deformation limit
        """
        assert 0 < k_con <= 1, "k_con must be between 0 and 1"
        return self.fc / (self.E * k_con)
