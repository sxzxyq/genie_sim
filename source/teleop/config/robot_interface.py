# Copyright (c) 2023-2026, AgiBot Inc. All Rights Reserved.
# Author: Genie Sim Team
# License: Mozilla Public License Version 2.0

from enum import Enum


class RobotType(Enum):
    G2 = "G2"
    G2_WALKER_S2 = "G2_WalkerS2"


# cfg
# G2
g2_arm_joints0 = [0.0, -0.66, 0.0, -1.6, 0.0, -0.8, 0.0]
g2_waist_joints0 = [0.0, 0.0, 0.0, 0.0, 0.0]
G2 = {
    #  limits is tmp
    "lb": [],
    "ub": [],
    "tol": [],
    "ee_frames": ["arm_l_end_link", "arm_r_end_link"],
    "ref_frames": ["arm_l_link3", "arm_r_link3"],
    "waist_frame": "body_link5",
    "home_joints": [g2_waist_joints0, g2_arm_joints0, g2_arm_joints0],
}

walker_s2_arm_joints0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
walker_s2_waist_joints0 = [0.0, 0.0]
walker_s2_head_joints0 = [0.0, 0.0]
WALKER_S2_BODY_JOINT_NAMES = ["waist_yaw_joint", "waist_pitch_joint"]
WALKER_S2_HEAD_JOINT_NAMES = ["head_yaw_joint", "head_pitch_joint"]
WALKER_S2_LEFT_ARM_JOINT_NAMES = [
    "L_shoulder_pitch_joint",
    "L_shoulder_roll_joint",
    "L_shoulder_yaw_joint",
    "L_elbow_roll_joint",
    "L_elbow_yaw_joint",
    "L_wrist_pitch_joint",
    "L_wrist_roll_joint",
]
WALKER_S2_RIGHT_ARM_JOINT_NAMES = [
    "R_shoulder_pitch_joint",
    "R_shoulder_roll_joint",
    "R_shoulder_yaw_joint",
    "R_elbow_roll_joint",
    "R_elbow_yaw_joint",
    "R_wrist_pitch_joint",
    "R_wrist_roll_joint",
]
WALKER_S2_JOINT_NAMES = (
    WALKER_S2_BODY_JOINT_NAMES
    + WALKER_S2_HEAD_JOINT_NAMES
    + WALKER_S2_LEFT_ARM_JOINT_NAMES
    + WALKER_S2_RIGHT_ARM_JOINT_NAMES
)
G2_WALKER_S2 = {
    "lb": [],
    "ub": [],
    "tol": [],
    "base_frame": "base_link",
    "arm_base_frame": "waist_pitch_link",
    "ee_frames": ["L_hand_link", "R_hand_link"],
    "ref_frames": ["L_elbow_yaw_link", "R_elbow_yaw_link"],
    "waist_frame": "waist_pitch_link",
    "home_joints": [walker_s2_waist_joints0, walker_s2_arm_joints0, walker_s2_arm_joints0],
    "joint_names": WALKER_S2_JOINT_NAMES,
    "body_joint_names": WALKER_S2_BODY_JOINT_NAMES,
    "head_joint_names": WALKER_S2_HEAD_JOINT_NAMES,
    "left_arm_joint_names": WALKER_S2_LEFT_ARM_JOINT_NAMES,
    "right_arm_joint_names": WALKER_S2_RIGHT_ARM_JOINT_NAMES,
    "tool_joint_names": [],
    "enable_tool_control": False,
}

robot_desc_map = {
    RobotType.G2: G2,
    RobotType.G2_WALKER_S2: G2_WALKER_S2,
}


def robot_type_from_name(robot_name):
    if "WalkerS2" in robot_name:
        return RobotType.G2_WALKER_S2
    return RobotType.G2
BODY_JOINT_NAMES = [
    "idx01_body_joint1",
    "idx02_body_joint2",
    "idx03_body_joint3",
    "idx04_body_joint4",
    "idx05_body_joint5",
]
HEAD_JOINT_NAMES = ["idx11_head_joint1", "idx12_head_joint2", "idx13_head_joint3"]
LEFT_ARM_JOINT_NAMES = [
    "idx21_arm_l_joint1",
    "idx22_arm_l_joint2",
    "idx23_arm_l_joint3",
    "idx24_arm_l_joint4",
    "idx25_arm_l_joint5",
    "idx26_arm_l_joint6",
    "idx27_arm_l_joint7",
]
RIGHT_ARM_JOINT_NAMES = [
    "idx61_arm_r_joint1",
    "idx62_arm_r_joint2",
    "idx63_arm_r_joint3",
    "idx64_arm_r_joint4",
    "idx65_arm_r_joint5",
    "idx66_arm_r_joint6",
    "idx67_arm_r_joint7",
]
