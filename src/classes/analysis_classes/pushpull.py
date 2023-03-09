from dataclasses import dataclass
from typing import List


@dataclass
class PushPullAnalysis:
    """
    Dataclass containing the data of PushPull analysis
    """
    integration_step: float
    disp_points: List[float]
    