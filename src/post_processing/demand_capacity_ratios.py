from typing import List
import numpy as np
import pandas as pd

from model.enums import ConnectionLimitStateType
from ..classes import Frame, TimeHistoryAnalysis
from ..scripts import compute_limit_states, import_time_history_analysis

from src.time_series_tools import spectral_acceleration

import model.paths as pth


def compute_gaps_dcr(frame: Frame,
                     limit_state: ConnectionLimitStateType) -> pd.DataFrame:
    """
    Computes the demand capacity ratios for connection limit states

    Args:
        frame (Frame): frame object
        limit_state (ConnectionLimitStateType): connection limit state

    Returns:
        pd.DataFrame: demand capacity ratios 
    """
    gap_openings = pd.read_csv(pth.GAP_OPENINGS_PROCESSED)
    
    limit_states = {
        'int_col': compute_limit_states(frame, frame.int_column_section),
        'ext_col': compute_limit_states(frame, frame.ext_column_section)
    }
    for storey in range(frame.n_storeys):
        limit_states[f'ext_beam_{storey + 1}'] = compute_limit_states(
            frame, 
            frame.beam_sections[storey]
        )
        limit_states[f'int_beam_{storey + 1}'] = compute_limit_states(
            frame, 
            frame.beam_sections[storey]
        )

    demand_capacity_ratios = pd.DataFrame()
    for key, item in limit_states.items():
        demand_capacity_ratios[key] = [
            gap/item.__dict__[limit_state] 
            if item.__dict__[limit_state] is not None else 0 
            for gap in gap_openings[key]
        ]

    return demand_capacity_ratios


def compute_failure_points(frame: Frame) -> List[bool]:
    """
    Computes the failure points considering as failed the DS2

    Args:
        frame (Frame): frame object

    Returns:
        List[bool]: failure points
    """
    gap_openings = compute_gaps_dcr(frame, 'DS2')
    DS2_edp = [max(row) for _, row in gap_openings.iterrows()]
    return [value >= 1 for value in DS2_edp]


def intensity_measure_as_SaT1(time_histories: List[TimeHistoryAnalysis],
                              first_period: float) -> List[float]:
    """
    Computes the intensity measures for a list of time history analysis using Sa(T1)

    Args:
        time_histories (List[TimeHistoryAnalysis]): time histories
        first_period (float): T1 for the spectral response

    Returns:
        List[float]: intensity measures
    """
    return [
        spectral_acceleration(
            time_series=np.loadtxt(pth.TIMESERIES_INPUT_FOLDER / time_history.filename),
            time_step=time_history.time_step,
            period=first_period
        ) for time_history in time_histories
    ]


def export_global_connections_dcr(frame: Frame) -> None:
    """Exports the data cloud points for global fragility model"""

    data = pd.DataFrame()

    DSs = ['DS1', 'DS2', 'DST']

    time_histories = import_time_history_analysis(pth.TIME_HISTORY_PATH)
    period = pd.read_csv(pth.MODAL_OUTPUT)['structure_periods'][0]

    data['time_history_id'] = list(range(1, len(time_histories) + 1))
    data['int_measure'] = intensity_measure_as_SaT1(time_histories, period)

    for ds in DSs:
        gap_openings = compute_gaps_dcr(frame, ds)
        data[ds] = [max(row) for _,row in gap_openings.iterrows()]

    data['failure'] = compute_failure_points(frame)

    data.to_csv(pth.DCR_PROCESSED, float_format='%.3f', index=False)

