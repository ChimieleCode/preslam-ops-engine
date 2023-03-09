import openseespy.opensees as ops
from itertools import product

from ..classes.frame import Frame


def define_nodal_vertical_loads(frame: Frame) -> None:
    """
    Defines Vertical loads for the frame nodes
    :param frame: frame data
    :return: None
    """
    frame_tot_mass = sum(frame.masses)
    axial_unit_int = frame.int_column_section.axial_load/frame_tot_mass
    axial_unit_ext = frame.ext_column_section.axial_load/frame_tot_mass

    ops.pattern('Plain', 0, 1)

    for vertical, floor in product(range(frame.n_spans + 1), range(1, frame.n_storeys + 1)):
        if vertical in {0, frame.n_spans}:
            axial_unit = axial_unit_ext
        else:
            axial_unit = axial_unit_int

        ops.load(
            frame.node_grid(vertical, floor),
            0.,
            -frame.masses[floor - 1] * axial_unit,
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
    ops.wipeAnalysis()



