from enum import Enum

class Transformation(int, Enum):
    Linear = 1
    PDelta = 2

class ConnectionLimitStateType(str, Enum):
    DS1 = 'DS1'
    DS2 = 'DS2'
    DST = 'DST'