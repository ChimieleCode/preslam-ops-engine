from typing import Tuple
from ..classes import Section, Frame


def tendon_strain(theta: float, neutral_axis: float,
                  section: Section, frame: Frame) -> float:
    """
    Computes the tendon strain given neutral axis and theta

    Args:
        theta (float): rotation of connection
        neutral_axis (float): neutral axis depth (from top)   
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        float: strain value
    """
    tendon_delta = theta * (section.h/2 - neutral_axis)
    delta_strain = tendon_delta * 2*frame.n_spans / frame.tendon_unbonded_length
    return delta_strain + section.tendon_initial_strain


def steel_strain(theta: float, neutral_axis: float,
                 section: Section) -> Tuple[float]:
    """
    Computes the steel bar strain for bottom and top reinforcement

    Args:
        theta (float): rotation of connection
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section

    Returns:
        Tuple[float]: bottom strain, top strain
    """
    steel_bar_deltas = [
        theta * (section.bottom_reinforcement_depth - neutral_axis),
        theta * (section.top_reinforcement_depth - neutral_axis)
    ]
    return tuple(delta / section.bar_length for delta in steel_bar_deltas)


def timber_strain(theta: float, neutral_axis: float,
                  section: Section, frame: Frame) -> float:
    """
    Computes the timber strain of the section

    Args:
        theta (float): rotation of the connection
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section


    Returns:
        float: timber max strain
    """
    if section.is_beam:
        L_cant = .5 * (frame.span_length - frame.int_column_section.h)
    
    else:
        L_cant = .5 * (frame.storey_height - frame.beam_sections[0].h)
    
    return neutral_axis * 3*theta/L_cant


