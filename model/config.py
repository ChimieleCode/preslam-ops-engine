from pydantic import BaseModel
from pathlib import Path
from model.enums import Transformation


CONFIG_PATH = Path('./config.yaml')


class PerfOptions(BaseModel):
    processes: int


class AnalysisConfig(BaseModel):
    run_modal: bool
    run_pushpull: bool
    run_timehistory: bool
    run_IDA: bool


class MomentRotationOptions(BaseModel):
    pt_points: int
    use_GM: bool
    steel_failure: bool
    tendon_failure: bool
    beta: float


class ModelOptions(BaseModel):
    transformation: Transformation
    rigid_joints: bool
    rigid_factor: int
    rigid_link: int
    frame_damping: float


class IDAOptions(BaseModel):
    initial_int_measure: float
    initial_step: float
    max_iter_ida: int


class MNINTConfig(BaseModel):
    analysis: AnalysisConfig
    moment_rotation_options: MomentRotationOptions
    model_options: ModelOptions
    ida_options: IDAOptions
    performance_options: PerfOptions
