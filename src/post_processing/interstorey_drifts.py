from pathlib import Path
from typing import List
import model.paths as pth
import os
import numpy as np

from ..utils import write_to_csv


def compute_interstorey_drifts(save_path: Path) -> List[List[float]]:
    """
    Computes interstorey drifts and saves them in csv file

    Args:
        save_path (Path): csv file path

    Returns:
        List[List[float]]: interstorey drifts
    """
    interstorey_drifts = list()

    for folder in os.listdir(pth.OUTPUT_TH_DIR_PATH):
        folder_path = pth.OUTPUT_TH_DIR_PATH / folder
        storey_disps = np.loadtxt(
            folder_path / pth.STOREY_DISPS_FILE
        )
        interstorey_drifts_time = abs(np.transpose(np.diff(storey_disps))[1:])
        interstorey_drifts.append(
            [np.max(storey_drifts) for storey_drifts in interstorey_drifts_time]
        )

    csv_out_data = [
        [folder] + drifts 
        for folder, drifts in zip(os.listdir(pth.OUTPUT_TH_DIR_PATH),
                                  interstorey_drifts)
    ]
    n_storeys = len(interstorey_drifts[0])
    csv_header = ['Time_History'] + list(range(1, n_storeys + 1))
    write_to_csv(save_path, csv_out_data, csv_header)

    return interstorey_drifts
