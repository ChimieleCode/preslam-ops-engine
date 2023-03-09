import h5py
import os
import numpy as np
import pandas as pd
from pathlib import Path


def hdf5_create_dataset(hdf5file: h5py.File,
                        dataset_path: str,
                        data: np.ndarray,
                        metadata: dict = None) -> h5py.Dataset:
    """
    Creates an hdf5 dataset with attributes
    :param hdf5file: file hdf5
    :param dataset_path: path to dataset in hdf5
    :param data: data as ndarray
    :param metadata: metadata as dictionary
    :return: dataset created
    """
    dataset = hdf5file.create_dataset(
        dataset_path,
        data=data
    )
    if metadata is not None:
        for key, value in metadata.items():
            dataset.attrs[key] = value

    return dataset


def hdf5_create_group(hdf5file: h5py.File,
                      group_path: str,
                      metadata: dict = None) -> h5py.Group:
    """
    Creates a group in a hdf5 file
    :param hdf5file: hdf5 file
    :param group_path: path to group in hdf5
    :param metadata: metadata as dict
    :return: created group
    """
    group = hdf5file.create_group(
        group_path
    )
    if metadata is not None:
        for key, value in metadata.items():
            group.attrs[key] = value

    return group


def export_CLOUD_to_HDF5(time_history_folder: Path,
                         hdf5_save_path: Path,
                         time_history_input_data: Path) -> None:
    """
    Exports time history result data from cloud analysis to hdf5 format
    :param time_history_folder: path to time history output folder
    :param hdf5_save_path: path to hdf5 file
    :param time_history_input_data: path to time history input folder
    :return: None
    """
    import model.paths as pth
    from src.utils import import_from_json

    # removes existing file if present
    if hdf5_save_path.exists():
        os.remove(hdf5_save_path)
    with h5py.File(hdf5_save_path, 'w') as hdf5_file:

        # Modal data
        modal_path = time_history_folder.parent / 'modal.csv'
        if modal_path.exists():
            modal = pd.read_csv(modal_path).to_numpy()
            MODAL_METADATA = {
                'units': 'seconds'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='modal',
                data=modal.astype(float),
                metadata=MODAL_METADATA
            )

        # Limit States
        limit_states_path = time_history_folder.parent / 'section_limit_states.csv'
        if limit_states_path.exists():
            limit_states_dataframe = pd.read_csv(limit_states_path)
            LS_METADATA = {
                'units': 'rad',
                'columns': list(limit_states_dataframe.keys().values)
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='limit_states',
                data=limit_states_dataframe.to_numpy().astype(float),
                metadata=LS_METADATA
            )

        # Time history cases
        time_histories = import_from_json(time_history_input_data)['NLTHCases']
        th_status = import_from_json(time_history_folder / 'status.json')
        for (key, status), time_history in zip(th_status.items(), time_histories):
            time_history['success'] = status
            th_case_name = f'TH_{int(key):04}'
            folder_path = time_history_folder / th_case_name
            hdf5_create_group(
                hdf5file=hdf5_file,
                group_path=th_case_name,
                metadata=time_history
            )

            # Time history timeseries
            time_series_path = Path(pth.TIMESERIES_INPUT_FOLDER) / time_history['filename']
            TIMESERIES_METADATA = {
                'units': 'meters/seconds^2',
                'type': 'absolute'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path=th_case_name + '/time_series',
                data=np.loadtxt(time_series_path),
                metadata=TIMESERIES_METADATA
            )

            # Displacements
            displacements_file_path = folder_path / Path(pth.STOREY_DISPS_FILE)
            if displacements_file_path.exists():
                DISP_METADATA = {
                    'units': 'meters',
                    'type': 'absolute'
                }
                hdf5_create_dataset(
                    hdf5file=hdf5_file,
                    dataset_path=th_case_name + '/displacements',
                    data=np.loadtxt(displacements_file_path),
                    metadata=DISP_METADATA
                )

            # Accelerations
            accelerations_file_path = folder_path / Path(pth.STOREY_REL_ACC_FILE)
            if accelerations_file_path.exists():
                ACC_METADATA = {
                    'units': 'meters/seconds^2',
                    'type': 'relative'
                }
                hdf5_create_dataset(
                    hdf5file=hdf5_file,
                    dataset_path=th_case_name + '/accelerations',
                    data=np.loadtxt(accelerations_file_path),
                    metadata=ACC_METADATA
                )

            # Gap Openings
            gap_openings_file_path = folder_path / Path(pth.GAP_OPENINGS_FILE)
            if gap_openings_file_path.exists():
                GAP_OPENINGS_METADATA = {
                    'units': 'rad'
                }
                hdf5_create_dataset(
                    hdf5file=hdf5_file,
                    dataset_path=th_case_name + '/gap_openings',
                    data=np.loadtxt(gap_openings_file_path),
                    metadata=GAP_OPENINGS_METADATA
                )

            # Base Reactions
            base_reactions_file_path = folder_path / Path(pth.BASE_REACTIONS_FILE)
            if base_reactions_file_path.exists():
                BASE_REACTIONS_METADATA = {
                    'units': 'kilo newtons'
                }
                hdf5_create_dataset(
                    hdf5file=hdf5_file,
                    dataset_path=th_case_name + '/base_reactions',
                    data=np.loadtxt(base_reactions_file_path),
                    metadata=BASE_REACTIONS_METADATA
                )


