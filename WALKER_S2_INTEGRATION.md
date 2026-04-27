# WalkerS2 接入 GenieSim 总流程

本文档整理了将
[walker_s2_v1_world_description](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description)
接入 GenieSim 的完整流程。

重点说明三件事：

1. 每一步是为了做什么
2. 每一步的输入文件是什么
3. 每一步的输出文件是什么

本文档基于当前仓库结构整理，适合作为 `walkerS2` 的接入实施清单。

## 1. 当前已有输入

当前已经具备的原始机器人描述文件位于：

- [walker_s2_v1_world_description/urdf/s2_v1_world/s2_v1_world.urdf](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description/urdf/s2_v1_world/s2_v1_world.urdf:1)
- [walker_s2_v1_world_description/meshes/s2_v1_world](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description/meshes/s2_v1_world)
- [walker_s2_v1_world_description/meshes/s2_v1_world_complex](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description/meshes/s2_v1_world_complex)
- [walker_s2_v1_world_description/launch/display.launch.py](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description/launch/display.launch.py:1)

从当前 URDF 可以确认：

- 这是完整人形本体描述，包含头、腰、双臂、双腿
- 末端存在 `L_hand_link / R_hand_link`
- 末端前一级存在 `L_sixforce_link / R_sixforce_link`
- 当前未看到现成相机 prim
- 当前未看到现成 gripper/finger joints
- 关节命名风格为 `waist_yaw_joint`、`R_shoulder_pitch_joint` 这一类

这意味着：

- 可以先做“机器人本体接入”
- 如果要替代现有 `G1/G2` 跑 benchmark，还需要额外代码适配

## 2. 推荐目标拆分

建议把接入拆成两阶段。

### 阶段 A：最小可运行接入

目标：

- 机器人能被 Isaac Sim 正常加载
- 机器人能在 GenieSim 中作为一台机器人初始化
- 能读到 articulation
- 能做基础运动学 / 基础关节控制

### 阶段 B：完整 benchmark 接入

目标：

- 能替代现有 `G1_omnipicker / G2_omnipicker`
- 能跑 benchmark task
- 能对接相机观测
- 能对接 gripper / end effector 控制
- 能对接 policy / infer / preprocess

建议顺序：

1. 先完成阶段 A
2. 再决定是否推进阶段 B

## 3. GenieSim 现有机器人接入链

当前仓库中，现有机器人大致分成三层：

### 3.1 机器人资产层

目录示例：

- [source/geniesim/assets/robot/G1_omnipicker](/home/qsh/Workspace/genie_sim/source/geniesim/assets/robot/G1_omnipicker)
- [source/geniesim/assets/robot/G1_120s](/home/qsh/Workspace/genie_sim/source/geniesim/assets/robot/G1_120s)

作用：

- 保存 `robot.usda`
- 这是运行时真正被 Isaac Sim `reference` 到场景中的机器人

### 3.2 运行配置层

目录示例：

- [source/geniesim/app/robot_cfg/G1_omnipicker.json](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker.json:1)
- [source/geniesim/app/robot_cfg/G1_120s.json](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_120s.json:1)

作用：

- 告诉 GenieSim 机器人 USD 在哪
- base prim path 是什么
- 相机有哪些
- 末端执行器是谁
- gripper 控制关节是谁
- 运动学文件在哪

### 3.3 运动学/规划层

目录示例：

- [source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.urdf](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.urdf:1)
- [source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.yml](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.yml:1)

作用：

- 提供 URDF
- 提供 Lula/IK/cspace 配置

## 4. WalkerS2 接入总流程

下面给出建议的完整流程。

---

## Step 1：确认原始机器人描述是否可作为接入源

### 目的

确认 `walkerS2` 的原始 URDF 和 mesh 是否足够支撑后续导入。

### 输入

- [walker_s2_v1_world_description/urdf/s2_v1_world/s2_v1_world.urdf](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description/urdf/s2_v1_world/s2_v1_world.urdf:1)
- `walker_s2_v1_world_description/meshes/s2_v1_world/*.STL`
- `walker_s2_v1_world_description/meshes/s2_v1_world_complex/*.STL`

