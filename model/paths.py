from pathlib import Path


# Input paths
###
FRAME_PATHS: dict[str, Path] = {
    'steel_path': Path("./input/steel.json"),
    'tendon_path': Path("./input/tendon.json"),
    'timber_path': Path("./input/timber.json"),
    'frame_path': Path("./input/frame.json")
}
###
PUSHOVER_PATH: Path = Path('./input/pushover.json')
TIME_HISTORY_PATH: Path = Path('./input/time_history.json')
TIME_HISTORY_IDA_PATH: Path = Path('./input/time_history_IDA.json')

MODEL_OUTPUT_PATH: Path = Path('./output/model.json')

# Modal
MODAL_OUTPUT: Path = Path('./output/modal.csv')

# Pushpull Paths
###
OUTPUT_PUSHPULL_DIR_PATH: Path = Path('./output/pushpull')

BASE_REACTIONS_FILE: str = 'base_reactions.txt'
STOREY_DISPS_FILE: str = 'storey_disps.txt'

# Timehistory Paths
###
OUTPUT_TH_DIR_PATH: Path = Path('./output/time_history')
###
TIMESERIES_INPUT_FOLDER: Path = Path('./time_series')
IDA_TIMESERIES_INPUT_FOLDER: Path = Path('./time_series_IDA')

STOREY_DISPS_FILE: str = STOREY_DISPS_FILE
STOREY_REL_ACC_FILE: str = 'storey_acc.txt'
GAP_OPENINGS_FILE: str = 'gap_openings.txt'
TH_STATS_FILE: str = 'stats.json'

# Output Files and processed
HDF5_FILE_PATH: Path = Path('./output/model_data.hdf5')
LIMIT_STATE_GAP_VALUES: Path = Path('./output/section_limit_states.csv')
GAP_OPENINGS_PROCESSED: Path = Path('./output/gap_openings.csv')
STOREY_DRIFTS_PROCESSED: Path = Path('./output/storey_drifts.csv')
FLOOR_ACCELERATIONS: Path = Path('./output/storey_acc.csv')
DCR_PROCESSED: Path = Path('./output/cloud_data.csv')

# Logging not working yet
LOGGING_CONF = './logging.conf'
