from math import floor
import openseespy.opensees as ops
from itertools import product
from ..classes import Frame


def define_diaphragm(frame: Frame) -> None:
    """
    Defines diaphragm constrains 

    Args:
        frame (Frame): frame object
    """
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(1, frame.n_spans + 1)):
        ops.equalDOF(
            frame.node_grid(0, storey),
            frame.node_grid(vertical, storey),
            1
        )


def define_base_restraints(frame: Frame) -> None:
    """
    Defines base restraints

    Args:
        frame (Frame): frame object
    """
    for vertical in range(frame.n_spans + 1):
        ops.fix(
            frame.node_grid(vertical, 0),
            *[1, 1, 1]
        )
