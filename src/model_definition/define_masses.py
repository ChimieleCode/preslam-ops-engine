from itertools import product
import openseespy.opensees as ops
from ..classes import Frame


def define_node_masses(frame: Frame) -> None:
    """
    Define masses of the model for grid nodes

    Args:
        frame (Frame): frame object
    """
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(frame.n_spans + 1)):
        if vertical in (0, frame.n_spans):
            ops.mass(
                frame.node_grid(vertical, storey),
                frame.masses[storey - 1]/(2 * frame.n_spans * frame.n_frames),
                0,
                0
            )
        
        else:
            ops.mass(
                frame.node_grid(vertical, storey),
                frame.masses[storey - 1]/(frame.n_spans * frame.n_frames),
                frame.masses[storey - 1]/(frame.n_spans * frame.n_frames),
                0.
            )


def define_node_weights(frame: Frame) -> None:
    """
    Define weights of the model for grid nodes

    Args:
        frame (Frame): frame object
    """
    ax_unit = frame.int_column_section.axial_load/sum(frame.masses)

    ops.pattern('Plain', 0, 1)
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(frame.n_spans + 1)):
        if vertical in (0, frame.n_spans):
            ops.load(
                frame.node_grid(vertical, storey),
                0.,
                -frame.masses[storey - 1]/2 * ax_unit,
                0.
            )
        
        else:
            ops.load(
                frame.node_grid(vertical, storey),
                0.,
                -frame.masses[storey - 1] * ax_unit,
                0.
            )

    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('ProfileSPD')
    ops.test('NormDispIncr', 0.000001, 100)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')

    ops.record()
    ops.analyze(10)

    ops.setTime(0.)
    ops.loadConst()
