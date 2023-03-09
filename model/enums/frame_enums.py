from enum import Enum, auto

class BeamSide(int, Enum):
    Right = 1
    Left = 0

class ColumnSide(int, Enum):
    Above = 1
    Below = 0


