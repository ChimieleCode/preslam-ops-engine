import openseespy.opensees as ops
from model.enums import Transformation


def model_initialize() -> None:
    """
    Initialize the model
    """
    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)


def model_time_series() -> None:
    """
    Define a time series
    """
    ops.timeSeries('Linear', 1, '-factor', 1.)


def model_transformation():
    """
    Define geometry transformation
    """
    ops.geomTransf('Linear', Transformation.Linear)
    ops.geomTransf('PDelta', Transformation.PDelta)
