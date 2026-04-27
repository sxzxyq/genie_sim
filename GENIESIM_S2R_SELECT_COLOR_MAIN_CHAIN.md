# `geniesim --config source/geniesim/config/s2r_select_color.yaml` 主链路

`geniesim --config source/geniesim/config/s2r_select_color.yaml` 实际不是 setuptools 的 console script，而是容器启动时在 [entrypoint.sh](/home/qsh/Workspace/genie_sim/scripts/entrypoint.sh:44) 里写进 shell 的 alias：`geniesim='omni_python /geniesim/main/source/geniesim/app/app.py'`。也就是说，这条命令真正进入的是 [app.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/app.py:1)。

1. [app.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/app.py:14) 启动时先做环境修正，再用 [params.py](/home/qsh/Workspace/genie_sim/source/geniesim/config/params.py:15) 读配置。顺序是先读基础配置 [config.yaml](/home/qsh/Workspace/genie_sim/source/geniesim/config/config.yaml:1)，再被你传入的 [s2r_select_color.yaml](/home/qsh/Workspace/genie_sim/source/geniesim/config/s2r_select_color.yaml:1) 覆盖，最后再吃 CLI 单项参数。  
实际对这条命令生效的关键值是：`task_name=table_task_g1`、`sub_task_name=pick_block_color`、`model_arc=pi`、`enable_ros=false`、`num_episode=1`、`seed=1`。没在 yaml 里写的，比如 `infer_host=localhost:8999`、`physics_step=120`、`rendering_step=60`，来自 dataclass 默认值。

2. [app.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/app.py:23) 用 [app_launcher.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/workflow/app_launcher.py:192) 创建 `SimulationApp`。这里真正把 Isaac Sim 拉起来，渲染器用 `cfg.app.render_mode`，物理步长是 `1/120`，渲染步长是 `1/60`。

3. 接着 [app.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/app.py:38) 无条件启用 `isaacsim.ros2.bridge`，并 `rclpy.init()`。注意：即使你的配置里 `enable_ros=false`，这一步也仍然会发生；只是后面 benchmark 数据流不会走 ROS topic。

4. [app.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/app.py:69) 在主线程里创建 `World`、[UIBuilder](/home/qsh/Workspace/genie_sim/source/geniesim/app/workflow/ui_builder.py:32)、[APICore](/home/qsh/Workspace/genie_sim/source/geniesim/app/controllers/api_core.py:60) 和 [TaskManager](/home/qsh/Workspace/genie_sim/source/geniesim/app/task_manager.py:8)。  
这里的架构很重要：主线程只负责 IsaacSim 的 render/physics loop；benchmark 逻辑跑在 `TaskManager` 的后台线程；真正改 USD/物理状态时，再通过 `APICore.run_on_render_loop/run_on_physics_loop` 回投到主线程。

5. [APICore.__init__](/home/qsh/Workspace/genie_sim/source/geniesim/app/controllers/api_core.py:128) 会先读一次基础任务定义 [table_task_g1.json](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/config/eval_tasks/table_task_g1.json:1)。这个文件定义的是“基座任务模板”：机器人型号、背景场景、工作区、通用 stage、录制相机列表、generalization 配置。  
对这个任务来说，`objects.*` 是空的，说明实例化对象不从这里摆，而是从后面的 `llm_task/pick_block_color/<id>/scene.usda` 来。

6. [TaskManager](/home/qsh/Workspace/genie_sim/source/geniesim/app/task_manager.py:14) 开后台线程，直接调 [task_benchmark.py](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/task_benchmark.py:90) 的 `main()`。  
`TaskBenchmark.evaluate_policy()` 会再读一次 [table_task_g1.json](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/config/eval_tasks/table_task_g1.json:1)，还会读 [robot_init_pose.json](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/config/robot_init_pose.json:1)，但这份 `robot_init_pose.json` 在当前 benchmark 路径里实际上没有再被使用，这是个“读了但没用到”的文件。

7. [TaskBenchmark](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/task_benchmark.py:110) 会创建 [TaskGenerator](/home/qsh/Workspace/genie_sim/source/geniesim/plugins/tgs/layout/task_generate.py:149)，生成运行期临时 task 文件到 `source/geniesim/benchmark/saved_task/table_task_g1/`。  
这里它读取的仍然是 `table_task_g1.json` 里的内容；因为这个任务 `generalization={}`、对象列表也空，所以 [task_generate.py](/home/qsh/Workspace/genie_sim/source/geniesim/plugins/tgs/layout/task_generate.py:475) 只会生成一个 `table_task_g1_0.json`，不做光照/材质/相机/初始位姿的变体扩增。  
另外，`scene.function_space_objects` 已经直接写在 `table_task_g1.json` 里了，所以 `scene_info_dir` 指向的 `scene_parameters.json` 分支在这个任务里不会走。

