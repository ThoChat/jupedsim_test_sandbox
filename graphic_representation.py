### Representation of the HPP and graphic representation  ###
import numpy as np
import matplotlib.pyplot as plt

## general Humanoid parameters ###
height = 1.75  # height of the agent

orrientation = np.array([0, 0])  # orientation of the agent (x, y) in the world frame

NECK_SCALING_FACTOR = 0.1396
SHOULDER_WIDTH_SCALING_FACTOR = 0.45 / 1.7
TRUNK_WIDTH_SCALING_FACTOR = 0.1470  # called l_r previously
TRUNK_HEIGHT_SCALING_FACTOR = 0.3495
PELVIS_WIDTH_SCALING_FACTOR = 0.2 / 1.7
LEG_SCALING_FACTOR = 0.4791  # 0.2522 (shank) + 0.2269 (thigh)
ANKLE_SCALING_FACTOR = 0.0451
FOOT_FORWARD_SCALING_FACTOR = 0.1470 / 2
FOOT_BACKWARD_SCALING_FACTOR = 0.1470 / 4
FOOT_WIDTH_SCALING_FACTOR = 0.1470 * 8 / 50

# Calculating segment lengths
foot_length_forward = height * FOOT_FORWARD_SCALING_FACTOR
foot_length_backward = height * FOOT_BACKWARD_SCALING_FACTOR
ankle_length = height * ANKLE_SCALING_FACTOR
leg_length = height * LEG_SCALING_FACTOR
pelvis_width = height * PELVIS_WIDTH_SCALING_FACTOR
neck_length = height * NECK_SCALING_FACTOR
shoulder_width = height * SHOULDER_WIDTH_SCALING_FACTOR
trunk_length = height * TRUNK_HEIGHT_SCALING_FACTOR
trunk_width = height * TRUNK_WIDTH_SCALING_FACTOR

#####################################

########### functions ###############


def Create_Transform_Matrix(translation, rotation):
    """
    Create a transformation matrix from translation and rotation.

    Parameters:
    translation (array-like): Translation vector (x, y, z).
    rotation (array-like): Rotation vector (roll, pitch, yaw) in radians.

    Returns:
    np.ndarray: A 4x4 transformation matrix.
    """
    tx, ty, tz = translation
    roll, pitch, yaw = rotation

    # Create the rotation matrix using Euler angles
    R_x = np.array(
        [[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]]
    )

    R_y = np.array(
        [
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)],
        ]
    )

    R_z = np.array(
        [[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]]
    )

    # Combined rotation matrix
    R = R_z @ R_y @ R_x

    # Create the transformation matrix
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = translation

    return T


#####################################

## Joint angles
joint_angles_matrix = np.zeros((11, 3))
# // Rows: joints * 11, Columns: x/y/z rotation in the relative Frames linke to each segment/link,
# // the referencial of the coordinate in linked to the pelvis so that
# // x == sagittal, y == frontal, z == vertical (up) axis
# // list of all simulated joints
# /**
# 0 - right heel
# 1 - right ankle
# 2 - right hip
# 3 - left hip
# 4 - left ankle
# 5 - left heel
# 6 - pelvis/CoM
# 7 - right shoulder
# 8 - C7 / neck
# 9 - left shoulder
# 10 - head
#  **/

########## trying rotations ##############
## swing right leg

joint_angles_matrix = np.array(
    [
        [0, 0, 0],  # 0 - right heel
        [0.00350799, -0.430637, 0],  # 1 - right ankle
        [-0.00350799, 0.430637, 0],  # 2 - right hip
        [-0.00350799, -0.430637, 0],  # 3 - left hip
        [0.00350799, 0.430637, 0],  # 4 - left ankle
        [0, 0, 0],  # 5 - left heel
        [0, 0, 0],  # 6 - pelvis/CoM
        [0, 0, 0],  # 7 - right shoulder
        [0, 0, 0],  # 8 - C7 / neck
        [0, 0, 0],  # 9 - left shoulder
        [0, 0, 0],  # 10 - head
    ]
)

# change joint_angle matrix to match this

joint_angles_matrix = np.array(
    [
        [0, 0, 0],  # 0 - right heel
        [-0.0158286, -0.395093, 0],  # 1 - right ankle
        [0.0158286, 0.395093, 0],  # 2 - right hip
        [0.0158286, -0.395093, 0],  # 3 - left hip
        [-0.0158286, 0.395093, 0],  # 4 - left ankle
        [0, 0, 0],  # 5 - left heel
        [0, 0, 0],  # 6 - pelvis/CoM
        [0, 0, 0],  # 7 - right shoulder
        [0, 0, 0],  # 8 - C7 / neck
        [0, 0, 0],  # 9 - left shoulder
        [0, 0, 0],  # 10 - head
    ]
)


## Joint Positions
joint_positions_matrix = np.zeros((11, 3))
# genaral position of the joints in the pelvis referential

## computing position
# the pelvis == fixed frame

