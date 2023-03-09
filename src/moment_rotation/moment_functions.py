from .strain_functions import timber_strain
from .force_functions import steel_force, tendon_force

from ..classes import Section, Frame


def timber_resultant_depth(theta: float, neutral_axis: float,
                           section: Section, frame: Frame) -> float:
    """
    Get the depth of the timber compression resultant force

    Args:
        theta (float): theta
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        float: resultant depth
    """
    timber_epsilon = timber_strain(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    timber_epsilon_lim = section.timber.epsilon_lim(section.connection_stiffness_ratio)
    plastic_depth = max(
        0, 
        neutral_axis * (timber_epsilon - timber_epsilon_lim) / timber_epsilon_lim
    )
    return (
        (1/3 * (neutral_axis**2 - 2*plastic_depth**2 + plastic_depth * neutral_axis) 
            + plastic_depth**2)
        / (plastic_depth + neutral_axis)
    )


def steel_moment(theta: float, neutral_axis: float,
                 section: Section, frame: Frame) -> float:
    """
    Get the moment contribution of steel

    Args:
        theta (float): theta
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        float: moment
    """
    steel_f_bot, steel_f_top = steel_force(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section
    )
    moment_pole = timber_resultant_depth(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    return sum(
        [
            steel_f_top * (section.top_reinforcement_depth - moment_pole),
            steel_f_bot * (section.bottom_reinforcement_depth - moment_pole)
        ]
    )


def tendon_moment(theta: float, neutral_axis: float,
                  section: Section, frame: Frame) -> float:
    """
    Get the moment contribution of tendon

    Args:
        theta (float): theta
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        float: moment
    """
    tendon_f = tendon_force(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    moment_pole = timber_resultant_depth(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    return (.5*section.h - moment_pole) * tendon_f


def axial_moment(theta: float, neutral_axis: float,
                 section: Section, frame: Frame) -> float:
    """
    Get the moment contribution of axial load

    Args:
        theta (float): theta
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        float: moment
    """
    moment_pole = timber_resultant_depth(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    return (.5*section.h - moment_pole) * section.axial_load

