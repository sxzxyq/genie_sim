# WalkerS2 Pico 接入 Debug 文件地图

这份文档只解释本次 `G2_WalkerS2` Pico 采集接入新增或修改的文件。用途是 debug 时能快速判断：一个问题应该先看哪一层、哪个文件、哪个字段。

首版目标：`G2_WalkerS2` 右臂末端遥操作，手部固定，不做灵巧手主动控制。

## 1. 启动入口

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `scripts/autoteleop.sh` | 修改 | 增加 `walker_s2` 启动模式；根据参数切换仿真配置、teleop robot_cfg、motion-control robot。 | 如果四个终端启动错配置，先看 `ROBOT_MODE`、`SIM_CONFIG`、`TELEOP_ROBOT_CFG`、`MC_ARGS`。 |

使用方式：

```bash
./scripts/autoteleop.sh walker_s2
```

这个命令会让四个进程变成：

```text
app.py --config ./source/geniesim/config/teleop_walker_s2.yaml
bridge.py
start_mc.sh -s --robot=G2_WalkerS2 --no-tool
teleop.py --robot_cfg G2_WalkerS2.json --teleop_config ./source/geniesim/config/teleop_walker_s2.yaml
```

`-s` 的作用是清理 `start_mc.sh` 缓存的旧 robot name，避免之前选过 `G2` 后继续误用 `G2`。

## 2. GenieSim 机器人资源索引

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `source/geniesim/app/robot_cfg/G2_WalkerS2.json` | 新增 | GenieSim 读取机器人的总索引。它告诉 `RobotCfg` 机器人 USD、URDF、Lula yml、base prim、末端 frame、固定手配置在哪里。 | 如果机器人加载失败，先看 `robot.robot_usd`、`robot.base_prim_path`、`robot.robot_description`、`robot.urdf_name`。 |
| `source/geniesim/app/robot_cfg/G2_WalkerS2/G2_WalkerS2.urdf` | 新增 | GenieSim/Lula 使用的 WalkerS2 URDF 副本。 | 如果 IK 报 joint/link 找不到，检查这里的 joint/link 名和 USD articulation DOF 名是否一致。 |
| `source/geniesim/app/robot_cfg/G2_WalkerS2/G2_WalkerS2.yml` | 新增 | Lula 右臂运动学配置；首版只把右臂 7 个关节放进 `cspace`，其他关节固定。 | 如果 IK 不动或末端不对，重点看 `cspace`、`default_q`、`cspace_to_urdf_rules`、`collision_spheres`。 |

当前 `G2_WalkerS2.json` 的关键设计：

```text
robot_name: G2_WalkerS2
base_prim_path: /G2_WalkerS2
robot_usd: robot/WalkerS2/Collected_WalkerS2/SubUSDs/s2_hand4_v1.usd
robot_description: /G2_WalkerS2/G2_WalkerS2.yml
urdf_name: /G2_WalkerS2/G2_WalkerS2.urdf
end_effector_name.right: R_hand_link
gripper_type: fixed
```

首版 `camera` 是空对象，因为当前未确认 WalkerS2 USD 里的稳定相机 prim。需要图像采集时，必须先在 USD 中确认或新增 Camera，再同步更新 `G2_WalkerS2.json` 和任务配置里的 `recording_setting.camera_list`。

## 3. GenieSim 任务配置

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `source/geniesim/config/teleop_walker_s2.yaml` | 新增 | WalkerS2 专用启动配置，把 benchmark task 指到 `table_task_walker_s2`。 | 如果 app 启动后仍加载 G1/G2 原机器人，先看这里的 `benchmark.task_name`。 |
| `source/geniesim/benchmark/config/eval_tasks/table_task_walker_s2.json` | 新增 | WalkerS2 专用任务配置，指定 `robot_cfg: G2_WalkerS2.json`、场景、初始位姿、记录设置。 | 如果 `TaskBenchmark` 没加载 WalkerS2，先看 `robot.robot_cfg`。如果记录没图像，看 `recording_setting.camera_list`。 |
| `source/geniesim/benchmark/config/robot_init_states.py` | 修改 | 给 `pick_block_color` 增加 `G2_WalkerS2` 初始状态，teleop reset 时能找到 body/head/arm 初始值。 | 如果 Pico reset 报找不到 `G2_WalkerS2` 初始状态，检查 `TASK_INFO_DICT["pick_block_color"]["G2_WalkerS2"]`。 |
| `source/geniesim/benchmark/task_benchmark.py` | 修改 | 让 WalkerS2 录制 topic 不再套用 G1/G2 相机 topic，首版只记录 `/tf`、`/joint_states`、`/record/static_info`。 | 如果录制流程找不存在的相机 topic，检查 `set_record_topics()` 中 WalkerS2 分支。 |