### 需要确认的事项

- 根 link 是什么
- 头部 link 是什么
- 左右臂末端 link 是什么
- 左右臂 wrist / flange / hand 是什么
- 有没有现成 camera
- 有没有现成 gripper/finger joint
- mesh 路径是否都能正确解析

### 当前可确认的结果

- 根 link：`base_link`
- 头部链路：`head_yaw_link`、`head_pitch_link`
- 左臂末端候选：`L_hand_link` / `L_sixforce_link`
- 右臂末端候选：`R_hand_link` / `R_sixforce_link`
- 当前没有现成相机
- 当前没有现成夹爪驱动关节

### 输出

一份“机器人关键信息表”，至少记录：

- base_link
- left end effector candidate
- right end effector candidate
- head links
- waist joints
- arm joints

---

## Step 2：将原始 URDF 导入 Isaac Sim，生成机器人 USD

### 目的

把 ROS/URDF 机器人转换成 GenieSim 运行时真正使用的机器人资产。

### 输入

- [s2_v1_world.urdf](/home/qsh/Workspace/genie_sim/walker_s2_v1_world_description/urdf/s2_v1_world/s2_v1_world.urdf:1)
- `walker_s2_v1_world_description/meshes/...`

### 参考模板

- [source/geniesim/assets/robot/G1_omnipicker/config.yaml](/home/qsh/Workspace/genie_sim/source/geniesim/assets/robot/G1_omnipicker/config.yaml:1)

### 这一步做什么

使用 Isaac Sim 的 URDF Importer：

- 导入 URDF
- 修正 mesh 路径
- 生成 `robot.usda`
- 检查 articulation 是否正常
- 检查 root prim 是否明确

### 推荐命名

为了减少现有代码改动，建议第一版先使用带 `G1` 前缀的名字，例如：

- `G1_walkerS2`

这样后续很多只认 `G1/G2` 的逻辑更容易复用。

### 输出

建议生成到：

- `source/geniesim/assets/robot/G1_walkerS2/robot.usda`
- `source/geniesim/assets/robot/G1_walkerS2/config.yaml`
- `source/geniesim/assets/robot/G1_walkerS2/configuration/...`

### 验收标准

- `robot.usda` 能单独打开
- articulation 初始化正常
- link/joint 层级正确
- base prim 路径明确

---

## Step 3：在 `assets/robot/` 下建立 WalkerS2 机器人资产目录

### 目的

让 GenieSim 有一套符合现有结构的机器人资产目录。

### 输入

- Step 2 生成的 `robot.usda`
- 导入配置 `config.yaml`
- 如果有拆分的 USD 配置层，也一起放入

### 输出目录建议

```text
source/geniesim/assets/robot/G1_walkerS2/
  robot.usda
  config.yaml
  configuration/
```

### 输出说明

- `robot.usda`：运行时真正加载的机器人主 USD
- `config.yaml`：URDF -> USD 的导入配置记录
- `configuration/`：Isaac Sim 生成的辅助 USD 组件

---

## Step 4：建立 GenieSim 运行配置 JSON

### 目的

告诉 GenieSim 如何加载和使用这台机器人。

### 输入

- Step 3 生成的 `robot.usda`
- Step 1 整理出的 link/joint 信息

### 参考模板

- [source/geniesim/app/robot_cfg/G1_omnipicker.json](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker.json:1)

### 输出文件建议

- `source/geniesim/app/robot_cfg/G1_walkerS2.json`

### 这一步需要填写的关键字段

- `robot.robot_name`
- `robot.base_prim_path`
- `robot.robot_usd`
- `robot.urdf_name`
- `robot.robot_description`
- `camera`
- `gripper.end_effector_name`
- `gripper.end_effector_prim_path`
- `gripper.finger_names`
- `gripper.gripper_control_joint`

### 当前对 WalkerS2 的建议

- `robot_name`：先用 `G1_walkerS2`
- `base_prim_path`：建议第一版先用 `/G1`
- 左右末端执行器：
  - 左：`L_hand_link` 或 `L_sixforce_link`
  - 右：`R_hand_link` 或 `R_sixforce_link`

### 特别说明

