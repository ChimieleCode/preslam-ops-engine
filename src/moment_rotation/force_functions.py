from re import M
from typing import Tuple
from functools import cache
from ..classes import Section, Frame
from .strain_functions import steel_strain, tendon_strain, timber_strain


def tendon_force(theta: float, neutral_axis: float,
                 section: Section, frame: Frame) -> float:
    """
    Computes the tendon force

    Args:
        theta (float): rotation of connection
        neutral_axis (float): neutral axis depth (from top)   
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        float: force value
    """
    if section.tendon is not None:
        strain = tendon_strain(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        )
        return strain * section.tendon.E * section.post_tensioning_area

    else:
        return 0


def steel_force(theta: float, neutral_axis: float,
                 section: Section) -> Tuple[float]:
    """
    Computes the steel bar force for bottom and top reinforcement

    Args:
        theta (float): rotation of connection
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section

    Returns:
        Tuple[float]: bottom force, top force
    """
    strains = steel_strain(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section
    )
    return tuple(
        section.steel.stress_from_strain(strain) * section.steel_area 
        for strain in strains
    )


def timber_force(theta: float, neutral_axis: float,
                 section: Section, frame: Frame) -> float:
    """
    Computes the timber force of the section

    Args:
        theta (float): rotation of the connection
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section


    Returns:
        float: timber max force
    """
    strain = timber_strain(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    timber_limit_strain = section.timber.epsilon_lim(section.connection_stiffness_ratio)
    if strain <= timber_limit_strain:
        return .5 * section.connection_stiffness * strain * section.b * neutral_axis

    else:
        plastic_depth = max(
            0, 
            neutral_axis * (strain - timber_limit_strain)/timber_limit_strain
        )
        return (.5 * timber_limit_strain * section.connection_stiffness 
                * section.b * (plastic_depth + neutral_axis))


def force_inbalance(theta: float, neutral_axis: float,
                    section: Section, frame: Frame,
                    steel_failure: bool = False) -> float:
    """
    Computes the relative inbalance of forces in the section

    Args:
        theta (float): connection rotation
        neutral_axis (float): neutral axis depth (from top)
        section (Section): section
        frame (Frame): frame containing the section
        steel_failure (bool): consider the steel as failed
 
    Returns:
        float: force inbalance
    """
    timber_f = timber_force(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    tendon_f = tendon_force(
        theta=theta,
        neutral_axis=neutral_axis,
        section=section,
        frame=frame
    )
    if steel_failure:
        steel_fs = [0]
    
    else:
        steel_fs = steel_force(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section
        )
        
    return timber_f - sum(steel_fs) - tendon_f - section.axial_load



