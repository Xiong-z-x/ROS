# 第 7 章 ROS 运行管理：自测题与参考答案

## 自测题

1. 为什么实际 ROS 系统不应该靠手动打开多个终端运行？
2. `roslaunch` 自动启动 roscore 是否意味着它就是 ROS Master？
3. launch 文件为什么不是顺序脚本？
4. YAML 参数加载到参数服务器后，节点一定会自动使用吗？为什么？
5. 私有参数和全局参数有什么区别？
6. `arg` 和 YAML 分别适合解决什么问题？
7. remap 解决什么问题？什么时候只 remap 一端会出错？
8. 命名空间适合什么场景？为什么初学阶段不应滥用？
9. rosbag 记录的是代码、参数，还是 topic 数据？
10. 为什么初学阶段不建议直接 `rosbag record -a`？
11. 如果 bag 回放后 listener 没输出，应先检查哪些命令？
12. `output="screen"` 对调试有什么帮助？
13. `roswtf` 能解决什么问题？为什么不能完全依赖它？
14. `/use_sim_time=true` 但没有 `/clock` 时，可能出现什么现象？

## 参考答案

1. 手动打开多个终端容易漏启动节点、漏设参数、顺序不一致、topic 名不统一，也不方便别人复现。实际 ROS 系统需要用 launch、参数文件和记录流程把运行方式固化下来。统一入口能降低人为误差，让排障从“输入过哪些命令”转向“系统配置是否正确”。

2. 不是。`roslaunch` 在没有 Master 时可以启动 `roscore`，但它本身不是 ROS Master。ROS Master 仍然是负责注册和发现的服务；`roslaunch` 是启动和组织节点、参数、命名空间、remap 的工具。

3. launch 文件描述要启动哪些进程、加载哪些参数、如何命名和重映射，但不保证业务逻辑按 XML 行顺序完成初始化。某个节点进程启动了，不代表它的 topic、service、TF 或硬件已经就绪。依赖另一个服务时，应在代码中显式等待，例如 `wait_for_service`，而不是依赖 launch 文件中的先后顺序。

4. 不一定。YAML 加载到参数服务器，只说明参数已经存储在 ROS 参数系统中；节点是否使用它，取决于节点代码是否读取对应参数名。有些节点只在启动时读取一次，运行中参数改变也不会自动生效。排查时要同时看 `rosparam get` 和节点代码或文档。

5. 全局参数使用以 `/` 开头的完整名字，例如 `/use_sim_time`；私有参数使用 `~` 语义，通常解析到当前节点命名空间下，例如节点 `/talker` 的 `~rate` 对应 `/talker/rate`。私有参数适合节点自己的配置，全局参数适合系统级约定，但滥用全局参数容易造成名字冲突。

6. `arg` 适合让 launch 文件在启动时可配置，例如 `model:=burger`、`rate:=5.0`；YAML 适合保存一组结构化参数，便于版本管理和复用。简单启动选项用 arg 更方便，大量参数或嵌套配置用 YAML 更清晰。二者可以配合使用。

7. remap 用来在不改代码的情况下改变 topic 或 service 名称解析结果。例如通用节点订阅 `scan`，运行时可 remap 到 `/front_laser/scan`。只 remap 一端会出错：发布者发到 `/renamed_chatter`，订阅者仍听 `/chatter`，两者就不会连接。此时 `rqt_graph` 和 `rostopic info` 能直接看出断开。

8. 命名空间适合多机器人、多传感器或大型系统分组，例如 `/robot1/cmd_vel` 和 `/robot2/cmd_vel` 避免冲突。初学阶段不应滥用，是因为命名空间会改变节点、topic、参数的实际名字，排查时更容易找错路径。先掌握相对名、全局名和私有名，再使用复杂命名空间。

9. rosbag 记录的是 topic 中传输的消息数据及时间信息，不记录节点源代码，也不完整记录参数服务器状态和仿真世界内部状态。它能回放 `/chatter`、`/scan`、`/odom` 等消息，让订阅者像收到实时数据一样工作，但不能自动复原原来的所有节点逻辑。

10. `rosbag record -a` 会录制所有 topic，初学阶段容易生成巨大文件，也会混入很多还不理解的数据，影响分析和存储。更好的做法是先用 `rostopic list` 和 `rqt_graph` 看清系统，再只录关键 topic，例如 `/cmd_vel`、`/odom`、`/scan`、`/tf`。

11. 先用 `rosbag info 文件.bag` 确认 bag 中是否包含 listener 订阅的 topic；再用 `rostopic list` 和 `rostopic echo 话题名` 确认回放时 topic 是否出现；再查 listener 是否启动、订阅的 topic 名和消息类型是否一致。如果 topic 名不一致，可能需要 remap 或改 listener 配置。

12. `output="screen"` 会把节点日志直接显示在 roslaunch 终端，初学阶段能立即看到 Python traceback、C++ 错误和 ROS 日志。没有它时，错误可能只写入 `~/.ros/log`，学生容易误以为节点“没反应”。调试阶段建议打开 screen 输出，稳定后再按项目需要调整日志方式。

13. `roswtf` 能检查环境变量、包路径、ROS 图、依赖和常见配置问题，适合作为第一轮自动诊断。但它只能发现工具规则覆盖到的问题，不能判断业务语义是否正确，例如速度值是否合理、TF 语义是否符合机器人模型、参数是否被节点代码使用。使用 `roswtf` 后仍要用 CLI 和日志验证具体状态。

14. 如果 `/use_sim_time=true`，节点会等待 `/clock` 提供时间。若没有 Gazebo 或 `rosbag play --clock` 发布 `/clock`，依赖 ROS 时间的定时器、时间戳或 TF 查询可能长时间不前进，表现为节点等待、回调不触发或 RViz/TF 时间相关警告。排查时先看 `rosparam get /use_sim_time` 和 `rostopic info /clock`。