8. [TaskBenchmark](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/task_benchmark.py:138) 会枚举 `benchmark/config/llm_task/pick_block_color/` 下所有数字子目录。当前仓库里是 `0..9` 共 10 个实例；每个实例的 `instructions.json` 和 `problems.json` 都是 5 条，所以这条命令总共会跑 `10 * 5 * 1 = 50` 个 episode。

9. 每个实例先走 `create_policy()` 和 `create_env()`。  
`create_policy()` 因为 `model_arc=pi`，实际选的是 [PiPolicy](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/policy/pipolicy.py:30)，不是默认配置里的 `DemoPolicy`；它再通过 [websocket_client.py](/home/qsh/Workspace/genie_sim/source/geniesim/utils/comm/websocket_client.py:14) 连 `ws://localhost:8999`。  
`create_env()` 因为 `model_arc=pi`，实际选的是 [PiEnv](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/envs/pi_env.py:21)，不是默认配置里的 `DummyEnv`。

10. `create_env()` 里最关键的是 [APICore._init_robot_cfg](/home/qsh/Workspace/genie_sim/source/geniesim/app/controllers/api_core.py:825)。它会读 [G1_omnipicker.json](/home/qsh/Workspace/genie_sim/source/geniesim/app/robot_cfg/G1_omnipicker.json:1)，拿到机器人 USD、相机、夹爪、URDF、robot description 路径；然后把  
`robot/G1_omnipicker/robot.usda` 挂到 stage，  
把 `table_task_g1.json` 里的背景 `background/laboratory/laboratory_3/background.usda` 挂到 `/World`，  
再把实例 overlay `llm_task/pick_block_color/<instance_id>/scene.usda` 挂到 `/Workspace`。  
它还会尝试读取与背景 USD 同名的 sidecar JSON，也就是 `background.json`，用于做场景对象筛选；没有就跳过。

11. 机器人加载后，[UIBuilder](/home/qsh/Workspace/genie_sim/source/geniesim/app/workflow/ui_builder.py:40) 会初始化 articulation 和运动学；[robot.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/utils/robot.py:17) 解析机器人 JSON；[kinematics_solver.py](/home/qsh/Workspace/genie_sim/source/geniesim/app/controllers/kinematics_solver.py:16) 再读 `G1_omnipicker.yml` 和 `G1_omnipicker.urdf`；同时 [ikfk_utils.py](/home/qsh/Workspace/genie_sim/source/geniesim/utils/ikfk_utils.py:44) 会读 `IK-SDK/G1_NO_GRIPPER.urdf` 和 [g1_solver.yaml](/home/qsh/Workspace/genie_sim/source/geniesim/utils/IK-SDK/g1_solver.yaml:1)，用来把当前关节状态转成左右手末端位姿，供 `PiPolicy` 打包观测。

12. 环境初始化阶段，[BaseEnv](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/envs/base_env.py:216) 会读运行期临时文件 `table_task_g1_0.json`；[LLMTask](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/tasks/llm_task.py:25) 会读 `llm_task/pick_block_color/<id>/instructions.json`；每次 `set_current_task()` 时，[action_parsing.py](/home/qsh/Workspace/genie_sim/source/geniesim/plugins/ader/action/action_parsing.py:71) 会读同目录下的 `problems.json`，把里面的 DSL 解析成 `ActionList -> Follow -> PickUpOnGripper` 这套 ADER 动作树。  
如果 `problems.json` 丢了，就回退到 [default_problem.json](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/config/task_definitions/default_problem.json:1)。

13. episode 真正跑起来后，[PiEnv](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/envs/pi_env.py:32) 直接从 [DataCourier](/home/qsh/Workspace/genie_sim/source/geniesim/utils/data_courier.py:11) 取 RGB、depth、joint states；因为 `enable_ros=false`，这些数据是直接从 `APICore -> RobotInterface` 读，不经过 `PIROSNode` topic 中转。  
[PiPolicy](/home/qsh/Workspace/genie_sim/source/geniesim/benchmark/policy/pipolicy.py:46) 会把观测整理成：32 维 state、左右末端位姿、3 路 RGB、3 路 depth、自然语言 prompt、`task_name=sub_task_name`，再送去 websocket 推理。  
随后 `PiEnv.step()` 执行动作；每 30 步调用一次 `action_update()`，让 `Follow`、`PickUpOnGripper` 这些动作类更新完成状态；评分则由 [eval_utils.py](/home/qsh/Workspace/genie_sim/source/geniesim/plugins/output_system/eval_utils.py:34) 里的 `TASK_STEPS["pick_block_color"] = ["Follow", "PickUpOnGripper"]` 决定，结果最终写到 `output/benchmark/table_task_g1/pick_block_color/evaluate_ret_XX.json`。
