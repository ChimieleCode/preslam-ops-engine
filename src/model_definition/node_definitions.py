import openseespy.opensees as ops
from itertools import product
from  ..classes import Frame
from model.enums import BeamSide, ColumnSide


def define_nodes(frame: Frame) -> None:
    """
    Define all the nodes of the model from frame object

    Args:
        frame (Frame): frame object
    """
    # Grid Nodes
    for storey, vertical in product(range(frame.n_storeys + 1), 
                                    range(frame.n_spans + 1)):
        ops.node(
            frame.node_grid(vertical, storey),
            vertical * frame.span_length,
            storey * frame.storey_height
        )
    
    # Base Nodes and Top Column Nodes
    for vertical in range(frame.n_spans + 1):
        ops.node(
            frame.node_base(vertical),
            vertical * frame.span_length,
            0
        )
        ops.node(
            frame.node_top_column(vertical),
            vertical * frame.span_length,
            frame.height - .5*frame.beam_sections[-1].h
        )

    # Panel Nodes
    for storey, vertical in product(range(1, frame.n_storeys + 1), 
                                    range(frame.n_spans + 1)):
        ops.node(
            frame.node_panel(vertical, storey),
            vertical * frame.span_length,
            storey * frame.storey_height
        )

    # Rigid Beam Nodes and Beam Nodes
    for storey, vertical in product(range(1, frame.n_storeys + 1), 
                                    range(1, frame.n_spans + 1)):
        ops.node(
            frame.node_rigid_beam(vertical, storey, BeamSide.Left),
            (vertical - 1) * frame.span_length + frame.int_column_section.h/2,
            storey * frame.storey_height
        )
        ops.node(
            frame.node_beam(vertical, storey, BeamSide.Left),
            (vertical - 1) * frame.span_length + frame.int_column_section.h/2,
            storey * frame.storey_height
        )
        ops.node(
            frame.node_rigid_beam(vertical, storey, BeamSide.Right),
            vertical * frame.span_length - frame.int_column_section.h/2,
            storey * frame.storey_height
        )
        ops.node(
            frame.node_beam(vertical, storey, BeamSide.Right),
            vertical * frame.span_length - frame.int_column_section.h/2,
            storey * frame.storey_height
        )
    
    # Column Nodes
    for storey, vertical in product(range(1, frame.n_storeys), 
                                    range(frame.n_spans + 1)):
        ops.node(
            frame.node_column(vertical, storey, ColumnSide.Below),
            vertical * frame.span_length,
            storey * frame.storey_height - frame.beam_sections[storey - 1].h/2
        )
        ops.node(
            frame.node_column(vertical, storey, ColumnSide.Above),
            vertical * frame.span_length,
            storey * frame.storey_height + frame.beam_sections[storey - 1].h/2
        )
    