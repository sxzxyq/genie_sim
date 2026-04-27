# WalkerS2 Pico 采集接入方案

本文档记录 WalkerS2 在 GenieSim 中的首版 Pico 采集接入方案。首版目标是先跑通 `G2_WalkerS2` 的右臂末端遥操作与数据采集，手部保持固定，不做完整灵巧手 retarget。

## 1. 现有资源

WalkerS2 资源目录：

`source/geniesim/assets/robot/WalkerS2`

已经具备的资源：

- `Collected_WalkerS2/s2_v1.usd`：二进制 USD 总包，包含收集后的 SubUSD、材质、纹理等引用。
- `Collected_WalkerS2/SubUSDs/*.usd`：拆分出的 robot、physics、sensor、base 等 USD 子资源。
- `walker_s2_v1_world_description 2/urdf/s2_v1_world/s2_v1_world.urdf`：首版推荐使用的 WalkerS2 机器人 URDF。
- `walker_s2_v1_world_description 2/meshes/s2_v1_world/*.STL`：与上述 URDF 对应的 mesh。
- `walker_s2_description/urdf/s2/s2.urdf`：另一份身体 URDF，不含 `L_hand_link/R_hand_link`。
- `ubt_hand_v3.../hand3_v1.urdf`：左右三代灵巧手 URDF 与 mesh，首版暂不主动控制。

首版使用的 URDF 是 `s2_v1_world.urdf`。它包含 `base_link`、腰部、头部、左右 7 自由度手臂、左右手固定链接和腿部，共 35 个 link、34 个 joint。右臂控制链是：

```text
R_shoulder_pitch_joint
R_shoulder_roll_joint
R_shoulder_yaw_joint
R_elbow_roll_joint
R_elbow_yaw_joint
R_wrist_pitch_joint
R_wrist_roll_joint
```

右臂末端 frame 使用 `R_hand_link`。

## 2. 已补齐的首版硬资源

GenieSim 机器人侧：

- `source/geniesim/app/robot_cfg/G2_WalkerS2.json`：机器人总索引，告诉 `RobotCfg` 去哪里找 USD、URDF、Lula yml、末端 frame 和固定手配置。
- `source/geniesim/app/robot_cfg/G2_WalkerS2/G2_WalkerS2.urdf`：从 WalkerS2 资源目录复制出的规范 URDF。
- `source/geniesim/app/robot_cfg/G2_WalkerS2/G2_WalkerS2.yml`：Lula 运动学配置，首版只把右臂 7 关节放入 `cspace`，腰、头、左臂和腿部通过 `cspace_to_urdf_rules` 固定。
- `source/geniesim/config/teleop_walker_s2.yaml`：WalkerS2 专用 teleop 配置。
- `source/geniesim/benchmark/config/eval_tasks/table_task_walker_s2.json`：WalkerS2 专用任务配置。

Pico / motion-control 侧：

- `source/teleop/app/configuration/robot/G2_WalkerS2/model/*.yaml`：WalkerS2 腰、头、左右臂 joint group 配置。
- `source/teleop/app/configuration/robot/G2_WalkerS2/quark/quark.yaml`：motion-control 启动配置，配置目录指向 `configuration/robot/G2_WalkerS2`。
- `source/teleop/app/configuration/robot/G2_WalkerS2/description/urdf/G2_WalkerS2.urdf`：motion-control 侧随配置保存的 WalkerS2 URDF 副本。
- `source/teleop/app/configuration/robot/G2_WalkerS2/description/meshes/`：motion-control 侧随配置保存的 WalkerS2 mesh 副本。

注意：`source/teleop/app/share/genie_robot_description` 当前归属用户是 `1234:1234`，当前用户无法直接写入。因此首版把 motion-control 的 URDF 和 mesh 备份放到了 writable 的 `configuration/robot/G2_WalkerS2/description/` 下。如果 `genie_motion_control` 二进制强制从 `share/genie_robot_description/urdf/G2_WalkerS2` 查找模型，还需要后续用有权限的用户把这份 description 同步到 share 目录。

## 3. 机器人接入链路

1. `scripts/autoteleop.sh walker_s2` 选择 WalkerS2 模式。

2. 仿真进程启动：

```bash
omni_python ./source/geniesim/app/app.py --config ./source/geniesim/config/teleop_walker_s2.yaml
```

3. `app.py` 读取默认配置、`config.yaml` 和 `teleop_walker_s2.yaml`，得到 `cfg.benchmark.task_name = table_task_walker_s2`。

