
import os
import numpy as np

from pathlib import Path
from typing import List

import model.paths as pth

from ..utils import write_to_csv

def compute_gap_openings(save_path : Path) -> List[List[float]]:
    """
    Computes the gap openinfs and saves them in a csv file

    Args:
        save_path (Path): file path

    Returns:
        List[List[float]]: gap openings
    """
    

    max_gap_openings = list()

    for folder in os.listdir(pth.OUTPUT_TH_DIR_PATH):
        folder_path = pth.OUTPUT_TH_DIR_PATH / folder
        gap_openings_data = np.loadtxt(
            folder_path + '\\' + pth.GAP_OPENINGS_FILE
        )
        # first column is time and i need only odd positions
        gap_openings_time = np.transpose(np.diff(gap_openings_data))[1::2]
        max_gap_openings.append([np.max(abs(gaps)) for gaps in gap_openings_time])

    csv_out_data = [
        [folder] + gaps 
        for folder, gaps in zip(os.listdir(pth.OUTPUT_TH_DIR_PATH),
                                max_gap_openings)
    ]
    n_storeys = round(len(max_gap_openings[0])/2 - 1)
    ext_beam_header = [f'ext_beam_{i + 1}' for i in range(n_storeys)]
    int_beam_header = [f'int_beam_{i + 1}' for i in range(n_storeys)]
    csv_header = (
        ['Time_History', 'ext_col', 'int_col'] 
        + [val for pair in zip(ext_beam_header, int_beam_header) for val in pair]
    )
    write_to_csv(save_path, csv_out_data, csv_header)

    return max_gap_openings

