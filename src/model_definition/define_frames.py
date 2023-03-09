from itertools import product
import openseespy.opensees as ops
from model.enums.frame_enums import BeamSide, ColumnSide
from ..utils import import_configuration
from ..classes import Frame, Section

# Import config data
import model.config as config

cfg : config.MNINTConfig
cfg = import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)


def define_elastic_beam_column(id: int, node_i: int, node_j: int, section: Section) -> None:
    """
    Defines an opensees elastic beamcolumn element

    Args:
        id (int): element id
        node_i (int): i node
        node_j (int): j node
        section (Section): section of beamcolumn
    """
    ops.element(
        'elasticBeamColumn', 
        id, 
        node_i, 
        node_j,
        section.area,
        section.timber.E,
        section.inertia,
        cfg.model_options.transformation
    )


def define_rigid_beam_column(id: int, node_i: int, node_j: int, section: Section) -> None:
    """
    Defines an opensees rigid link of elastic beamcolumn element

    Args:
        id (int): element id
        node_i (int): i node
        node_j (int): j node
        section (Section): section of beamcolumn
    """
    ops.element(
        'elasticBeamColumn', 
        id, 
        node_i, 
        node_j,
        section.area,
        section.timber.E * cfg.model_options.rigid_factor,
        section.inertia,
        cfg.model_options.transformation
    )


def define_frame_elements(frame: Frame) -> None:
    """
    Define frame elements of the model

    Args:
        frame (Frame): frame object
    """
    element_id = frame.element_avalable_id

    # Base columns
    for vertical in range(frame.n_spans + 1):
        
        # picks the column section
        if vertical in (0, frame.n_spans):
            column_section = frame.ext_column_section
        else:
            column_section = frame.int_column_section

        # checks if the frame has only 1 storey
        if frame.n_storeys == 1:
            define_elastic_beam_column(
                id=element_id,
                node_i=frame.node_base(vertical), 
                node_j=frame.node_top_column(vertical),
                section=column_section
            )
            element_id += 1
        else:
            define_elastic_beam_column(
                id=element_id,
                node_i=frame.node_base(vertical), 
                node_j=frame.node_column(vertical, 1, ColumnSide.Below),
                section=column_section
            )
            element_id += 1

    # Other columns [only if there are at least 2 storeys]
    if frame.n_storeys > 1:
        for storey, vertical in product(range(1, frame.n_storeys),
                                        range(frame.n_spans + 1)):
            
            # picks the column section            
            if vertical in (0, frame.n_spans):
                column_section = frame.ext_column_section
            else:
                column_section = frame.int_column_section
                    
            # last floor has a a different type of nodes
            if storey == frame.n_storeys - 1:
                define_elastic_beam_column(
                    id=element_id,
                    node_i=frame.node_column(vertical, storey, ColumnSide.Above), 
                    node_j=frame.node_top_column(vertical),
                    section=column_section
                )
                element_id += 1
            else:
                define_elastic_beam_column(
                    id=element_id,
                    node_i=frame.node_column(vertical, storey, ColumnSide.Above), 
                    node_j=frame.node_column(vertical, storey + 1, ColumnSide.Below),
                    section=column_section
                )
                element_id += 1
    
    # Beam elements
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(1, frame.n_spans + 1)):
        define_elastic_beam_column(
            id=element_id,
            node_i=frame.node_beam(vertical, storey, BeamSide.Left), 
            node_j=frame.node_beam(vertical, storey, BeamSide.Right),
            section=frame.beam_sections[storey - 1]
        )
        element_id += 1
    
    # Rigid links below column
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(frame.n_spans + 1)):
        # picks the column section     
        if vertical in (0, frame.n_spans):
            column_section = frame.ext_column_section
        else:
            column_section = frame.int_column_section

        if storey == frame.n_storeys:
            define_rigid_beam_column(
                id=element_id,
                node_i=frame.node_top_column(vertical),
                node_j=frame.node_grid(vertical, storey),
                section=column_section
            )
            element_id += 1
        else:
            define_rigid_beam_column(
                id=element_id,
                node_i=frame.node_column(vertical, storey, ColumnSide.Below),
                node_j=frame.node_grid(vertical, storey),
                section=column_section
            )
            element_id += 1

    # Rigid link above column
    for storey, vertical in product(range(1, frame.n_storeys),
                                    range(frame.n_spans + 1)):
        # picks the column section     
        if vertical in (0, frame.n_spans):
            column_section = frame.ext_column_section
        else:
            column_section = frame.int_column_section
        
        define_rigid_beam_column(
            id=element_id,
            node_i=frame.node_column(vertical, storey, ColumnSide.Above),
            node_j=frame.node_grid(vertical, storey),
            section=frame.beam_sections[storey - 1]
        )
        element_id += 1
    
    # Rigid beam elements
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(1, frame.n_spans + 1)):
        define_rigid_beam_column(
            id=element_id,
            node_i=frame.node_panel(vertical - 1, storey),
            node_j=frame.node_rigid_beam(vertical, storey, BeamSide.Left),
            section=frame.beam_sections[storey - 1]
        )
        element_id += 1
        define_rigid_beam_column(
            id=element_id,
            node_i=frame.node_rigid_beam(vertical, storey, BeamSide.Right),
            node_j=frame.node_panel(vertical, storey),
            section=frame.beam_sections[storey - 1]
        )
        element_id += 1
    
    frame.element_avalable_id = element_id

         





