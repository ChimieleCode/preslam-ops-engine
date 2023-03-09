from pydantic import BaseModel, validator

class SteelInput(BaseModel):
    """
    Validator data model for Steel Material
    """
    id : str
    fy : float
    fu : float
    E : float
    epsilon_u : float

    class Config:
        frozen = True


class TimberInput(BaseModel):
    """
    Validator data model for Timber Material
    """
    id : str
    fc : float
    E : float
    G : float
    Eperp : float

    class Config:
        frozen = True


class TendonInput(BaseModel):
    """
    Validator data model for Tendon Material
    """
    id : str
    fy : float
    fu : float
    E : float
    A : float
    epsilon_u : float

    class Config:
        frozen = True