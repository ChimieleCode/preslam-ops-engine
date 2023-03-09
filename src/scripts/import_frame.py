from pathlib import Path

import src.classes as cls
import model.validation as mdl
from ..utils import import_from_json, import_configuration

# Import config data
import model.config as config

cfg: config.MNINTConfig
cfg = import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)


def import_frame_data(frame_path: Path, steel_path: Path, tendon_path: Path, timber_path: Path) -> cls.Frame:
    """
    Imports the json files and builds the Frame object

    Args:
        frame_path (Path): path to frame input file
        steel_path (Path): path to steel input file
        tendon_path (Path): path to tendon input file
        timber_path (Path): path to timber input file

    Returns:
        Frame: frame object
    """
    # Validation
    validated_timber = mdl.TimberInput(
        **import_from_json(
            timber_path
        )
    )
    validated_steel = mdl.SteelInput(
        **import_from_json(
            steel_path
        )
    )
    validated_tendon = mdl.TendonInput(
        **import_from_json(
            tendon_path
        )
    )
    validated_frame = mdl.RegularFrameInput(
        **import_from_json(
            frame_path
        )
    )

    # Build frame object
    timber = cls.Timber(
        **validated_timber.__dict__
    )
    steel = cls.Steel(
        **validated_steel.__dict__
    )
    tendon = cls.Tendon(
        **validated_tendon.__dict__
    )
    section_factory = cls.SectionFactory(
        timber=timber,
        tendon=tendon,
        steel=steel,
        validated_sections=validated_frame.sections
    )

    return cls.Frame(
        validated_frame=validated_frame,
        section_factory=section_factory,
        damping=cfg.model_options.frame_damping
    )
