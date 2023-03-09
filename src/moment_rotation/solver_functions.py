from typing import Iterable, List, Tuple
from scipy.optimize import fsolve

from ..classes import Section, Frame

from .strain_functions import steel_strain, tendon_strain, timber_strain
from .force_functions import force_inbalance


def steel_yielding(initial_guess: Iterable, section: Section,
                   frame: Frame) -> Tuple[float]:
    """
    Computes the neutral axis and theta at steel yielding

    Args:
        initial_guess (Iterable): initial guess of theta and neutral axis
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        Tuple[float]: theta, neutral_axis
    """
    def objective_yielding(guess : Iterable) -> List[float]:
        """
        objective function for steel yielding

        Args:
            guess (Iterable): theta, neutral axis

        Returns:
            List[float]: balances
        """
        theta = guess[0]
        neutral_axis = guess[1]
        force_balance = force_inbalance(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        ) 
        steel_epsilon = steel_strain(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section
        )[0] # bottom bar
        steel_strain_balance = steel_epsilon - section.steel.epsilon_y
        return [
            force_balance,
            steel_strain_balance
        ]
    
    return fsolve(objective_yielding, initial_guess, xtol=10**-3, maxfev=10**4)


def steel_failure(initial_guess : Iterable, section : Section, 
                   frame : Frame) -> Tuple[float]:
    """
    Computes the neutral axis and theta at steel failure

    Args:
        initial_guess (Iterable): initial guess of theta and neutral axis
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        Tuple[float]: theta, neutral_axis
    """
    def objective_failure(guess : Iterable) -> List[float]:
        """
        objective function for steel failure

        Args:
            guess (Iterable): theta, neutral axis

        Returns:
            List[float]: balances
        """
        theta = guess[0]
        neutral_axis = guess[1]
        force_balance = force_inbalance(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        ) 
        steel_epsilon = steel_strain(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section
        )[0] # bottom bar
        steel_strain_balance = steel_epsilon - section.steel.epsilon_u
        return [
            force_balance,
            steel_strain_balance
        ]

    return fsolve(objective_failure, initial_guess, xtol=10**-6, maxfev=10**4)


def tendon_failure(initial_guess : Iterable, section : Section, 
                   frame : Frame) -> Tuple[float]:
    """
    Computes the neutral axis and theta at tendon failure

    Args:
        initial_guess (Iterable): initial guess of theta and neutral axis
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        Tuple[float]: theta, neutral_axis
    """
    def objective_tendon(guess: Iterable) -> List[float]:
        """
        objective function for tendon failure

        Args:
            guess (Iterable): theta, neutral axis

        Returns:
            List[float]: balances
        """
        theta = guess[0]
        neutral_axis = guess[1]
        force_balance = force_inbalance(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame,
            steel_failure=True
        ) 
        tendon_epsilon = tendon_strain(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        )
        tendon_strain_balance = tendon_epsilon - section.tendon.epsilon_y
        return [
            force_balance,
            tendon_strain_balance
        ]

    return fsolve(objective_tendon, initial_guess, xtol=10**-6, maxfev=10**4)


def timber_yielding(initial_guess: Iterable, section: Section,
                    frame: Frame) -> Tuple[float]:
    """
    Computes the neutral axis and theta at timber yielding

    Args:
        initial_guess (Iterable): initial guess of theta and neutral axis
        section (Section): section
        frame (Frame): frame containing the section

    Returns:
        Tuple[float]: theta, neutral_axis
    """
    def objective_timber(guess: Iterable) -> List[float]:
        """
        objective function for timber yielding

        Args:
            guess (Iterable): theta, neutral axis

        Returns:
            List[float]: balances
        """
        theta = guess[0]
        neutral_axis = guess[1]
        force_balance = force_inbalance(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        ) 
        timber_epsilon = timber_strain(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        )
        timber_strain_balance = (
            timber_epsilon - section.timber.epsilon_lim(section.connection_stiffness_ratio)
        )
        return [
            force_balance,
            timber_strain_balance
        ]

    return fsolve(objective_timber, initial_guess, xtol=10**-6, maxfev=10**4)


def get_neutral_axis(initial_guess: Iterable, theta: float,
                     section: Section, frame: Frame) -> Tuple[float]:
    """
    Computes the neutral axis at a given theta

    Args:
        initial_guess (float): neutral axis initial guess
        theta (float): connection rotation
        section (Section): section
        frame (Frame): frame containing section

    Returns:
        Tuple[float]: neutral axis
    """
    def objective_equilibrium(guess: Iterable) -> List[float]:
        """
        objective function for equilibrium

        Args:
            guess (Iterable): neutral axis

        Returns:
            List[float]: balances
        """
        neutral_axis = guess[0]
        force_balance = force_inbalance(
            theta=theta,
            neutral_axis=neutral_axis,
            section=section,
            frame=frame
        ) 
        return [
            force_balance
        ]

    return fsolve(objective_equilibrium, initial_guess, xtol=10**-6, maxfev=10**4)



  


    