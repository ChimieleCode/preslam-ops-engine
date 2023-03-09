import h5py
import os
import numpy as np
import pandas as pd
from pathlib import Path

import model.paths as pth
from model.validation import PushPullInput, TimeHistoryCollectionInput

from ..utils import import_from_json
from ..classes import Frame


def hdf5_create_dataset(hdf5file: h5py.File, dataset_path: str, data: np.array, metadata: dict = None) -> h5py.Dataset:
    """
    Creates a dataset in a hdf5 file with attributes

    Args:
        hdf5file (h5py.File): hdf5 file object
        dataset_path (str): dataset hdf5 path
        data (np.array): n-dimensional numpy array
        metadata (dict, optional): metadata as dictionary. Defaults to None.

    Returns:
        h5py.Dataset: dataset created
    """
    dataset = hdf5file.create_dataset(
        dataset_path,
        data=data
    )
    if metadata is not None:
        for key, value in metadata.items():
            dataset.attrs[key] = value
    
    return dataset


def hdf5_create_group(hdf5file: h5py.File, group_path: str, metadata: dict = None) -> h5py.Group:
    """
    Creates a group in a hdf5 file with attributes

    Args:
        hdf5file (h5py.File): hdf5 file object
        group_path (str): group hdf5 path
        metadata (dict, optional): metadata as dictionary. Defaults to None.

    Returns:
        h5py.Group: _description_
    """
    group = hdf5file.create_group(
        group_path
    )
    if metadata is not None:
        for key, value in metadata.items():
            group.attrs[key] = value
    
    return group


def save_output_in_hdf5(frame: Frame) -> None:
    """
    Compresses all the cases outputs in a hdf5 format

    Args:
        frame (Frame): frame data object
    """

    push_pull_data = PushPullInput(
        **import_from_json(pth.PUSHOVER_PATH)
    )

    time_history_data = TimeHistoryCollectionInput(
        **import_from_json(pth.TIME_HISTORY_PATH)
    )

    # Removes the previous file
    os.remove(Path('./output/model_data.hdf5'))
    with h5py.File(Path('./output/model_data.hdf5'), 'w') as f:

        # Modal
        modal = pd.read_csv(pth.MODAL_OUTPUT)
        modal_metadata = {
            'count': len(modal['structure_periods']),
            'units': 's'
        }
        hdf5_create_dataset(
            f,
            'mode_periods',
            data=modal['structure_periods'],
            metadata=modal_metadata
        )

        # Time History
        th_group_metadata = {
            'count': len(time_history_data.NLTHCases),
            'floors': frame.n_storeys,
            'interstorey_heights': [frame.storey_height] * frame.n_storeys
        }
        hdf5_create_group(
            f,
            'time_history',
            metadata=th_group_metadata
        )

        for folder, time_history in zip(os.listdir(pth.OUTPUT_TH_DIR_PATH),
                                        time_history_data.NLTHCases):

            folder_path = pth.OUTPUT_TH_DIR_PATH / folder
            # group and attributes for time history case
            th_case_metadata = {
                'id': time_history.id,
                'success': import_from_json(
                        folder_path / pth.TH_STATS_FILE
                    )['success'],
                'time_step': time_history.time_step,
                'scale_factor': time_history.scale_factor,
                'time_step_ratio': time_history.time_step_ratio
            }
            hdf5_create_group(
                f,
                f'time_history/{folder}',
                metadata=th_case_metadata
            )
            # ground motion used for time history case
            ground_motion = np.loadtxt(
                pth.TIMESERIES_INPUT_FOLDER / time_history.filename,
                dtype='f'
            )
            ground_motion_metadata = {
                'duration': time_history.duration,
                'time_step': time_history.time_step,
                'unit': 'm/s2'
            }
            hdf5_create_dataset(
                f,
                f'time_history/{folder}/ground_motion',
                data=ground_motion,
                metadata=ground_motion_metadata
            )
            # recorded absolute storey displacements
            storey_disps = np.loadtxt(
                folder_path / pth.STOREY_DISPS_FILE,
                dtype='f'
            )
            storey_disps_metadata = {
                'units': 'm'
            }
            hdf5_create_dataset(
                f,
                f'time_history/{folder}/storey_disps',
                data=storey_disps[:, 1:],
                metadata=storey_disps_metadata
            )
            # recorded gap openings
            gap_openings = np.loadtxt(
                folder_path / pth.GAP_OPENINGS_FILE
            )
            gap_opnenings_metadata = {
                'units': 'rad',
                'format': [
                    'ext_col',
                    'int_col',
                    'ext_beam_i',
                    'int_beam_i'
                ]
            }
            hdf5_create_dataset(
                f,
                f'time_history/{folder}/section_gaps',
                data=gap_openings[:, 1:],
                metadata=gap_opnenings_metadata
            )
            # recorded relative floor accelerations
            storey_acc = np.loadtxt(
                folder_path / pth.STOREY_REL_ACC_FILE,
                dtype='f'
            )
            storey_acc_metadata = {
                'units': 'm/s2',
                'note': 'relative'
            }
            hdf5_create_dataset(
                f,
                f'time_history/{folder}/storey_accs',
                data=storey_acc[:, 1:],
                metadata=storey_acc_metadata
            )

        # Push Pulls
        push_pull_metadata = push_pull_data.__dict__
        push_pull_metadata['masses'] = frame.masses
        push_pull_metadata['frames'] = frame.n_frames
        push_pull_metadata['heights'] = list(np.arange(1, frame.n_storeys + 1) * frame.storey_height)
        hdf5_create_group(
            f,
            'push_pull',
            metadata=push_pull_metadata
        )
        # pushpull base reactions
        base_reactions = np.loadtxt(
            pth.OUTPUT_PUSHPULL_DIR_PATH / pth.BASE_REACTIONS_FILE,
            dtype='f'
        )
        base_reactions_metadata = {
            'units': 'kN'
        }
        hdf5_create_dataset(
            f,
            f'push_pull/base_reactions',
            data=base_reactions[:, 1:],
            metadata=base_reactions_metadata
        )

        storey_disps = np.loadtxt(
            pth.OUTPUT_PUSHPULL_DIR_PATH / pth.STOREY_DISPS_FILE,
            dtype='f'
        )
        storey_disps_metadata = {
            'units': 'm'
        }
        hdf5_create_dataset(
            f,
            f'push_pull/push_pull_disps',
            data=storey_disps[:, 1:],
            metadata=storey_disps_metadata
        )

        # Limit States
        section_limit_states = pd.read_csv(pth.LIMIT_STATE_GAP_VALUES)
        limit_state_gaps = section_limit_states.to_numpy()
        limit_states_metadata = {
            'units': 'rad',
            'rows': [
                'ext_col',
                'int_col',
                'beam_i'
            ],
            'columns': [
                'DS1',
                'DS2',
                'DST'
            ]
        }
        hdf5_create_dataset(
            f,
            'section_limit_states',
            data=limit_state_gaps,
            metadata=limit_states_metadata
        )
        