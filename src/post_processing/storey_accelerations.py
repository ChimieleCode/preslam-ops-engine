from pathlib import Path
from typing import List
import model.paths as pth
import os
import numpy as np

from ..classes import Frame
from ..utils import import_from_json, write_to_csv

G = 9.81


def compute_floor_accelerations(save_path: Path) -> List[List[float]]:
    """
    Computes storey accelerations and saves them in csv file

    Args:
        save_path (Path): csv file path

    Returns:
        List[List[float]]: storey_accelerations
    """
    max_accelerations = list()

    for folder in os.listdir(pth.OUTPUT_TH_DIR_PATH):
        folder_path = pth.OUTPUT_TH_DIR_PATH / folder
        floors_acc = np.loadtxt(
            folder_path / pth.STOREY_REL_ACC_FILE
        )
        base_acc = np.loadtxt(
            pth.TIMESERIES_INPUT_FOLDER / import_from_json(folder_path / pth.TH_STATS_FILE)['time_series_name']
        )
        absolute_acc = np.array([floor_acc + base for floor_acc, base in zip(floors_acc, base_acc)])
        max_storey_acc = np.array(
            # first column is time
            [np.max(storey)/G for storey in np.transpose(absolute_acc)[1:]]
        )
        max_accelerations.append(max_storey_acc)
    
    csv_out_data = [
        [folder] + list(accs)
        for folder, accs in zip(os.listdir(pth.OUTPUT_TH_DIR_PATH), max_accelerations)
    ]
    n_storeys = len(max_accelerations[0])
    csv_header = ['Time_History'] + list(range(n_storeys))
    write_to_csv(save_path, csv_out_data, csv_header)

    return max_accelerations
