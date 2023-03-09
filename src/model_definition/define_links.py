from itertools import product
import openseespy.opensees as ops

from model.enums.frame_enums import BeamSide
from ..classes import Frame, Section
from ..utils import import_configuration

# Import config data
import model.config as config

cfg: config.MNINTConfig
cfg = import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)


def external_joint_stiffness(frame: Frame, storey: int) -> float:
    """
    External joint stiffness

    Args:
        frame (Frame): frame object
        storey (int): storey of joint (consistent with beams)

    Returns:
        float: stiffness
    """
    return (17/30 * frame.ext_column_section.area 
            * frame.beam_sections[storey].h 
            * frame.ext_column_section.timber.G
            / (1 - frame.ext_column_section.h/frame.span_length))


def internal_joint_stiffness(frame: Frame, storey: int) -> float:
    """
    Internal joint stiffness

    Args:
        frame (Frame): frame object
        storey (int): storey of joint (consistent with beams)

    Returns:
        float: stiffness
    """
    return (17/30 * frame.int_column_section.area 
            * frame.beam_sections[storey].h 
            * frame.int_column_section.timber.G 
            * 2/(2 - cfg.moment_rotation_options.beta)
            / (1 - frame.int_column_section.h/frame.span_length))


def define_rigid_link(frame: Frame) -> None:
    """
    Defines a rigid material for links

    Args:
        frame (Frame): frame object
    """
    ops.uniaxialMaterial(
        'Elastic', 
        frame.rigid_link(), 
        cfg.model_options.rigid_link
    )


def define_sections_uniaxial_material_links(frame: Frame) -> None:
    """
    Defines the uniaxial materials used for the section links

    Args:
        frame (Frame): frame object
    """
    # Internal column N
    ops.uniaxialMaterial(
        'ElasticMultiLinear',
        frame.column_N(1),                             
        '-strain', 
        *frame.int_column_section.multilinear_elastic_link.strain,
        '-stress', 
        *frame.int_column_section.multilinear_elastic_link.stress
    )
    # External column N
    ops.uniaxialMaterial(
        'ElasticMultiLinear',
        frame.column_N(0),                             
        '-strain', 
        *frame.ext_column_section.multilinear_elastic_link.strain,
        '-stress', 
        *frame.ext_column_section.multilinear_elastic_link.stress
    )

    if cfg.moment_rotation_options.use_GM:
        # Internal column S
        ops.uniaxialMaterial(
            'Steel02', 
            frame.column_S(1),                              
            frame.int_column_section.GM_link.Fy,                              
            frame.int_column_section.GM_link.E0,                              
            frame.int_column_section.GM_link.b,                              
            frame.int_column_section.GM_link.r0,                              
            frame.int_column_section.GM_link.cr1,                              
            frame.int_column_section.GM_link.cr2
        )
        internal_strain_limit = frame.int_column_section.GM_link.strain_limit
        # External column S
        ops.uniaxialMaterial(
            'Steel02', 
            frame.column_S(0),                              
            frame.ext_column_section.GM_link.Fy,                              
            frame.ext_column_section.GM_link.E0,                              
            frame.ext_column_section.GM_link.b,                              
            frame.ext_column_section.GM_link.r0,                              
            frame.ext_column_section.GM_link.cr1,                              
            frame.ext_column_section.GM_link.cr2
        )
        external_strain_limit = frame.ext_column_section.GM_link.strain_limit
    else:
        # Internal column S
        ops.uniaxialMaterial(
            'Hardening', 
            frame.column_S(1), 
            frame.int_column_section.kinetic_link.E0, 
            frame.int_column_section.kinetic_link.Fy, 
            frame.int_column_section.kinetic_link.H_iso, 
            frame.int_column_section.kinetic_link.H_kin
        )
        internal_strain_limit = frame.int_column_section.kinetic_link.strain_limit
        # External column S
        ops.uniaxialMaterial(
            'Hardening', 
            frame.column_S(0), 
            frame.ext_column_section.kinetic_link.E0, 
            frame.ext_column_section.kinetic_link.Fy, 
            frame.ext_column_section.kinetic_link.H_iso, 
            frame.ext_column_section.kinetic_link.H_kin
        )
        external_strain_limit = frame.ext_column_section.kinetic_link.strain_limit

    if cfg.moment_rotation_options.steel_failure:
        # Internal column
        ops.uniaxialMaterial(
            'MinMax',
            frame.column_S_MinMax(1),
            frame.column_S(1),
            '-min',
            -internal_strain_limit,
            '-max',
            internal_strain_limit
        )
        # External column
        ops.uniaxialMaterial(
            'MinMax',
            frame.column_S_MinMax(0),
            frame.column_S(0),
            '-min',
            -external_strain_limit,
            '-max',
            external_strain_limit
        )

    # Beam Links
    for storey in range(frame.n_storeys):
        # Beams PT
        ops.uniaxialMaterial(
            'ElasticMultiLinear', 
            frame.beam_PT(storey + 1),
            '-strain', 
            *frame.beam_sections[storey].multilinear_elastic_link.strain,
            '-stress', 
            *frame.beam_sections[storey].multilinear_elastic_link.stress
        )

        if cfg.moment_rotation_options.tendon_failure:
            ops.uniaxialMaterial(
                'MinMax',
                frame.beam_PT_MinMax(storey + 1),
                frame.beam_PT(storey + 1),
                '-min',
                frame.beam_sections[storey].multilinear_elastic_link.strain[0],
                '-max',
                frame.beam_sections[storey].multilinear_elastic_link.strain[-1],
            )
        
        # Beam S
        if cfg.moment_rotation_options.use_GM:
            ops.uniaxialMaterial(
                'Steel02', 
                frame.beam_S(storey + 1),                              
                frame.beam_sections[storey].GM_link.Fy,                              
                frame.beam_sections[storey].GM_link.E0,                              
                frame.beam_sections[storey].GM_link.b,                              
                frame.beam_sections[storey].GM_link.r0,                              
                frame.beam_sections[storey].GM_link.cr1,                              
                frame.beam_sections[storey].GM_link.cr2
            )
            beam_strain_limit = frame.beam_sections[storey].GM_link.strain_limit
        else:
            ops.uniaxialMaterial(
                'Hardening', 
                frame.beam_S(storey + 1), 
                frame.beam_sections[storey].kinetic_link.E0, 
                frame.beam_sections[storey].kinetic_link.Fy, 
                frame.beam_sections[storey].kinetic_link.H_iso, 
                frame.beam_sections[storey].kinetic_link.H_kin
            )
            beam_strain_limit = frame.int_column_section.kinetic_link.strain_limit

        if cfg.moment_rotation_options.steel_failure:
            ops.uniaxialMaterial(
                'MinMax',
                frame.beam_S_MinMax(storey + 1),
                frame.beam_S(storey + 1),
                '-min',
                -beam_strain_limit,
                '-max',
                beam_strain_limit
            )


