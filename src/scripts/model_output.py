from pathlib import Path
import openseespy.opensees as ops


def print_model(path: Path) -> None:
    """
    Saves the opensees model as a json file

    Args:
        path (Path): path to output
    """
    ops.printModel(
        '-JSON',
        '-file',
        path.__str__()
    )
    