这层的调用关系：

```text
teleop_walker_s2.yaml
-> benchmark.task_name = table_task_walker_s2
-> table_task_walker_s2.json
-> robot.robot_cfg = G2_WalkerS2.json
-> api_core.init_robot_cfg(...)
```

## 4. GenieSim 运行时硬编码适配

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `source/geniesim/utils/name_utils.py` | 修改 | 增加 `G2_WalkerS2` 的 benchmark robot type mapping 和关节组。 | 如果 benchmark 报 `Invalid robot type: G2_WalkerS2`，先看 `robot_type_mapping()` 和 `ROBOT_CONFIGS`。 |
| `source/geniesim/utils/data_courier.py` | 修改 | 允许 `G2_WalkerS2` 在无相机映射时用空字典读取 observation，避免直接抛 `Invalid robot cfg`。 | 如果数据流调用 observation 报 invalid robot cfg，检查这里是否走到 `G2_WalkerS2` 分支。 |
| `source/geniesim/app/controllers/api_core.py` | 修改 | viewport 默认相机不再硬编码 `/G1/...` 或 `/genie/...`，改为从 robot config 的 `camera` 字段取第一个相机。 | 如果启动时报 set active camera 路径不存在，检查 `G2_WalkerS2.json` 的 `camera` 字段或这里的 `active_camera`。 |
| `source/geniesim/app/ros_publisher/robot_interface.py` | 修改 | 增加 WalkerS2 关节名到动态 TF 名单；查找 `base_link` 更宽松；只追加真实存在的 legacy `/genie/...` TF。 | 如果 `/tf` 没有 `R_hand_link` 或 `base_link`，先看 `register_robot_tf()` 是否找到 root prim。 |

这层主要解决两个问题：

```text
问题 1：原项目很多地方只认识 G1_omnipicker/G2_omnipicker/G2_90d。
解决：给 name_utils/data_courier 加 G2_WalkerS2 分支。

问题 2：原项目 TF 和 viewport 有 /G1、/genie 硬编码。
解决：对 WalkerS2 改成配置驱动或存在性检查。
```

## 5. Pico Teleop Python 侧

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `source/teleop/config/robot_interface.py` | 修改 | 新增 `RobotType.G2_WALKER_S2`，定义 WalkerS2 的 base frame、arm base frame、左右末端 frame、关节组、是否启用 tool control。 | 如果 `/wbc/retarget` 的 frame 名不对，先看 `G2_WALKER_S2["arm_base_frame"]` 和 `ee_frames`。 |
| `source/teleop/utils/name_utils.py` | 修改 | 新增 WalkerS2 teleop 侧关节名列表。 | 如果 teleop 解析 `/joint_states` 找不到 WalkerS2 关节，检查这些 joint names 是否与 `/joint_states.name` 一致。 |
| `source/teleop/utils/ros_nodes.py` | 修改 | 让 `SimNode` 根据 robot name 选择 WalkerS2 frames；`pub_mc()` 不再硬编码 `arm_base_link`；WalkerS2 不发布 right tool group。 | 如果 Pico 位姿已收到但 motion-control 不动，先看 `/wbc/retarget` 中 `frame_id`、`target_frame_names` 是否是 `waist_pitch_link` 和 `R_hand_link`。 |
| `source/teleop/teleop.py` | 修改 | 支持 `--robot_cfg G2_WalkerS2.json` 和 `--teleop_config`；WalkerS2 固定手时跳过夹爪命令；reset 使用 WalkerS2 初始状态。 | 如果 trigger 还在控制 `idx41/idx81`，看 `parse_eef_control()` 是否因 `fixed_hand` return。 |
| `source/teleop/bridge.py` | 修改 | 让 bridge 能识别 WalkerS2 的 `waist_*`、`L_*`、`R_*` 关节名，并发布给 `/hal/joint_state`。 | 如果 motion-control 收不到 WalkerS2 关节状态，先看 `_publish_hal()` 是否把 WalkerS2 joint name 加进 `GeniesimJointState`。 |

