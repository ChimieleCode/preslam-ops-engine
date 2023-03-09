from typing import List, Optional
from pydantic import BaseModel, validator

class BasicSectionInput(BaseModel):
    """
    Validator data model for section collection
    """
    n_tendons: int
    tendons_pt: float
    axial_load: float
    top_reinforcement_depth: float
    b: float
    h: float
    lambda_bar: Optional[int] = 60
    connection_stiffness_ratio: float
    reinforcement_diameter: int
    reinforcement_count: int

    class Config:
        frozen = True

    @validator('lambda_bar')
    def lambda_bar_limit(cls, value):
        if 40 > value or 60 < value:
            raise ValueError('lambda of bar must be between 40 and 60')
        return value
    
    @validator('reinforcement_count')
    def reinforcement_must_be_present(cls, value):
        if value == 0:
            raise ValueError('reinforcement must be present')
        return value
    
    @validator('connection_stiffness_ratio')
    def must_be_between_1_0(cls, value):
        if value >= 1 or value < 0:
            raise ValueError('connection stiffness ratio must be between 1 and 0')
        return value

    @validator('b')
    def b_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('b must be strictly positive for every section')
        return value

    @validator('h')
    def h_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('h must be strictly positive for every section')
        return value


class SectionCollectionInput(BaseModel):
    """
    Validator data model for section collection
    """
    internal_column: BasicSectionInput
    external_column: BasicSectionInput
    beams: List[BasicSectionInput]

    class Config:
        frozen = True
    
    def __hash__(self):
        return hash(
            tuple(
                [
                    self.internal_column,
                    self.external_column,
                    tuple(self.beams)
                ]
            )
        )


class RegularFrameInput(BaseModel):
    """
    Validator data model for structural frames
    """
    storey_height: float
    span_length: float
    n_storeys: int
    n_spans: int
    n_frames: int
    masses: List[float]
    sections: SectionCollectionInput

    class Config:
        frozen = True

    @validator('n_storeys')
    def storeys_validator(cls, value):
        if value < 1:
            raise ValueError('number of storeys must be at lest one')
        return value

    @validator('n_spans')
    def spans_validator(cls, value):
        if value < 1:
            raise ValueError('number of spans must be at lest one')
        return value

    @validator('masses')
    def masses_must_match_storeys(cls, value, values):
        if len(value) != values['n_storeys']:
            raise ValueError('masses must match with n_storeys')
        return value