4. `TaskBenchmark` 读取 `source/geniesim/benchmark/config/eval_tasks/table_task_walker_s2.json`。

5. `TaskBenchmark.create_env()` 调用：

```python
api_core.init_robot_cfg("G2_WalkerS2.json", scene_usd, init_position, init_rotation, sub_usd_path)
```

6. `APICore._init_robot_cfg()` 读取 `source/geniesim/app/robot_cfg/G2_WalkerS2.json`，并按 `robot_usd` 字段引用机器人 SubUSD：

```text
source/geniesim/assets/robot/WalkerS2/Collected_WalkerS2/SubUSDs/s2_hand4_v1.usd
```

7. `APICore._init_robot()` 把 `RobotCfg` 交给 `UIBuilder._init_solver()`，由 `Kinematics_Solver` 读取：

```text
source/geniesim/app/robot_cfg/G2_WalkerS2/G2_WalkerS2.yml
source/geniesim/app/robot_cfg/G2_WalkerS2/G2_WalkerS2.urdf
```

8. `LulaKinematicsSolver` 使用 `.yml + .urdf` 建立右臂运动学模型，`ArticulationKinematicsSolver` 把该模型绑定到 Isaac Sim 的 live articulation。

9. `RobotInterface` 发布 `/joint_states`、`/tf`，并订阅 `/joint_command`，最终由 Isaac `ArticulationController` 把 joint command 施加到 WalkerS2 articulation。

## 4. Pico 交互链路

`scripts/autoteleop.sh walker_s2` 会启动四个进程：

1. GenieSim 仿真进程：加载 WalkerS2 和任务场景。

2. `source/teleop/bridge.py`：把 motion-control 输出的 `/hal/joint_cmd` 转成 Isaac 使用的 `/joint_command`。

3. `source/teleop/app/bin/start_mc.sh -s --robot=G2_WalkerS2 --no-tool`：启动 `genie_motion_control`，并强制使用 WalkerS2 配置，`-s` 用来清理旧 robot cache。

4. `source/teleop/teleop.py --robot_cfg G2_WalkerS2.json --teleop_config ./source/geniesim/config/teleop_walker_s2.yaml`：监听 Pico UDP 输入并发布 retarget 指令。

Pico 到机器人动作的数据流是：

```text
Pico UDP JSON
-> PicoDevice.parse_pico_command()
-> TeleOp.parse_arm_control()
-> SimNode.parse_delta_pose()
-> /wbc/retarget
-> genie_motion_control
-> /hal/joint_cmd
-> bridge.py
-> /joint_command
-> Isaac ArticulationController
-> WalkerS2 articulation
```

首版固定手逻辑：

- `G2_WalkerS2.json` 中 `gripper_type` 设置为 `fixed`。
- `teleop.py` 检测到 `WalkerS2` 后跳过 `parse_eef_control()`。
- Pico trigger 会被解析，但不会向不存在的 `idx41/idx81` omnipicker 夹爪关节下发命令。

## 5. 关键代码适配点

- `source/teleop/config/robot_interface.py`：新增 `RobotType.G2_WALKER_S2`，定义 WalkerS2 的 base frame、arm base frame、左右末端 frame、关节组。
- `source/teleop/utils/name_utils.py`：新增 WalkerS2 joint name 列表。
- `source/teleop/utils/ros_nodes.py`：根据 `robot_name` 选择 WalkerS2 frames；`pub_mc()` 不再硬编码 `arm_base_link`；WalkerS2 不发布 right tool group。
- `source/teleop/teleop.py`：支持 `G2_WalkerS2.json` 和 `--teleop_config`；固定手时跳过夹爪命令。
- `source/teleop/bridge.py`：支持 `waist_*`、`L_*`、`R_*` 形式的 WalkerS2 关节名。
- `source/geniesim/utils/name_utils.py`：新增 `G2_WalkerS2` 的 benchmark robot type mapping。
- `source/geniesim/utils/data_courier.py`：允许 `G2_WalkerS2` 使用空相机映射，避免直接抛 `Invalid robot cfg`。
- `source/geniesim/app/controllers/api_core.py`：viewport 相机改为从 robot config 中取，不再固定 `/G1/...` 或 `/genie/...`。
- `source/geniesim/app/ros_publisher/robot_interface.py`：WalkerS2 关节加入动态 TF 名单，并且只追加真实存在的 `/genie/...` legacy TF。

