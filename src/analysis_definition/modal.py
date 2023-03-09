from typing import List

import openseespy.opensees as ops
import time
import math

import model.paths as pth

from ..classes import Frame
from ..utils import write_to_csv


def run_modal_analysis(frame: Frame, save_data: bool = False) -> List[float]:
    """
    Runs a modal analysis

    Args:
        frame (Frame): Frame object
        save_data (bool): save data as csv. Defaults to False.

    Returns:
        Tuple[float]: Modal periods
    """ 
    print('-o-o-o- Modal Analysis Started -o-o-o-' )
    start_t = time.perf_counter()

    # analysis options
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGen')
    ops.test('NormDispIncr', 10**-6, 25, 0, 1)
    ops.algorithm('Newton')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')

    if frame.n_storeys > 2:
        eigen_values = ops.eigen('-genBandArpack', frame.n_storeys - 1)
    else:
        eigen_values = ops.eigen('-fullGenLapack', frame.n_storeys)

    ops.wipeAnalysis()
    end_t = time.perf_counter()
    total_time = end_t - start_t
    print(f'-o-o-o- Modal Analysis Completed in {total_time:.2f}s -o-o-o-' )

    periods = [
        2*math.pi / math.sqrt(eigen_value) for eigen_value in eigen_values
    ]
    if save_data:
        write_to_csv(
            file_path=pth.MODAL_OUTPUT,
            data=zip(periods), 
            header=['structure_periods']
        )
        
    return periods
        