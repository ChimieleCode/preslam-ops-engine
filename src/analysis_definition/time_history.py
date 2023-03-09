from pathlib import Path
from typing import List
import openseespy.opensees as ops
import time
import math
import os

import model.paths as pth

from model.enums.frame_enums import BeamSide
from ..classes import Frame, TimeHistoryAnalysis
from ..utils import clean_directory, export_to_json


def run_time_history_analysis(frame: Frame,
                              time_history_analysis: TimeHistoryAnalysis,
                              structure_periods: List[float],
                              save_dir: Path = None,
                              ida: bool = False) -> bool:
    """
    Runs a time history analysis

    Args:
        frame (Frame): frame object
        time_history_analysis (TimeHistoryAnalysis): time history options.
        structure_periods (List[float]) List of modal periods
        save_dir (Path, optional): directory where to save the analysis output.
            Defaults to the one specified in model.paths.
        ida (bool, optional): if the TH is part of an IDA sequence. Defaults False.

    Returns:
        bool: success of analysis
    """
    if save_dir is None:
        th_results_directory = (
            pth.OUTPUT_TH_DIR_PATH / f'TH_{time_history_analysis.id:04}'
        )
    else:
        th_results_directory = save_dir

    if os.path.isdir(th_results_directory):
        clean_directory(th_results_directory)
    else:
        os.mkdir(th_results_directory)

    print(f'-o-o-o- THNL Analysis {time_history_analysis.id} -o-o-o-')

    storey_nodes_ids = [
        frame.node_grid(0, storey) for storey in range(frame.n_storeys + 1)
    ]
    base_nodes_ids = [
        frame.node_grid(span, 0) for span in range(frame.n_spans + 1)
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
    # storey disp recorder
    ops.recorder(
        'Node', 
        '-file', 
        (th_results_directory / pth.STOREY_DISPS_FILE).__str__(),
        '-time', 
        '-node', 
        *storey_nodes_ids, 
        '-dof', 
        1, 
        'disp'
    )
    # storey relative accelerations recorder
    ops.recorder(
        'Node', 
        '-file',
        (th_results_directory / pth.STOREY_REL_ACC_FILE).__str__(),
        '-time', 
        '-node', 
        *storey_nodes_ids, 
        '-dof', 
        1, 
        'accel'
    )
    # gap recorders
    ops.recorder(
        'Node', 
        '-file',
        (th_results_directory / pth.GAP_OPENINGS_FILE).__str__(),
        '-time', 
        '-node', 
        *gap_nodes_ids, 
        '-dof', 
        3, 
        'disp'
    )
    # base reactions recorder
    ops.recorder(
        'Node',
        '-file',
        (th_results_directory / pth.BASE_REACTIONS_FILE).__str__(),
        '-time',
        '-node',
        *base_nodes_ids,
        '-dof',
        1,
        'reaction'
    )

    T1 = structure_periods[0]

    # Handle edge cases: 1 and 2 floors
    if frame.n_storeys == 1:
        T2 = T1 * 0.2
    elif frame.n_storeys == 2:
        T2 = structure_periods[frame.n_storeys - 1]
    else:
        T2 = structure_periods[frame.n_storeys - 2]
        
    # computes damping Rayleigh coeff
    om_1 = 2*math.pi / T1
    om_2 = 2*math.pi / T2
    aR = (2*(om_1 * om_2 * (om_2 - om_1) * frame.damping) / (om_2**2 - om_1**2))
    bR = 2 * (om_2 - om_1) * frame.damping / (om_2**2 - om_1**2)

    # time series definition
    time_series_input_folder = pth.IDA_TIMESERIES_INPUT_FOLDER if ida else pth.TIMESERIES_INPUT_FOLDER
    dt = time_history_analysis.time_step
    ops.timeSeries(
        'Path', 
        time_history_analysis.id + 1, 
        '-dt', 
        dt, 
        '-filePath',
        (time_series_input_folder / time_history_analysis.filename).__str__(),
        '-factor', 
        time_history_analysis.scale_factor
    )
    # performance
    start_t = time.perf_counter()

    # analysis options
    ops.test('NormDispIncr', 10**-6, 1000, 0, 0)
    ops.pattern('UniformExcitation', time_history_analysis.id + 1, 
                1, '-accel', time_history_analysis.id + 1)
    ops.constraints('Plain')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.rayleigh(aR, bR, 0., 0.)
    ops.algorithm('NewtonLineSearch', True, False, False, False, 0.8, 100, 0.1, 1)
    ops.numberer('RCM')
    ops.system('BandGen')
    ops.analysis('Transient')

    TH_steps = round(time_history_analysis.duration/dt + structure_periods[0] * 10) # Not good if u want to track residual disps, try adding 20 T1
    success = True

    time_analysis = 0
    final_time = ops.getTime() + TH_steps * dt

    dt_analyze = dt * time_history_analysis.time_step_ratio

    while success and time_analysis <= final_time:

        analysis_status = ops.analyze(1, dt_analyze)
        success = (analysis_status == 0)
        time_analysis = ops.getTime()

    end_t = time.perf_counter()
    total_time = end_t - start_t

    if success:

        print(f'-o-o-o- THNL Analysis succesful {time_history_analysis.id}' + 
              f' in {total_time:.2f}s -o-o-o-')

    else:

        print(f'-o-o-o- THNL Analysis failed {time_history_analysis.id}' + 
              f' in {total_time:.2f}s -o-o-o-')

    ops.wipeAnalysis()
    ops.remove('recorders')
    ops.remove('loadPattern', time_history_analysis.id + 1)
    ops.reset()

    # Stats
    th_stats = {
        'time': total_time,
        'success': success,
        'time_series_name': time_history_analysis.filename
    }
    export_to_json(
        filepath=th_results_directory / pth.TH_STATS_FILE,
        data=th_stats
    )

    return success
