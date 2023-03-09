from typing import List
from pydantic import BaseModel, validator

class TimeHistoryInput(BaseModel):
    """
    Validator data model for time history analysis
    """
    id : int
    time_step_ratio : float
    scale_factor : float
    time_step : float
    duration : float
    filename : str

    class Config:
        frozen = True


class TimeHistoryCollectionInput(BaseModel):
    """
    Validator data model for multiple time history analyses
    """
    NLTHCases : List[TimeHistoryInput]

    class Config:
        frozen = True