def define_joint_uniaxial_material_links(frame : Frame) -> None:
    """
    Defines the uniaxial materials used for the node links

    Args:
        frame (Frame): frame object
    """
    for storey in range(frame.n_storeys):
        # External
        ops.uniaxialMaterial(
            'Elastic',
            frame.joint_external_link(storey + 1),                             
            external_joint_stiffness(frame, storey)
        )
        # Internal
        ops.uniaxialMaterial(
            'Elastic',
            frame.joint_internal_link(storey + 1),                             
            internal_joint_stiffness(frame, storey)
        )


#### DEFINITION OF LINK ELEMENTS ####
def define_zerolength_link(element_id: int, node_i: int, node_j: int, uniax_mat_id: int, rigid_mat_id: int) -> None:
    """
    Defines a zerolength element

    Args:
        element_id (int): element id
        node_i (int): node i
        node_j (int): node j
        uniax_mat_id (int): uniaxial material id for dir 6
        rigid_mat_id (int): rigid material id for dir 1 & 2
    """
    ops.element(
        'zeroLength',
        element_id,
        node_i,
        node_j,
        '-mat',
        uniax_mat_id,
        rigid_mat_id,
        rigid_mat_id,
        '-dir',
        *[6, 1, 2]
    )


def define_sections_link_elements(frame: Frame) -> None:
    """
    Defines section zerolength elements

    Args:
        frame (Frame): frame object
    """
    element_id = frame.element_avalable_id

    # Columns
    for vertical in range(frame.n_spans + 1):
        if cfg.moment_rotation_options.steel_failure:
            tag_steel = frame.column_S_MinMax(vertical)
        else:
            tag_steel = frame.column_S(vertical)
        
        # Column N
        define_zerolength_link(
            element_id=element_id,
            node_i=frame.node_grid(vertical, 0),
            node_j=frame.node_base(vertical),
            uniax_mat_id=frame.column_N(vertical),
            rigid_mat_id=frame.rigid_link() 
        )
        element_id += 1
        # Column S
        define_zerolength_link(
            element_id=element_id,
            node_i=frame.node_grid(vertical, 0),
            node_j=frame.node_base(vertical),
            uniax_mat_id=tag_steel,
            rigid_mat_id=frame.rigid_link() 
        )
        element_id += 1
    
    # Beams
    for storey in range(1, frame.n_storeys + 1):
        if cfg.moment_rotation_options.tendon_failure:
            tag_tendon = frame.beam_PT_MinMax(storey)
        else:
            tag_tendon = frame.beam_PT(storey)

        if cfg.moment_rotation_options.steel_failure:
            tag_steel = frame.beam_S_MinMax(storey)
        else:
            tag_steel = frame.beam_S(storey)

        for vertical in range(1, frame.n_spans + 1):
            # Beam PT
            define_zerolength_link(
                element_id=element_id,
                node_i=frame.node_rigid_beam(vertical, storey, BeamSide.Left),
                node_j=frame.node_beam(vertical, storey, BeamSide.Left),
                uniax_mat_id=tag_tendon,
                rigid_mat_id=frame.rigid_link() 
            )
            element_id += 1

            define_zerolength_link(
                element_id=element_id,
                node_i=frame.node_beam(vertical, storey, BeamSide.Right),
                node_j=frame.node_rigid_beam(vertical, storey, BeamSide.Right),
                uniax_mat_id=tag_tendon,
                rigid_mat_id=frame.rigid_link() 
            )
            element_id += 1

            # Beam S
            define_zerolength_link(
                element_id=element_id,
                node_i=frame.node_rigid_beam(vertical, storey, BeamSide.Left),
                node_j=frame.node_beam(vertical, storey, BeamSide.Left),
                uniax_mat_id=tag_steel,
                rigid_mat_id=frame.rigid_link() 
            )
            element_id += 1

            define_zerolength_link(
                element_id=element_id,
                node_i=frame.node_beam(vertical, storey, BeamSide.Right),
                node_j=frame.node_rigid_beam(vertical, storey, BeamSide.Right),
                uniax_mat_id=tag_steel,
                rigid_mat_id=frame.rigid_link() 
            )
            element_id += 1
    
    frame.element_avalable_id = element_id

 
