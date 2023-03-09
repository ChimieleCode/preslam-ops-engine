import os
import pandas as pd
import numpy as np

from numpy.typing import ArrayLike
from typing import List
from pathlib import Path
from .time_history import run_time_history_analysis
from ..classes import TimeHistoryAnalysis, Frame
from ..time_series_tools import spectral_acceleration
from ..utils import import_configuration

import model.paths as pth

# Import config data
import model.config as config

cfg: config.MNINTConfig
cfg = import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)


def get_intensity_measure(time_history_analysis: TimeHistoryAnalysis,
                          period: float) -> float:
    """
    Returns the intensity measure for given period
    :param time_history_analysis: time history data
    :param period: first mode period
    :return:
    """
    return spectral_acceleration(
        np.loadtxt(pth.IDA_TIMESERIES_INPUT_FOLDER / time_history_analysis.filename),
        time_history_analysis.time_step,
        period
    )


def format_ls(limit_states: ArrayLike) -> ArrayLike:
    rows = limit_states.shape[0]
    formatted_limit_states = np.zeros(2 * (rows - 1))
    formatted_limit_states[:2] = limit_states[:2]
    for i in range(2, rows):
        formatted_limit_states[2*i-2] = limit_states[i]
        formatted_limit_states[2*i-1] = limit_states[i]
    return formatted_limit_states


def compute_dcr(results_directory: Path) -> dict:
    """
    Computes the demand capacity ratios of the sections given the tim ehistory save path

    Args:
        results_directory (Path): path where to find time history output files

    Returns:
        dict: demand capacity ratios for each DS
    """
    damage_states = pd.read_csv('.\\output\\section_limit_states.csv')

    recorded_gaps = np.loadtxt(results_directory / pth.GAP_OPENINGS_FILE)[:, 1:]
    left_rotations = recorded_gaps[:, ::2]
    right_rotations = recorded_gaps[:, 1::2]
    gap_openings = abs(left_rotations - right_rotations)
    max_gap_openings = np.amax(gap_openings, axis=0)

    demand_capacity_ratios = dict()
    for key in damage_states.keys():
        limit_states = format_ls(damage_states[key].to_numpy())
        demand_capacity_ratios[key] = max(
            np.nan_to_num(max_gap_openings/limit_states)
        )
    
    return demand_capacity_ratios


def run_incremental_dynamic_analysis(frame: Frame,
                                     time_history_analysis: TimeHistoryAnalysis,
                                     structure_periods: List[float]) -> None:
    run_number = 1
    reached_dcr = False
    continue_iterating = True
    bisection = False
    id_ground_motion = time_history_analysis.id

    ida_results = pd.DataFrame(columns=['scale_factor', 'int_measures', 'DS1', 'DS2', 'DST'])

    initial_int_measure = get_intensity_measure(time_history_analysis, structure_periods[0])
    current_scale_factor = cfg.ida_options.initial_int_measure/initial_int_measure

    step = current_scale_factor * cfg.ida_options.initial_step

    th_directory = Path(f'./output/IDA/TH_{time_history_analysis.id:04d}')

    if not os.path.isdir(th_directory):
        os.mkdir(th_directory)

    while (not reached_dcr) and continue_iterating:
        ida_directory = th_directory / f'run_{run_number:04d}'
        # update scale factor and id
        time_history_analysis.id = run_number
        time_history_analysis.scale_factor = current_scale_factor 
        print(f'------> CASE {id_ground_motion} : {run_number}')
        success = run_time_history_analysis(
            frame, 
            time_history_analysis, 
            structure_periods, 
            save_dir=ida_directory,
            ida=True
        )

        run_number += 1

        bisection = (not success) or bisection
        continue_iterating = (step > cfg.ida_options.initial_step * 0.5**cfg.ida_options.max_iter_ida)

        data_row = [
            current_scale_factor, 
            initial_int_measure * current_scale_factor
        ]
        if bisection:
            step = step * 0.5

        if not continue_iterating:
            pass

        if not success:
            current_scale_factor = current_scale_factor - step
            continue
        
        current_scale_factor = current_scale_factor + step

        dem_cap_ratios = list(compute_dcr(ida_directory).values())
        data_row += dem_cap_ratios
        ida_results.loc[len(ida_results)] = data_row

        reached_dcr = np.all(np.greater_equal(np.array(dem_cap_ratios), 1))
        continue_iterating = (step > cfg.ida_options.initial_step * 0.5**cfg.ida_options.max_iter_ida)

    ida_results.to_csv(th_directory / 'ida_results.csv')
        






        

    