def export_IDA_to_HDF5(time_history_folder: Path,
                       hdf5_save_path: Path,
                       time_history_input_data: Path) -> None:
    """
    Exports time history result data from IDA analysis to hdf5 format
    :param time_history_folder: path to time history output folder
    :param hdf5_save_path: path to hdf5 file
    :param time_history_input_data: path to time history input folder
    :return: None
    """
    import model.paths as pth
    from src.utils import import_from_json

    # removes existing file if present
    if hdf5_save_path.exists():
        os.remove(hdf5_save_path)
    with h5py.File(hdf5_save_path, 'w') as hdf5_file:

        # Modal data
        modal_path = time_history_folder.parent / 'modal.csv'
        if modal_path.exists():
            modal = pd.read_csv(modal_path).to_numpy()
            MODAL_METADATA = {
                'units': 'seconds'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='modal',
                data=modal.astype(float),
                metadata=MODAL_METADATA
            )

        # Time history cases
        time_histories = import_from_json(time_history_input_data)['NLTHCases']
        for i, time_history in enumerate(time_histories):
            th_case_name = f'TH_{int(i + 1):04}'
            folder_path = time_history_folder / th_case_name
            hdf5_create_group(
                hdf5file=hdf5_file,
                group_path=th_case_name,
                metadata=time_history
            )

            # Time history timeseries
            time_series_path = Path(pth.IDA_TIMESERIES_INPUT_FOLDER) / time_history['filename']
            TIMESERIES_METADATA = {
                'columns': 'meters/seconds^2',
                'type': 'absolute'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path=th_case_name + '/time_series',
                data=np.loadtxt(time_series_path),
                metadata=TIMESERIES_METADATA
            )

            # IDA results
            ida_results_path = Path('./output/IDA') / th_case_name / 'ida_results.csv'
            if ida_results_path.exists():
                ida_dataframe = pd.read_csv(ida_results_path, index_col=0)
                IDA_METADATA = {
                    'columns': list(ida_dataframe.keys().values)
                }
                hdf5_create_dataset(
                    hdf5file=hdf5_file,
                    dataset_path=th_case_name + '/ida_results',
                    data=ida_dataframe.to_numpy().astype(float),
                    metadata=IDA_METADATA
                )

            for j, case_folder in enumerate(os.listdir(folder_path)):
                # Skips the 0 case which is related to json file
                if j == 0:
                    continue

                scale_case_name = f'run_{int(j):04}'
                scale_case_hdf5_path = th_case_name + '/' + scale_case_name
                case_path = folder_path / scale_case_name
                case_stats = import_from_json(case_path / 'stats.json')
                IDA_CASE_METADATA = {
                    'runtime': case_stats['time'],
                    'success': case_stats['success'],
                }
                hdf5_create_group(
                    hdf5file=hdf5_file,
                    group_path=scale_case_hdf5_path,
                    metadata=IDA_CASE_METADATA
                )

                # Displacements
                displacements_file_path = case_path / Path(pth.STOREY_DISPS_FILE)
                if displacements_file_path.exists():
                    DISP_METADATA = {
                        'units': 'meters',
                        'type': 'absolute'
                    }
                    hdf5_create_dataset(
                        hdf5file=hdf5_file,
                        dataset_path=scale_case_hdf5_path + '/displacements',
                        data=np.loadtxt(displacements_file_path),
                        metadata=DISP_METADATA
                    )

                # Accelerations
                accelerations_file_path = case_path / Path(pth.STOREY_REL_ACC_FILE)
                if accelerations_file_path.exists():
                    ACC_METADATA = {
                        'units': 'meters/seconds^2',
                        'type': 'relative'
                    }
                    hdf5_create_dataset(
                        hdf5file=hdf5_file,
                        dataset_path=scale_case_hdf5_path + '/accelerations',
                        data=np.loadtxt(accelerations_file_path),
                        metadata=ACC_METADATA
                    )

                # Gap Openings
                gap_openings_file_path = case_path / Path(pth.GAP_OPENINGS_FILE)
                if gap_openings_file_path.exists():
                    GAP_OPENINGS_METADATA = {
                        'units': 'rad'
                    }
                    hdf5_create_dataset(
                        hdf5file=hdf5_file,
                        dataset_path=scale_case_hdf5_path + '/gap_openings',
                        data=np.loadtxt(gap_openings_file_path),
                        metadata=GAP_OPENINGS_METADATA
                    )

                # Base Reactions
                base_reactions_file_path = case_path / Path(pth.BASE_REACTIONS_FILE)
                if base_reactions_file_path.exists():
                    BASE_REACTIONS_METADATA = {
                        'units': 'kilo newton'
                    }
                    hdf5_create_dataset(
                        hdf5file=hdf5_file,
                        dataset_path=scale_case_hdf5_path + '/base_reactions',
                        data=np.loadtxt(base_reactions_file_path),
                        metadata=BASE_REACTIONS_METADATA
                    )


