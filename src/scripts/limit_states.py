import pandas as pd
import numpy as np
from pathlib import Path

from ..classes import Section, SectionLimitStates, Frame
from ..moment_rotation import timber_yielding, steel_failure, tendon_failure


def compute_limit_states(frame: Frame,
                         section: Section) -> SectionLimitStates:
    """
    Computes the limit states of the section

    Args:
        frame (Frame): frame containing the section
        section (Section): section

    Returns:
        SectionLimitStates: section limit states
    """
    limit_states = {
        'DS1': steel_failure(
            initial_guess=[0.02, 0.2],
            section=section,
            frame=frame
        )[0],
        'DS2': None,
        'DST': timber_yielding(
            initial_guess=[0.03, 0.1],
            section=section,
            frame=frame
        )[0]
    }
    if section.tendon is not None:
        limit_states['DS2'] = tendon_failure(
            initial_guess=[0.05, 0.1],
            section=section,
            frame=frame
        )[0]
        
    return SectionLimitStates(**limit_states)


def export_limit_states(frame: Frame,
                        path: Path) -> None:
    """
    Computes and saves the limit states for every section

    Args:
        frame (Frame): frame
        path (Path): file path

    Returns:
        SectionLimitStates: section limit states
    """
    sections = [
        frame.ext_column_section,
        frame.int_column_section
    ] + frame.beam_sections
    # print(sections)

    frame_gap_limit_states = pd.DataFrame()
    for field in SectionLimitStates.__annotations__.keys():
        frame_gap_limit_states[field] = np.zeros(len(sections))

    for i, section in enumerate(sections):
        limit_states = compute_limit_states(frame, section)
        for key, value in limit_states.__dict__.items():
            frame_gap_limit_states[key][i] = value
        
    frame_gap_limit_states.to_csv(path, index=False)
