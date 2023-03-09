from dataclasses import dataclass


@dataclass
class TimeHistoryAnalysis:
    """
    Dataclass containing the data of NLTHA analysis
    """
    id: int
    time_step_ratio: float
    scale_factor: float
    time_step: float
    duration: float
    filename: str

    @property
    def steps(self) -> int:
        return round(self.duration / self.time_step)