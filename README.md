# ROS1 零基础自学指导书

本仓库用于编写一本面向零基础大学生的 ROS1 自学指导书。当前上册只围绕 **ROS1 Noetic + Ubuntu 20.04 基础学习** 展开，目标是让读者从不会使用 Ubuntu 和 ROS，逐步具备独立安装、观察、编写、组织和排查 ROS1 系统的能力。

最终合订版文档：

- [ROS1 零基础自学指导书：最终版](ROS1零基础自学指导书-最终版.md)

## 读者对象

本书默认读者：

- 没有 Ubuntu 使用经验。
- 没有 Linux 命令行经验。
- 没有 ROS 经验。
- 具备基本编程概念，但不要求机器人系统开发基础。

本书的写法不是“命令速查表”，而是按 **概念 -> 命令/代码 -> 观察结果 -> 原因解释 -> 常见错误** 的顺序组织。每个重要概念都尽量配一个可运行实验、观察命令、图示或排障路径。

## 主线环境

| 项目 | 本书主线 |
|---|---|
| 操作系统 | Ubuntu 20.04 Focal Fossa |
| ROS 版本 | ROS1 Noetic Ninjemys |
| 构建系统 | catkin，主命令使用 `catkin_make` |
| 编程语言 | Python 3 先上手，C++14 补工程结构 |
| 图形工具 | rqt、RViz、Gazebo Classic |
| 基础案例 | turtlesim、beginner_tutorials |
| 移动机器人案例 | TurtleBot3 或同类移动机器人仿真 |

ROS Noetic 已于 **2025-05-31** 到达官方 EOL。本书继续选择 Noetic，是为了教授 ROS1 体系、维护历史项目和为后续平台适配研究打基础，不是建议新机器人项目默认继续优先选择 ROS1。

## 学完以后应达到的能力

完成本书后，读者应能做到：

- 解释 ROS 是什么、解决什么问题，以及为什么 ROS 不是传统操作系统。
- 独立搭建 Ubuntu 20.04 + ROS Noetic 学习环境。
- 使用 ROS CLI 观察节点、话题、服务、参数、TF 和计算图。
- 创建 catkin 工作空间和功能包。
- 用 Python 和 C++ 编写基础发布者、订阅者、服务端、客户端。
- 使用 launch、YAML 参数、命名空间、remap、日志和 rosbag 管理可复现实验。
- 理解 TF、URDF、RViz、Gazebo 在机器人系统中的位置。
- 启动并观察移动机器人仿真系统。
- 完成一个能启动、能观察、能控制、能记录、能复现的小型综合项目。

## 文档结构

### 全局设计文档

- [教材总纲](docs/01-教材总纲.md)：全书定位、章节结构、学习闭环和验收标准。
- [安装方法矩阵](docs/02-安装方法矩阵.md)：官方 apt、虚拟机、WSL2、Docker、一键安装、源码构建的取舍。
- [章节写作模板](docs/03-章节写作模板.md)：每章必须包含的教学单元。
- [资料来源与事实边界](docs/04-资料来源与事实边界.md)：官方资料、开源仓库、中文社区资料的使用优先级。
- [术语与常见误区](docs/05-术语与常见误区.md)：ROS1 入门必须先纠正的概念错误。

### 主体章节

| 章节 | 文件 | 核心问题 |
|---:|---|---|
| 1 | [Ubuntu 与 Linux 入门](chapters/01-ubuntu-linux入门.md) | 终端、目录、权限、APT、环境变量为什么是 ROS 学习底座 |
| 2 | [ROS1 基本概念](chapters/02-ros1基本概念.md) | Master、Node、Topic、Message、Service、Action、Parameter Server 如何组成 ROS 计算图 |
| 3 | [ROS1 安装方法完整说明](chapters/03-ros1安装方法完整说明.md) | 官方 apt、虚拟机、WSL2、Docker、鱼香 ROS、源码构建分别适合什么场景 |
| 4 | [第一个 ROS 系统](chapters/04-第一个ros系统.md) | 用 turtlesim 观察节点、话题、消息和 rqt_graph |
| 5 | [catkin 工作空间与功能包](chapters/05-catkin工作空间与功能包.md) | `catkin_ws/src`、`package.xml`、`CMakeLists.txt`、`devel/setup.bash` 的关系 |
| 6 | [Python 与 C++ 编写 ROS 节点](chapters/06-python与cpp编写ros节点.md) | 用 rospy/roscpp 写发布订阅和 service，并理解 CMake/消息生成 |
| 7 | [ROS 运行管理](chapters/07-ros运行管理.md) | 用 launch、YAML、参数、remap、日志和 rosbag 组织可复现实验 |
| 8 | [机器人坐标、模型与可视化](chapters/08-机器人坐标模型与可视化.md) | TF、URDF、RobotModel、RViz 如何表达空间关系 |
| 9 | [仿真与移动机器人入门](chapters/09-仿真与移动机器人入门.md) | Gazebo/RViz、`/cmd_vel`、`/odom`、`/scan`、`/tf` 如何组成移动机器人仿真系统 |
| 10 | [综合项目](chapters/10-综合项目.md) | 如何交付一个可启动、可观察、可控制、可记录、可复现的 ROS1 小项目 |