## 6. 建议阅读顺序

| 顺序 | 文件 | 一句话作用 |
|---:|---|---|
| 1 | `scripts/autoteleop.sh` | 看清 Pico 采集一次启动哪四个进程，以及 WalkerS2 模式如何切换配置。 |
| 2 | `source/geniesim/config/teleop_walker_s2.yaml` | 确认 WalkerS2 teleop 使用哪个 task、sub_task 和记录设置。 |
| 3 | `source/geniesim/app/app.py` | 理解 config 加载后如何创建 AppLauncher、APICore、TaskManager。 |
| 4 | `source/geniesim/benchmark/task_benchmark.py` | 找到任务配置如何选 robot_cfg，并调用 `api_core.init_robot_cfg()`。 |
| 5 | `source/geniesim/benchmark/config/eval_tasks/table_task_walker_s2.json` | 看任务如何指定 WalkerS2 robot、scene、robot_init_pose。 |
| 6 | `source/geniesim/app/controllers/api_core.py` | 看机器人 USD、场景 USD、ROS、TF、关节控制如何初始化。 |
| 7 | `source/geniesim/app/utils/robot.py` | 看 `G2_WalkerS2.json` 每个字段如何变成 `RobotCfg` 运行时对象。 |
| 8 | `source/geniesim/app/workflow/ui_builder.py` | 看 articulation 和 Lula/Isaac 运动学求解器如何绑定。 |
| 9 | `source/geniesim/app/controllers/kinematics_solver.py` | 看 `.yml + .urdf` 如何进入 `LulaKinematicsSolver`。 |
| 10 | `source/geniesim/app/ros_publisher/base.py` | 看 `/joint_command` 如何接到 Isaac `ArticulationController`。 |
| 11 | `source/geniesim/app/ros_publisher/robot_interface.py` | 看 `/joint_states`、`/tf`、camera topics 如何发布。 |
| 12 | `source/teleop/teleop.py` | 看 Pico 主循环如何把输入分成手臂、手部、腰部、reset、recording。 |
| 13 | `source/teleop/devices/pico_device.py` | 看 Pico 原始 JSON 如何转成左右手柄 delta pose 和按键语义。 |
| 14 | `source/teleop/utils/ros_nodes.py` | 看 delta pose 如何变成 `/wbc/retarget` 的末端目标。 |
| 15 | `source/teleop/app/bin/start_mc.sh` | 看 motion-control 如何选择机器人配置目录并启动二进制。 |
| 16 | `source/teleop/app/configuration/robot/G2_WalkerS2/*` | 看 WalkerS2 的 motion-control 关节组、retarget、quark 配置。 |
| 17 | `source/teleop/bridge.py` | 看 motion-control 输出如何桥接成仿真机器人最终执行的 `/joint_command`。 |

## 7. 验证标准

仿真侧：

- `omni_python ./source/geniesim/app/app.py --config ./source/geniesim/config/teleop_walker_s2.yaml` 能启动。
- `/joint_states` 中能看到 `R_shoulder_pitch_joint` 等 WalkerS2 关节。
- `/tf` 中能看到 `base_link`、`waist_pitch_link`、`R_hand_link`。

motion-control 侧：

- `source/teleop/app/bin/start_mc.sh -s --robot=G2_WalkerS2 --no-tool` 不再进入交互式 robot 选择。
- 能订阅 `/hal/joint_state`。
- 收到 `/wbc/retarget` 后能发布 `/hal/joint_cmd`。

Pico 采集侧：

- 右手 Pico grip 开启后，WalkerS2 右臂末端跟随移动。
- Pico trigger 不再向 `idx41_gripper_l_outer_joint1` 或 `idx81_gripper_r_outer_joint1` 发命令。
- 采集结束后输出数据至少包含 `/joint_states`、`/tf` 和 `recording_info.json`。

## 8. 后续扩展

- 如果需要图像采集，需要在 WalkerS2 USD 中补真实 Camera prim，并把 `G2_WalkerS2.json` 的 `camera` 和 `table_task_walker_s2.json` 的 `recording_setting.camera_list` 对齐。
- 如果需要简化手控制，可以把 Pico trigger 映射成若干手指联动关节。
- 如果需要完整灵巧手，需要把左右 `hand3_v1.urdf` 合入主 URDF/USD，并补 motion-control/teleop 的手部 retarget 配置。