Pico 侧最关键的数据流：

```text
Pico UDP
-> pico_device.py
-> teleop.py
-> ros_nodes.py pub_mc()
-> /wbc/retarget
-> genie_motion_control
-> /hal/joint_cmd
-> bridge.py
-> /joint_command
-> Isaac ArticulationController
```

注意：`source/teleop/devices/pico_device.py` 本次没有改。也就是说 Pico 坐标转换仍沿用原逻辑。如果 WalkerS2 右臂方向反了、旋转轴不对，再回到这个文件调右手柄坐标变换矩阵。

## 6. Motion-control 配置侧

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `source/teleop/app/configuration/robot/G2_WalkerS2/quark/quark.yaml` | 新增 | `genie_motion_control` 的 WalkerS2 启动配置，指定配置目录为 `configuration/robot/G2_WalkerS2`。 | 如果 `start_mc.sh --robot=G2_WalkerS2` 启动后仍找 G2 配置，检查这里的 `config.dir`。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/quark/rules.yaml` | 新增 | motion-control 状态机切换规则，沿用 G2 模板。 | 如果 motion-control 状态不能切到 `REACTIVE_CONTROL`，检查这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/model/default.yaml` | 新增 | 定义 WalkerS2 motion-control 的 group 组成和加载顺序。 | 如果某个 group 没加载，检查 `order` 和 `groups.includes`。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/model/right_arm.yaml` | 新增 | WalkerS2 右臂 7 关节配置，是首版 Pico 控制的核心 group。 | 如果右臂 IK 报关节名/limit 问题，先看这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/model/left_arm.yaml` | 新增 | WalkerS2 左臂 7 关节配置，首版不主动控制，但保留模型完整性。 | 如果 dual arm group 报错或 joint state 不完整，检查这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/model/waist.yaml` | 新增 | WalkerS2 腰部 2 关节配置，对应 `waist_yaw_joint`、`waist_pitch_joint`。 | 如果腰部 reset/axis 控制异常，检查这里和 `ros_nodes.py::pub_waist_pose()`。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/model/head_yaw.yaml` | 新增 | WalkerS2 头部 yaw 关节配置。 | 如果 head reset 报 group 不存在，检查这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/model/head_pitch.yaml` | 新增 | WalkerS2 头部 pitch 关节配置。 | 如果 head pitch 不动，检查这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/retarget_setting/default.yaml` | 新增 | retarget/relaxed IK 参数，首版沿用 G2 模板。 | 如果 IK 抖动、太慢、代价不合适，调这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/se3_track_setting/default.yaml` | 新增 | SE(3) 跟踪参数，首版沿用 G2 模板。 | 如果末端跟踪延迟或滤波异常，检查这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/mass_center_limits/default.yaml` | 新增 | 质心限制模板，首版沿用 G2。 | 如果 motion-control 报 balance/mass center limit，检查这里。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/ik_benckmark/default.yaml` | 新增 | IK benchmark 默认配置，首版沿用 G2。 | 主要用于 motion-control 内部 benchmark/debug。 |

首版真正最关键的是：

```text
quark/quark.yaml
model/default.yaml
model/right_arm.yaml
retarget_setting/default.yaml
se3_track_setting/default.yaml
```

如果 `genie_motion_control` 启动失败，优先看 `quark/quark.yaml`；如果启动成功但右臂不动，优先看 `right_arm.yaml` 和 `/wbc/retarget` 消息内容。

## 7. Motion-control URDF / Mesh 侧

| 文件 | 类型 | 作用 | Debug 重点 |
|---|---|---|---|
| `source/teleop/app/configuration/robot/G2_WalkerS2/description/urdf/G2_WalkerS2.urdf` | 新增 | motion-control 侧随配置保存的 WalkerS2 URDF 副本。 | 如果二进制找模型失败，需要确认它是否支持从这个路径找 URDF。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/description/urdf/G2_WalkerS2.srdf` | 新增 | 首版 SRDF，只配置相邻 link 的 disable collision。 | 如果 IK 碰撞检查误报，检查 disable collision 是否不足。 |
| `source/teleop/app/configuration/robot/G2_WalkerS2/description/meshes/*.STL` | 新增 | motion-control 侧随配置保存的 WalkerS2 mesh 副本。 | 如果 URDF mesh 加载失败，检查 URDF 中 mesh 路径和这里文件名是否匹配。 |