## 推荐学习路径

建议按章节顺序学习，不要跳过 Ubuntu、catkin 和运行管理部分：

1. 先完成第 1-4 章，确保能安装环境、运行 `roscore`、看懂 turtlesim 计算图。
2. 再完成第 5-7 章，确保能创建包、写节点、用 launch 和 rosbag 组织实验。
3. 最后完成第 8-10 章，理解坐标、模型、可视化、仿真和综合项目交付。

每章都应完成：

- 最小可运行实验。
- 正确现象检查。
- 高频错误排查。
- 本章自测题。
- 延伸阅读。

## 安装方法边界

本书会提及多种安装和运行方式，但不会把它们混成同一条主线：

| 方法 | 本书定位 |
|---|---|
| Ubuntu 20.04 + 官方 apt | 新手主线 |
| Ubuntu 20.04 虚拟机 | 零基础课堂推荐载体 |
| 原生 Ubuntu 20.04 | 性能和硬件访问更好，适合实验室机器 |
| WSL2 | Windows 学生的前期命令行和轻量实验备用路径 |
| Docker | 课堂兜底、环境隔离、CI 和批量复现工具 |
| 鱼香 ROS 一键安装 | 国内网络与 rosdep/换源辅助工具，不替代官方原理 |
| 源码构建 | 高级理解和后续平台适配铺垫，不作为新手主线 |

## 资料来源原则

核心技术结论优先依据：

- ROS.org、REP、ROS Wiki 镜像、docs.ros.org、官方 GitHub。
- `ros_comm`、`catkin`、`ros_tutorials`、`robot_state_publisher`、TurtleBot3 等上游仓库。
- `A Gentle Introduction to ROS`、Autolabor、鱼香 ROS、古月居等成熟资料用于教学节奏、中文表达和排障补充。

中文社区资料用于帮助理解和排障，不能覆盖官方事实边界。

## 关键参考链接

- ROS Noetic EOL：https://www.ros.org/blog/noetic-eol/
- REP-3 目标平台：https://www.ros.org/reps/rep-0003.html
- ROS Noetic Ubuntu 安装：https://mirror.umd.edu/roswiki/noetic%282f%29Installation%282f%29Ubuntu.html
- ROS Tutorials：https://mirror.umd.edu/roswiki/ROS%282f%29Tutorials.html
- ROS Technical Overview：https://mirror.umd.edu/roswiki/ROS%282f%29Technical%2820%29Overview.html
- catkin：https://github.com/ros/catkin
- robot_state_publisher：https://github.com/ros/robot_state_publisher
- TurtleBot3 e-Manual：https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/
- TurtleBot3 GitHub：https://github.com/ROBOTIS-GIT/turtlebot3
- 鱼香 ROS：https://fishros.org.cn/
- Autolabor ROS 文档：https://autolaborcenter.github.io/pm1-docs-sphinx/user-guide/using-ros/doc.html
- A Gentle Introduction to ROS：https://jokane.net/agitr/

## 范围边界

本册不展开：

- 后续平台部署实操。
- 交叉编译实操。
- Yocto/meta-ros 实操。
- 把源码构建作为新手主线。
- 把 ROS2 作为主体实现路线。
- 把 SLAM、导航、机械臂、PX4 等高级内容写成算法教材。

本册结尾只保留后续学习方向：掌握 ROS1 基础后，再进入更复杂的平台适配、源码构建、依赖移植和系统验证。

## 当前审查状态

当前主体 10 章均已包含：

- 概念解释。
- 最小可运行实验。
- 命令或代码示例。
- 正确现象说明。
- 高频错误与排查路径。
- Mermaid 图或文本成果图。
- 本章自测。
- 延伸阅读。

需要注意：本仓库当前是在 Windows 文档工作区中编辑教材，文档结构和事实边界已做本地校验；ROS/Gazebo 命令本身需要在 Ubuntu 20.04 + ROS Noetic 环境中执行。
