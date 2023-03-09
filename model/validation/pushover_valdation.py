from typing import List
from pydantic import BaseModel, validator

class PushPullInput(BaseModel):
    """
    Validator data model for Push-Pull analysis
    """
    integration_step : float
    disp_points : List[float]

    class Config:
        frozen = True

    @validator('integration_step')
    def validate_integration_step(cls, value):
        if value <= 0:
            raise ValueError('integration step must be strictly positive')
        return value

    @validator('disp_points')
    def validate_point_series(cls, value, values):
        if abs(value[0]) < values['integration_step']:
            raise ValueError('first point must be greater then integration step')
        for this_value, next_value in zip(value, value[1:]):
            if abs(this_value - next_value) < values['integration_step']:
                raise ValueError('different points must differ at least by' + 
                                 ' one integration step')
        return value