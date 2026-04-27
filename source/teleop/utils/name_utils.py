# Copyright (c) 2023-2026, AgiBot Inc. All Rights Reserved.
# Author: Genie Sim Team
# License: Mozilla Public License Version 2.0

G1_JOINT_NAMES = [
    "idx21_arm_l_joint1",
    "idx22_arm_l_joint2",
    "idx23_arm_l_joint3",
    "idx24_arm_l_joint4",
    "idx25_arm_l_joint5",
    "idx26_arm_l_joint6",
    "idx27_arm_l_joint7",
    "idx61_arm_r_joint1",
    "idx62_arm_r_joint2",
    "idx63_arm_r_joint3",
    "idx64_arm_r_joint4",
    "idx65_arm_r_joint5",
    "idx66_arm_r_joint6",
    "idx67_arm_r_joint7",
    "idx11_head_joint1",
    "idx12_head_joint2",
    "idx02_body_joint2",
    "idx01_body_joint1",
]


G2_JOINT_NAMES = [
    "idx21_arm_l_joint1",
    "idx22_arm_l_joint2",
    "idx23_arm_l_joint3",
    "idx24_arm_l_joint4",
    "idx25_arm_l_joint5",
    "idx26_arm_l_joint6",
    "idx27_arm_l_joint7",
    "idx61_arm_r_joint1",
    "idx62_arm_r_joint2",
    "idx63_arm_r_joint3",
    "idx64_arm_r_joint4",
    "idx65_arm_r_joint5",
    "idx66_arm_r_joint6",
    "idx67_arm_r_joint7",
]

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

OMNIPICKER_AJ_NAMES = ["idx41_gripper_l_outer_joint1", "idx81_gripper_r_outer_joint1"]