def export_PH_to_HDF5(pushover_folder: Path,
                      hdf5_save_path: Path) -> None:
    """
    Exports pushover analysis results to hdf5 format
    :param pushover_folder: path to pushover-pushpull output folder
    :param hdf5_save_path: path to hdf5 file
    :return: None
    """
    import model.paths as pth
    from src.utils import import_from_json

    # removes existing file if present
    if hdf5_save_path.exists():
        os.remove(hdf5_save_path)
    with h5py.File(hdf5_save_path, 'w') as hdf5_file:
        # Limit States
        limit_states_path = pushover_folder.parent / 'section_limit_states.csv'
        if limit_states_path.exists():
            limit_states_dataframe = pd.read_csv(limit_states_path)
            LS_METADATA = {
                'units': 'rad',
                'columns': list(limit_states_dataframe.keys().values)
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='limit_states',
                data=limit_states_dataframe.to_numpy().astype(float),
                metadata=LS_METADATA
            )

        # Displacements
        displacements_file_path = pushover_folder / Path(pth.STOREY_DISPS_FILE)
        if displacements_file_path.exists():
            DISP_METADATA = {
                'units': 'meters',
                'type': 'absolute'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='displacements',
                data=np.loadtxt(displacements_file_path),
                metadata=DISP_METADATA
            )

        # Gap Openings
        gap_openings_file_path = pushover_folder / Path(pth.GAP_OPENINGS_FILE)
        if gap_openings_file_path.exists():
            GAP_OPENINGS_METADATA = {
                'units': 'rad'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='gap_openings',
                data=np.loadtxt(gap_openings_file_path),
                metadata=GAP_OPENINGS_METADATA
            )

        # Base Reactions
        base_reactions_file_path = pushover_folder / Path(pth.BASE_REACTIONS_FILE)
        if base_reactions_file_path.exists():
            BASE_REACTIONS_METADATA = {
                'units': 'kilo newtons'
            }
            hdf5_create_dataset(
                hdf5file=hdf5_file,
                dataset_path='base_reactions',
                data=np.loadtxt(base_reactions_file_path),
                metadata=BASE_REACTIONS_METADATA
            )