当前代码 [RobotCfg](/home/qsh/Workspace/genie_sim/source/geniesim/app/utils/robot.py:17) 只接受机器人名中包含：

- `G1`
- `G2`

因此第一版建议先沿用 `G1_` 前缀。

### 输出

- `source/geniesim/app/robot_cfg/G1_walkerS2.json`

---

## Step 5：建立 WalkerS2 的 URDF / YML 运动学配置

### 目的

让 Lula / IK / 运动学求解器能够识别这台机器人。

### 输入

- 原始 `s2_v1_world.urdf`
- Step 1 整理出的 joint/link 信息

### 参考模板

- [source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.urdf](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.urdf:1)
- [source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.yml](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker/G1_omnipicker.yml:1)

### 输出目录建议

```text
source/geniesim/app/robot_cfg/G1_walkerS2/
  G1_walkerS2.urdf
  G1_walkerS2.yml
```

### 这一步做什么

#### 5.1 复制一份可在 GenieSim 中使用的 URDF

输出：

- `source/geniesim/app/robot_cfg/G1_walkerS2/G1_walkerS2.urdf`

#### 5.2 编写 Lula/IK 配置文件

输出：

- `source/geniesim/app/robot_cfg/G1_walkerS2/G1_walkerS2.yml`

需要定义：

- `cspace`
- `default_q`
- `cspace_to_urdf_rules`
- `collision_spheres`
- `ee_link`
- `base_link`

### 当前 WalkerS2 的关键难点

你的关节命名是：

- `R_shoulder_pitch_joint`
- `R_elbow_roll_joint`
- `waist_yaw_joint`

而不是现有 G1/G2 使用的 `idx..` 风格。

所以这一步不能直接照抄 G1/G2 的 YML，必须按 WalkerS2 自己的关节命名重新写。

---

## Step 6：在 GenieSim 中注册 WalkerS2

### 目的

让 GenieSim 的代码逻辑真正认识这台新机器人。

### 输入

- Step 4 的 `G1_walkerS2.json`
- Step 5 的 URDF/YML
- WalkerS2 的 joint/link 映射

### 需要改动的主要代码点

#### 6.1 机器人名识别

文件：

- [source/geniesim/app/utils/robot.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/utils/robot.py:17)

作用：

- 当前只根据机器人名判断 `G1 / G2`

如果继续使用 `G1_walkerS2`，这里可以先不改。

#### 6.2 机器人关节分组映射

文件：

- [source/geniesim/utils/name_utils.py](/home/qsh/Workspace/genie_sim/source/geniesim/utils/name_utils.py:1)

作用：

- 定义 arm joints
- 定义 waist joints
- 定义 head joints
- 定义 gripper joints
- 定义机器人类型映射

需要新增：

- `G1_walkerS2` 的 joint 分组配置

#### 6.3 推理前处理

文件：

- [source/geniesim/utils/infer_pre_process.py](/home/qsh/Workspace/genie_sim/source/geniesim/utils/infer_pre_process.py:1)

作用：

- 当前只接受：
  - `G1_omnipicker`
  - `G2_omnipicker`
  - `G2_90d`

如果要进入 benchmark / policy 链路，这里必须补 `G1_walkerS2`

#### 6.4 benchmark 初始状态

文件：

- [source/geniesim/benchmark/config/robot_init_states.py](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/config/robot_init_states.py:1)

作用：

- 为不同任务定义不同机器人初始状态

如果要跑 benchmark，需要新增：

- `G1_walkerS2` 对应的 `body_state / init_arm / init_hand`

### 输出

- `name_utils.py` 中新增 WalkerS2 配置
- `infer_pre_process.py` 中新增 WalkerS2 分支
- `robot_init_states.py` 中新增 WalkerS2 初始状态

---

## Step 7：决定是否接 benchmark / task / policy

### 目的

判断 `walkerS2` 是只做“机器人接入”，还是要做“任务执行机器人替换”。

### 如果只做最小接入

做到这里即可：

- 能加载 `robot.usda`
- 能读 articulation
- 能初始化 IK / 运动学
- 能被 `robot_cfg` 正常识别

此时不必立即处理：

