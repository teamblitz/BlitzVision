from scipy.spatial.transform import Rotation as R
import numpy as np
from core.utils import units


def compute_tag_transform(tag_xyz, tag_rot_matrix):
    output = np.zeros((4, 4))
    output[0:3, 0:3] = tag_rot_matrix
    output[0:3, 3] = tag_xyz
    output[3, 3] = 1
    return output


def compute_tag_corners(transform, size):
    corners = (  # Homogeneous corner coordinates
        [0, size / 2, -size / 2, 1],  # Lower left
        [0, -size / 2, -size / 2, 1],  # Lower right
        [0, -size / 2, size / 2, 1],  # Upper right
        [0, size / 2, size / 2, 1]  # Upper left
    )
    output_corners = []
    for corner in corners:
        output_corners.append((transform @ corner)[0:3])
    return output_corners


april_tag_transforms = {
            "tag16h5": {
                # Red side of the field
                1: compute_tag_transform([units.inches_to_meters(610.77),
                                          units.inches_to_meters(42.19),
                                          units.inches_to_meters(18.22)],
                                         np.identity(3)),
                2: compute_tag_transform([units.inches_to_meters(610.77),
                                          units.inches_to_meters(108.19),
                                          units.inches_to_meters(18.22)],
                                         np.identity(3)),
                3: compute_tag_transform([units.inches_to_meters(610.77),
                                          units.inches_to_meters(174.19),  # FIRST's diagram has a typo (it says 147.19)
                                          units.inches_to_meters(18.22)],
                                         np.identity(3)),
                4: compute_tag_transform([units.inches_to_meters(636.96),
                                          units.inches_to_meters(265.74),
                                          units.inches_to_meters(27.38)],
                                         np.identity(3)),
                # Blue side of the field
                5: compute_tag_transform([units.inches_to_meters(14.25),
                                          units.inches_to_meters(265.74),
                                          units.inches_to_meters(27.38)],
                                         R.from_euler("Z", np.pi).as_matrix()),
                6: compute_tag_transform([units.inches_to_meters(40.45),
                                          units.inches_to_meters(174.19),  # FIRST's diagram has a typo (it says 147.19)
                                          units.inches_to_meters(18.22)],
                                         R.from_euler("Z", np.pi).as_matrix()),
                7: compute_tag_transform([units.inches_to_meters(40.45),
                                          units.inches_to_meters(108.19),
                                          units.inches_to_meters(18.22)],
                                         R.from_euler("Z", np.pi).as_matrix()),
                8: compute_tag_transform([units.inches_to_meters(40.45),
                                          units.inches_to_meters(42.19),
                                          units.inches_to_meters(18.22)],
                                         R.from_euler("Z", np.pi).as_matrix())
            }
        }

size = units.inches_to_meters(6)
april_tag_corners = {
    "tag16h5": {
        1: compute_tag_corners(april_tag_transforms["tag16h5"][1], size),
        2: compute_tag_corners(april_tag_transforms["tag16h5"][2], size),
        3: compute_tag_corners(april_tag_transforms["tag16h5"][3], size),
        4: compute_tag_corners(april_tag_transforms["tag16h5"][4], size),
        5: compute_tag_corners(april_tag_transforms["tag16h5"][5], size),
        6: compute_tag_corners(april_tag_transforms["tag16h5"][6], size),
        7: compute_tag_corners(april_tag_transforms["tag16h5"][7], size),
        8: compute_tag_corners(april_tag_transforms["tag16h5"][8], size)
    }
}

print(april_tag_transforms)

print("\n\n\n\n")
print(april_tag_corners)
