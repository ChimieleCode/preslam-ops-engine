from ..classes import Frame, MultilinearElasticLink, GMSteelLink, KineticLink
from ..utils import import_configuration
from ..moment_rotation import (
    axial_moment, steel_moment, tendon_moment, get_neutral_axis, steel_yielding, steel_failure, tendon_failure)

# Import config data
import model.config as config

cfg: config.MNINTConfig
cfg = import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)

options = cfg.moment_rotation_options


def compute_moment_rotation(frame: Frame) -> Frame:
    """
    Computes moment rotation populating link data and limit states data for each 
    section of the frame

    Args:
        frame (Frame): frame object

    Returns:
        Frame: populated frame object
    """
    sections = frame.beam_sections + [
        frame.int_column_section,
        frame.ext_column_section
    ]
    for section in sections:
        theta_axis_points = list()
        # Steel yielding
        theta_axis_points.append(
            steel_yielding(
                initial_guess=[0.005, 0.3],
                section=section,
                frame=frame
            )
        )

        # Steel failure
        theta_axis_points.append(
            steel_failure(
                initial_guess=[0.02, 0.2],
                section=section,
                frame=frame
            )
        )
        # Tendon yielding
        if section.tendon is not None:
            theta_axis_points.append(
                tendon_failure(
                    initial_guess=[0.05, 0.1],
                    section=section,
                    frame=frame
                )
            )
        
        # Additional points
        delta_theta = (
            (theta_axis_points[1][0] - theta_axis_points[0][0]) 
            / (options.pt_points + 1)
        ) # (Theta_s - Thesta_y) / ...

        for i in range(options.pt_points):
            theta = delta_theta * (i + 1) + theta_axis_points[0][0]  # dTheta * (i+1) + Theta_y
            neutral_axis = get_neutral_axis(
                initial_guess=[theta_axis_points[1][1]],
                theta=theta,
                section=section,
                frame=frame
            )
            theta_axis_points.append(
                [theta, neutral_axis[0]]
            )
        
        # MULTILINEAR ELASTIC LINK
        # Initialize
        mul_el_link = MultilinearElasticLink(
            strain=[0.],
            stress=[0.]
        )
        # Decompression
        decompression_strain = 0.0004
        decompression_stress = (section.tendons_pt + section.axial_load) * section.h/6
        mul_el_link.strain.append(decompression_strain)
        mul_el_link.strain.append(-decompression_strain)
        mul_el_link.stress.append(decompression_stress)
        mul_el_link.stress.append(-decompression_stress)
        # Mom-Theta points
        for point in theta_axis_points:
            mul_el_link.strain.append(point[0])
            mul_el_link.strain.append(-point[0])
            stress = sum(
                [
                    tendon_moment(
                        theta=point[0],
                        neutral_axis=point[1],
                        section=section,
                        frame=frame
                    ),
                    axial_moment(
                        theta=point[0],
                        neutral_axis=point[1],
                        section=section,
                        frame=frame
                    )
                ]
            )
            mul_el_link.stress.append(stress)
            mul_el_link.stress.append(-stress)
        
        mul_el_link.strain.sort()
        mul_el_link.stress.sort()

        section.multilinear_elastic_link = mul_el_link

        # MULTILINEAR PLASTIC LINK
        # Fy & E0
        yielding_moment = steel_moment(
            theta=theta_axis_points[0][0],
            neutral_axis=theta_axis_points[0][1],
            section=section,
            frame=frame
        )
        elastic_stiffness = yielding_moment / theta_axis_points[0][0]
        post_yielding_moment = steel_moment(
            theta=theta_axis_points[1][0],
            neutral_axis=theta_axis_points[1][1],
            section=section,
            frame=frame
        )
        plastic_stiffness = ((post_yielding_moment - yielding_moment) 
                             / (theta_axis_points[1][0] - theta_axis_points[0][0]))
        # link type
        if options.use_GM:
            b = plastic_stiffness/elastic_stiffness
            section.GM_link = GMSteelLink(
                Fy=yielding_moment,
                E0=elastic_stiffness,
                b=b,
                strain_limit=theta_axis_points[1][0]
            )
        else:
            H_kin = (elastic_stiffness * plastic_stiffness 
                     / (elastic_stiffness - plastic_stiffness))
            section.kinetic_link = KineticLink(
                Fy=yielding_moment,
                E0=elastic_stiffness,
                H_kin=H_kin,
                strain_limit=theta_axis_points[1][0]
            )

    return frame