# right hip ==> translation of -pelvis_width/2 along the y-axis (relative to frame 0)
Transform_pelvis_rh = Create_Transform_Matrix(
    translation=[0, -pelvis_width / 2, 0],
    rotation=joint_angles_matrix[2],
)

joint_positions_matrix[2] = (Transform_pelvis_rh @ np.array([0, 0, 0, 1]))[:3]

# right ankle ==> translation of -leg_legth along the z-axis (relative to frame 1 link to right rh and r-leg)
Transform_rh_ra = Create_Transform_Matrix(
    translation=[0, 0, -leg_length],
    rotation=joint_angles_matrix[1],
)

joint_positions_matrix[1] = (
    Transform_pelvis_rh @ Transform_rh_ra @ np.array([0, 0, 0, 1])
)[:3]

# right heel==> translation of -ankle_length along the z-axis and -foot_length_backward along x-axis
#               (relative to frame 2 link to right ankle and r-leg)
Transform_rh_ra_rh = Create_Transform_Matrix(
    translation=[-foot_length_backward, 0, -ankle_length],
    rotation=joint_angles_matrix[0],
)

joint_positions_matrix[0] = (
    Transform_pelvis_rh @ Transform_rh_ra @ Transform_rh_ra_rh @ np.array([0, 0, 0, 1])
)[:3]


# left hip ==> translation of pelvis_width/2 along the y-axis (relative to frame 0)

Transform_pelvis_lh = Create_Transform_Matrix(
    translation=[0, pelvis_width / 2, 0],
    rotation=joint_angles_matrix[3],
)

# left ankle ==> translation of -leg_legth along the z-axis (relative to frame 3 link to left lh and l-leg)
Transform_lh_la = Create_Transform_Matrix(
    translation=[0, 0, -leg_length],
    rotation=joint_angles_matrix[4],
)

joint_positions_matrix[4] = (
    Transform_pelvis_lh @ Transform_lh_la @ np.array([0, 0, 0, 1])
)[:3]

# left heel ==> translation of -ankle_length along the z-axis and -foot_length_backward along x-axis
#               (relative to frame 4 link to left ankle and l-leg)
Transform_lh_la_lh = Create_Transform_Matrix(
    translation=[-foot_length_backward, 0, -ankle_length],
    rotation=joint_angles_matrix[5],
)

joint_positions_matrix[5] = (
    Transform_pelvis_lh @ Transform_lh_la @ Transform_lh_la_lh @ np.array([0, 0, 0, 1])
)[:3]

joint_positions_matrix[3] = (Transform_pelvis_lh @ np.array([0, 0, 0, 1]))[:3]


####### Plot all joints and link in 3D  ######
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")


# Initialize the plot view angle
ax.view_init(elev=45, azim=45)

# Create a list of colors using the viridis colormap
colors = plt.cm.viridis(np.linspace(0, 1, len(joint_angles_matrix)))

for i in range(len(joint_angles_matrix)):
    # Get the color for the current joint index
    color = colors[i]

    # plot joint position
    joint_position = joint_positions_matrix[6]
    ax.scatter(
        joint_position[0], joint_position[1], joint_position[2], color=color, s=50
    )

    # plot segments

# right foot height segment
ax.plot(
    [joint_positions_matrix[0, 0], joint_positions_matrix[1, 0]],
    [joint_positions_matrix[0, 1], joint_positions_matrix[1, 1]],
    [joint_positions_matrix[0, 2], joint_positions_matrix[1, 2]],
    color="g",
    linewidth=2,
)

# right leg segment
ax.plot(
    [joint_positions_matrix[1, 0], joint_positions_matrix[2, 0]],
    [joint_positions_matrix[1, 1], joint_positions_matrix[2, 1]],
    [joint_positions_matrix[1, 2], joint_positions_matrix[2, 2]],
    color="r",
    linewidth=2,
)

# Pelvis segment
ax.plot(
    [joint_positions_matrix[2, 0], joint_positions_matrix[3, 0]],
    [joint_positions_matrix[2, 1], joint_positions_matrix[3, 1]],
    [joint_positions_matrix[2, 2], joint_positions_matrix[3, 2]],
    color="b",
    linewidth=2,
)

# left leg segment
ax.plot(
    [joint_positions_matrix[3, 0], joint_positions_matrix[4, 0]],
    [joint_positions_matrix[3, 1], joint_positions_matrix[4, 1]],
    [joint_positions_matrix[3, 2], joint_positions_matrix[4, 2]],
    color="r",
    linewidth=2,
)

# left foot height segment
ax.plot(
    [joint_positions_matrix[4, 0], joint_positions_matrix[5, 0]],
    [joint_positions_matrix[4, 1], joint_positions_matrix[5, 1]],
    [joint_positions_matrix[4, 2], joint_positions_matrix[5, 2]],
    color="g",
    linewidth=2,
)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_aspect("equal", adjustable="box")
plt.show()