def define_rigid_node_links(frame: Frame) -> None:
    """
    Defines rigid node links

    Args:
        frame (Frame): frame object
    """
    element_id = frame.element_avalable_id
    # Node links
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(frame.n_spans + 1)):
        define_zerolength_link(
            element_id=element_id,
            node_i=frame.node_grid(vertical, storey),
            node_j=frame.node_panel(vertical, storey),
            uniax_mat_id=frame.rigid_link(),
            rigid_mat_id=frame.rigid_link() 
        )
        element_id += 1

    frame.element_avalable_id = element_id


def define_node_links(frame: Frame) -> None:
    """
    Defines elastic node links

    Args:
        frame (Frame): frame object
    """
    element_id = frame.element_avalable_id
    # Node links
    for storey, vertical in product(range(1, frame.n_storeys + 1),
                                    range(frame.n_spans + 1)):
        if vertical in (0, frame.n_spans):
            panel_link = frame.joint_external_link(storey)
        else:
            panel_link = frame.joint_internal_link(storey)
            
        define_zerolength_link(
            element_id=element_id,
            node_i=frame.node_grid(vertical, storey),
            node_j=frame.node_panel(vertical, storey),
            uniax_mat_id=panel_link,
            rigid_mat_id=frame.rigid_link() 
        )
        element_id += 1
    
    frame.element_avalable_id = element_id


def define_model_links(frame: Frame) -> None:
    """
    Handles all the link definitions

    Args:
        frame (Frame): frame object
    """
    # Define uniaxial materials
    define_rigid_link(frame)
    define_sections_uniaxial_material_links(frame)
    # Define link objects
    define_sections_link_elements(frame)
    # Defines node links
    if cfg.model_options.rigid_joints:
        define_rigid_node_links(frame)
    else:
        define_joint_uniaxial_material_links(frame)
        define_node_links(frame)