- benchmark task
- infer policy
- gripper 抓取逻辑
- 相机观测链路

### 如果要做 benchmark 替换

则还需要继续补：

- 任务配置文件中的 `robot_cfg`
- 相机路径
- gripper 逻辑
- 各类 action 插件对机器人 base path 的判断
- policy 输入输出适配

相关位置包括：

- `benchmark/config/eval_tasks/*.json`
- `plugins/ader/action/custom/*.py`
- `benchmark/envs/*.py`

### 当前 WalkerS2 的现实判断

由于当前 URDF：

- 没有现成相机
- 没有现成 gripper/finger joints
- 末端更像手或法兰，而不是当前 omnipicker 抓手

因此更推荐：

1. 先完成“机器人本体接入”
2. 再评估是否需要额外加相机和末端执行器
3. 最后再推进 benchmark 适配

---

## 5. 每一步输入/输出总表

| 步骤 | 目的 | 输入 | 输出 |
|---|---|---|---|
| Step 1 | 整理原始机器人信息 | `walker_s2_v1_world_description/urdf`、`meshes` | 机器人关键信息表 |
| Step 2 | URDF 导入 Isaac Sim | `s2_v1_world.urdf`、`meshes` | `robot.usda`、导入配置 |
| Step 3 | 建立机器人资产目录 | Step 2 输出 | `source/geniesim/assets/robot/G1_walkerS2/...` |
| Step 4 | 建立运行配置 JSON | Step 1/3 输出 | `source/geniesim/app/robot_cfg/G1_walkerS2.json` |
| Step 5 | 建立运动学配置 | 原始 URDF、link/joint 信息 | `G1_walkerS2.urdf`、`G1_walkerS2.yml` |
| Step 6 | 注册机器人到代码逻辑 | Step 4/5 输出 | `name_utils.py`、`infer_pre_process.py`、`robot_init_states.py` 更新 |
| Step 7 | 接 benchmark/policy | Step 6 输出 | 任务配置和 action 逻辑适配 |

---

## 6. 推荐的最小交付物

如果目标是“先把 walkerS2 放进 GenieSim”，建议第一阶段最少交付这些文件：

```text
source/geniesim/assets/robot/G1_walkerS2/robot.usda
source/geniesim/assets/robot/G1_walkerS2/config.yaml
source/geniesim/app/robot_cfg/G1_walkerS2.json
source/geniesim/app/robot_cfg/G1_walkerS2/G1_walkerS2.urdf
source/geniesim/app/robot_cfg/G1_walkerS2/G1_walkerS2.yml
```

以及这几处代码注册：

```text
source/geniesim/utils/name_utils.py
source/geniesim/utils/infer_pre_process.py
source/geniesim/benchmark/config/robot_init_states.py
```

---

## 7. 建议的实施顺序

建议按下面顺序推进：

1. 先做 URDF -> USD，确保 `robot.usda` 可用
2. 再做 `robot_cfg.json`
3. 再做 URDF/YML 运动学配置
4. 再补 `name_utils.py`
5. 最后才碰 benchmark / infer / policy

这样可以把问题逐层定位：

- 如果机器人显示不出来，问题在 USD 或 `robot_cfg`
- 如果显示出来但 IK 不通，问题在 URDF/YML
- 如果本体能动但 benchmark 不通，问题在注册/预处理/任务适配

---

## 8. 当前最推荐的第一阶段目标

针对 `walkerS2`，当前最推荐的第一阶段目标是：

**把它接成一台 GenieSim 能正常加载、初始化、读关节、做基础运动学的人形机器人。**

不建议第一步就直接对标：

- `pick_block_color`
- `drawer_task_g1`
- `omnipicker` 抓取链路

因为当前 `walkerS2` 与现有 benchmark 机器人相比，至少还缺：

- 相机
- gripper/finger joints
- 现成 benchmark 初始化状态
- 现成 policy preprocess 分支

---

## 9. 后续文档建议

建议后续再补两份配套文档：

1. `G1_walkerS2.json` 字段填写说明
2. `WalkerS2` 的 joint/link 映射表

这样后续接相机、末端执行器、benchmark 时会轻松很多。
