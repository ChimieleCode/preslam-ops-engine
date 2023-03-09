import src.model_definition as bld
from ..classes import Frame


def build_opensees_model(frame: Frame) -> None:
    """
    Builds an opensees model of the frame

    Args:
        frame (Frame): Frame object
    """
    # Initialize the model
    bld.model_initialize()
    # Define nodes
    bld.define_nodes(frame)
    # Define constrainst and restraints
    bld.define_base_restraints(frame)
    bld.define_diaphragm(frame)
    # Declare the geometric transformations
    bld.model_transformation()
    # Defines the frame elements
    bld.define_frame_elements(frame)
    # Defines the uniaxial materials
    bld.define_model_links(frame)
    # Time series
    bld.model_time_series()
    # Masses
    bld.define_node_masses(frame)
    # Loads
    bld.define_nodal_vertical_loads(frame)
