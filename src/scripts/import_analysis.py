from pathlib import Path
from typing import List

import src.classes as cls
import model.validation as mdl
from ..utils import import_from_json


def import_pushpull_analysis(path : Path) -> cls.PushPullAnalysis:
    """
    Imports and validates the pushpull analysis options

    Args:
        path (Path): path of pushpull analysis input file

    Returns:
        PushPullAnalysis: pushpull analysis
    """
    validated_pushpull_analysis = mdl.PushPullInput(
        **import_from_json(
            path
        )
    )
    return cls.PushPullAnalysis(
        **validated_pushpull_analysis.__dict__
    )


def import_time_history_analysis(path : Path) -> List[cls.TimeHistoryAnalysis]:
    """
    Import a list of time history analyses

    Args:
        path (Path): path of timehistory input file

    Returns:
        List[TimeHistoryAnalysis]: list of THNL Cases
    """
    validated_time_histories = mdl.TimeHistoryCollectionInput(
        **import_from_json(
            path
        )
    )
    return [
        cls.TimeHistoryAnalysis(
            **validated_timehistory.__dict__
        )
        for validated_timehistory in validated_time_histories.NLTHCases
    ]