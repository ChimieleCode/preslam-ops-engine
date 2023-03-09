from typing import List
import openseespy.opensees as ops
import time

import model.paths as pth

from ..utils import clean_directory
from ..classes import Frame, PushPullAnalysis
from model.enums.frame_enums import BeamSide


def run_pushpull_analysis(frame: Frame,
                          pushpull_analysis: PushPullAnalysis,
                          force_pattern: List[float]) -> None:
    """
    Performs a push-pull analysis on the opensees model

    Args:
        frame (Frame): frame object
        pushpull_analysis (PushPullAnalysis): pushpull analysis
        force_pattern (List[float]): force pushover pattern
    """
    # prepares the output folder
    clean_directory(dir_path=pth.OUTPUT_PUSHPULL_DIR_PATH)

    base_nodes_ids = [
        frame.node_grid(vertical, 0) for vertical in range(frame.n_spans + 1)
    ]
    storey_nodes_ids = [
        frame.node_grid(0, storey) for storey in range(frame.n_storeys + 1)
    ]
    # collect gap node ids
    gap_nodes_ids = [
        frame.node_grid(0, 0),
        frame.node_base(0),
        frame.node_grid(1, 0),
        frame.node_base(1)
    ]
    for storey in range(1, frame.n_storeys + 1):
        gap_nodes_ids += [
            frame.node_rigid_beam(1, storey, BeamSide.Left),
            frame.node_beam(1, storey, BeamSide.Left),
            frame.node_rigid_beam(1, storey, BeamSide.Right),
            frame.node_beam(1, storey, BeamSide.Right)
        ]
    n_pushovers = len(pushpull_analysis.disp_points)

    # Base Reactions
    ops.recorder(
        'Node', 
        '-file', 
        (pth.OUTPUT_PUSHPULL_DIR_PATH / pth.BASE_REACTIONS_FILE).__str__(),
        '-time', 
        '-node', 
        *base_nodes_ids, 
        '-dof', 
        1, 
        'reaction'
    )
    # Floor displacements
    ops.recorder(
        'Node', 
        '-file', 
        (pth.OUTPUT_PUSHPULL_DIR_PATH / pth.STOREY_DISPS_FILE).__str__(),
        '-time', 
        '-node', 
        *storey_nodes_ids, 
        '-dof', 
        1, 
        'disp'
    )
    # gap recorders
    ops.recorder(
        'Node',
        '-file',
        (pth.OUTPUT_PUSHPULL_DIR_PATH / pth.GAP_OPENINGS_FILE).__str__(),
        '-time',
        '-node',
        *gap_nodes_ids,
        '-dof',
        3,
        'disp'
    )

    print(f'-o-o-o- Analysis PushPull step 1/{n_pushovers} -o-o-o-')
    start_t = time.perf_counter()

    # parameters
    disp = pushpull_analysis.disp_points[0]
    direction = disp/abs(disp)
    step = direction * pushpull_analysis.integration_step
    total_steps = round(disp/step)

    # force pattern
    ops.pattern('Plain', 1, 1)
    for storey in range(frame.n_storeys):
        ops.load(
            frame.node_grid(0, storey + 1),
            *[
                direction * force_pattern[storey],
                0.,
                0.
            ]
        )

    # analysis options
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGen')
    ops.test('NormDispIncr', 0.000001, 100)
    ops.algorithm('NewtonLineSearch', True, False, False, False, 0.8, 1000, 0.1, 10)
    # roof disp control
    ops.integrator('DisplacementControl', frame.node_grid(0, frame.n_storeys), 1, step)
    ops.analysis('Static')

    # run analysis
    ops.record()
    ops.analyze(total_steps)

    end_t = time.perf_counter()
    total_time = end_t - start_t

    print(f'-o-o-o- Analysis complete step 1/{n_pushovers} in {total_time:.2f}s -o-o-o-')

    if n_pushovers > 1:
        for i in range(1, n_pushovers):
            print(f'-o-o-o- Analysis PushPull step {i + 1}/{n_pushovers} -o-o-o-')
            start_t = time.perf_counter()

            disp = (pushpull_analysis.disp_points[i] 
                    - pushpull_analysis.disp_points[i - 1])
            direction = disp/abs(disp)
            step = direction * pushpull_analysis.integration_step
            total_steps = round(disp/step)  

            # analysis options
            ops.numberer('RCM')
            ops.system('BandGen')
            ops.test('NormDispIncr', 0.000001, 100)
            ops.algorithm('NewtonLineSearch', True, False, 
                          False, False, 0.8, 1000, 0.1, 10)
            # roof disp control
            ops.integrator('DisplacementControl', 
                           frame.node_grid(0, frame.n_storeys), 1, step)
            ops.analysis('Static')

            # run analysis
            ops.record()
            ops.analyze(total_steps)

            end_t = time.perf_counter()
            total_time = end_t - start_t
            print(f'-o-o-o- Analysis complete step' + 
                  f' {i + 1}/{n_pushovers} in {total_time:.2f}s -o-o-o-')

    ops.wipeAnalysis()
    ops.remove('recorders')
    ops.reset()
