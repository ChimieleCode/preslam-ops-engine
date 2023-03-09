from pathlib import Path
from multiprocessing import Pool

import src.scripts as scr
import src.analysis_definition as analyze
import src.hdf5_exporter as exhdf5
import src.utils as util
import model.paths as pth

# Import config data
import model.config as config
 
cfg: config.MNINTConfig
cfg = util.import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)


# Picklable function IDA
def run_incremental_dynamic(time_history) -> None:
    """This function performs a single IDA"""
    frame = scr.import_frame_data(**pth.FRAME_PATHS)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    structure_periods = analyze.run_modal_analysis(frame)
    analyze.run_incremental_dynamic_analysis(
        frame=frame,
        time_history_analysis=time_history,
        structure_periods=structure_periods
    )


# Picklable function TH
def run_time_history(time_history) -> bool:
    """This function performs a single TH"""
    frame = scr.import_frame_data(**pth.FRAME_PATHS)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    structure_periods = analyze.run_modal_analysis(frame)
    status = analyze.run_time_history_analysis(
        frame=frame,
        time_history_analysis=time_history,
        structure_periods=structure_periods
    )
    # returns if the analysis Failed
    return status


def main():

    frame = scr.import_frame_data(**pth.FRAME_PATHS)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    scr.print_model(pth.MODEL_OUTPUT_PATH)
    scr.export_limit_states(frame, pth.LIMIT_STATE_GAP_VALUES)

    # Modal analysis is run if a TH is also performed
    if cfg.analysis.run_modal or cfg.analysis.run_timehistory or cfg.analysis.run_IDA:
        structure_periods = analyze.run_modal_analysis(frame)
        print(structure_periods)

    # Pushover
    if cfg.analysis.run_pushpull:
        pushpull_analysis = scr.import_pushpull_analysis(pth.PUSHOVER_PATH)
        analyze.run_pushpull_analysis(
            frame, 
            pushpull_analysis, 
            force_pattern=frame.inelastic_shape
        )
        # Export Results
        exhdf5.export_PH_to_HDF5(
            pushover_folder=Path('./output/pushpull'),
            hdf5_save_path=Path('./output/PH.hdf5')
        )

    # TIME HISTORY MULTI PROCESSING
    if cfg.analysis.run_timehistory:
        timehistory_analyses = scr.import_time_history_analysis(Path(pth.TIME_HISTORY_PATH))
        util.clean_directory(Path(pth.OUTPUT_TH_DIR_PATH))

        with Pool(processes=cfg.performance_options.processes) as pool:
            state = pool.map(run_time_history, timehistory_analyses)
            # Status output
            util.export_to_json(
                filepath=Path('./output/time_history/status.json'),
                data=dict(
                    zip(
                        range(1, len(state) + 1),
                        state
                    )
                )
            )
        # Export TH
        exhdf5.export_CLOUD_to_HDF5(
            time_history_folder=Path('./output/time_history'),
            hdf5_save_path=Path('./output/CLOUD.hdf5'),
            time_history_input_data=Path('./input/time_history.json')
        )

    # IDA
    if cfg.analysis.run_IDA:
        timehistory_analyses = scr.import_time_history_analysis(Path('./input/time_history_IDA.json'))
        util.clean_directory(Path('./output/IDA'))

        with Pool(processes=cfg.performance_options.processes) as pool:
            pool.map(run_incremental_dynamic, timehistory_analyses)
        # Export IDA
        exhdf5.export_IDA_to_HDF5(
            time_history_folder=Path('./output/IDA'),
            hdf5_save_path=Path('./output/IDA.hdf5'),
            time_history_input_data=Path('./input/time_history_IDA.json')
        )


# Profile Mode
if __name__ == '__main__':
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        main()

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()