权限限制：

```text
source/teleop/app/share/genie_robot_description
```

这个目录当前不是 `qsh` 可写，所以 WalkerS2 的 motion-control URDF/mesh 暂时放在：

```text
source/teleop/app/configuration/robot/G2_WalkerS2/description/
```

如果 `genie_motion_control` 二进制强制从 `share/genie_robot_description/urdf/G2_WalkerS2` 找模型，需要用有权限的用户把 `description/urdf` 和 `description/meshes` 同步到 share 目录。

## 8. 常见问题定位

| 现象 | 优先检查 |
|---|---|
| `./scripts/autoteleop.sh walker_s2` 仍加载 G1/G2 原机器人 | `scripts/autoteleop.sh` 的 `SIM_CONFIG`，以及 `teleop_walker_s2.yaml` 的 `benchmark.task_name`。 |
| `Invalid robot type: G2_WalkerS2` | `source/geniesim/utils/name_utils.py::robot_type_mapping()`。 |
| `Invalid robot_cfg G2_WalkerS2.json` | `source/teleop/teleop.py::setup_robot()` 是否识别 `WalkerS2`。 |
| `/wbc/retarget` frame 是 `arm_base_link` 而不是 `waist_pitch_link` | `source/teleop/utils/ros_nodes.py::pub_mc()` 和 `robot_interface.py` 的 `arm_base_frame`。 |
| `/wbc/retarget` target frame 不是 `R_hand_link` | `source/teleop/config/robot_interface.py` 的 `ee_frames`。 |
| motion-control 收不到 WalkerS2 joint state | `source/teleop/bridge.py::_publish_hal()` 是否识别 `waist_*`、`L_*`、`R_*`。 |
| Pico trigger 还在发夹爪命令 | `source/teleop/teleop.py::parse_eef_control()` 是否因为 `fixed_hand` 直接 return。 |
| `/tf` 中没有 `base_link/R_hand_link` | `source/geniesim/app/ros_publisher/robot_interface.py::register_robot_tf()` 是否找到 WalkerS2 的 `base_link` prim。 |
| 启动时报相机 prim 不存在 | `G2_WalkerS2.json` 的 `camera` 字段和 `api_core.py` 的 viewport 相机选择。 |
| 记录数据没有图像 | 首版没有配置 WalkerS2 相机；需要补 USD Camera prim、robot_cfg camera、task camera_list。 |

## 9. 建议 Debug 顺序

1. 先单独确认仿真能加载 WalkerS2：看 `G2_WalkerS2.json`、`api_core.py`、`robot_interface.py`。

2. 再确认 ROS 状态可用：看 `/joint_states` 是否有 WalkerS2 关节名，看 `/tf` 是否有 `base_link`、`waist_pitch_link`、`R_hand_link`。

3. 再启动 motion-control：看 `start_mc.sh -s --robot=G2_WalkerS2 --no-tool` 是否选择了 `configuration/robot/G2_WalkerS2`。

4. 再检查 teleop 输入：看 `teleop.py` 是否以 `--robot_cfg G2_WalkerS2.json` 启动，Pico grip 后是否发布 `/wbc/retarget`。

5. 最后检查闭环：`/wbc/retarget` -> `/hal/joint_cmd` -> `/joint_command` -> 机器人右臂实际运动。
