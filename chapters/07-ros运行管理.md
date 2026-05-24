# 第 7 章 ROS 运行管理

## 本章解决什么问题

到目前为止，已经可以手动打开多个终端运行节点。但实际 ROS 系统不会依赖“记住打开十几个终端”来运行。一个稍微完整的机器人系统可能包含底盘驱动、传感器驱动、状态估计、地图、导航、可视化、日志和数据记录。如果每次都手动输入命令，实验无法稳定复现，错误也较难定位。

本章讲 ROS1 的运行管理工具：`roslaunch`、参数服务器、YAML 配置、remap、命名空间、日志、rosbag、`roswtf` 和仿真时间。核心目标是把多个节点组织成一个可复现实验：同一份配置、同一条启动命令、同一套观察方法、同一份记录数据。

必须先纠正一个误区：launch 文件不是普通顺序脚本。它描述要启动哪些节点、加载哪些参数、如何命名和重映射，但不能保证写在前面的节点业务逻辑一定先完成初始化。节点之间的依赖要通过 topic、service、action 和显式等待机制处理。

## 学习完成后应达到的能力

- 用 `roslaunch` 启动多个节点。
- 编写最小 launch 文件。
- 用 YAML 管理参数。
- 使用 `rosparam list/get/set/dump/load` 操作参数服务器。
- 理解私有参数、全局参数和命名空间。
- 使用 remap 改变 topic 名。
- 使用 rosbag 录制、查看、回放数据。
- 使用 `roswtf` 做第一轮自动诊断。
- 解释 `/clock`、`use_sim_time` 与 rosbag/仿真的关系。
- 使用日志和 CLI 判断系统启动失败原因。
- 解释“能一键启动”和“能复现实验”之间的区别。

## 7.1 本章在全书中的位置

第 6 章已经能写节点，但节点还像散落的零件。本章把节点、参数、topic 名和数据记录组织成一个可重复运行的小系统。

机器人系统的工程化能力从这里开始。后面启动 RViz、Gazebo、移动机器人仿真、TF 和导航时，几乎都会依赖 launch 和参数文件。

## 7.2 必须理解的概念

| 概念 | 简明定义 | 容易误解的点 |
|---|---|---|
| `roslaunch` | 按 XML 配置启动一组 ROS 节点并设置参数 | 不是保证业务顺序执行的 shell 脚本 |
| launch 文件 | `.launch` XML 文件，描述节点、参数、命名空间等 | 写在文件里不等于节点一定能启动成功 |
| 参数服务器 | ROS Master 提供的参数存储服务 | 参数加载后，节点不会自动使用，代码必须读取 |
| YAML | 常用于保存结构化参数的文本格式 | 缩进错误会导致参数结构完全变掉 |
| 私有参数 | 节点私有命名空间下的参数，如 `~rate` | 它不是 Python/C++ 的私有变量 |
| remap | 运行时重映射 topic/service 名称 | 不改变代码，只改变名称解析结果 |
| 命名空间 | 给节点、topic、参数加前缀的组织方式 | 滥用会让初学者找不到真实名称 |
| rosbag | 记录和回放 ROS topic 数据的工具 | 记录的是消息数据，不是节点代码和算法状态 |
| `roswtf` | ROS1 自动诊断工具 | 只能提示常见环境和图结构问题，不能替代理解 |
| `/clock` | 仿真或回放发布的时间 topic | 只有启用 `use_sim_time` 的节点才会使用它 |
| 日志 | ROS 节点输出诊断信息的机制 | `print` 不是 ROS 工程中的主要日志方式 |

## 7.3 为什么需要 launch

如果每次运行系统都要手动执行：

```bash
roscore
rosrun beginner_tutorials talker.py
rosrun beginner_tutorials listener.py
rosparam set /talker/rate 2.0
rosbag record /chatter
```

问题很快出现：

- 顺序容易记错。
- 参数容易漏设。
- 节点名字不统一。
- topic 重命名要改代码。
- 数据记录路径和 topic 容易不一致。
- 不能方便交给别人复现。
- 课堂上 30 台电脑较难保持一致。

`roslaunch` 的作用是把运行配置写进文件，让系统启动可重复。它还会在当前没有 ROS Master 时自动启动一个 core 系统，因此很多时候可以直接运行 `roslaunch beginner_tutorials chatter.launch`，不必单独先开 `roscore`。

但这不意味着 launch 文件是“万能启动脚本”。它能启动进程、设置参数、组织名字，却不能替代程序本身保证某个服务一定已经准备好。客户端代码仍应使用 `wait_for_service` 等机制等待依赖就绪。

## 7.4 launch 文件最小结构

进入包：

```bash
source ~/catkin_ws/devel/setup.bash
roscd beginner_tutorials
mkdir -p launch
nano launch/chatter.launch
```

写入：

```xml
<launch>
  <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen" />
  <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen" />
</launch>
```

运行：

```bash
roslaunch beginner_tutorials chatter.launch
```

解释：

| XML 元素或属性 | 作用 |
|---|---|
| `<launch>` | launch 文件根元素 |
| `<node>` | 声明要启动一个节点 |
| `pkg` | 节点所在 ROS 包名 |
| `type` | 包内可执行文件名 |
| `name` | 节点运行时名称 |
| `output="screen"` | 把节点日志输出到 roslaunch 终端 |

另开终端观察：

```bash
source ~/catkin_ws/devel/setup.bash
rosnode list
rostopic list
rostopic info /chatter
rqt_graph
```

正确现象：

- `/talker` 和 `/listener` 都在节点列表中。
- `/chatter` 存在。
- `rqt_graph` 显示 `/talker -> /chatter -> /listener`。

## 7.5 launch 文件不是顺序脚本

很多学生会以为：

```xml
<node name="server" ... />
<node name="client" ... />
```

就表示 server 一定完全启动后 client 才开始运行。这个理解不可靠。launch 文件描述的是“要启动哪些进程”，不是“业务逻辑按行执行”。即使进程启动顺序接近 XML 顺序，服务注册、topic 建连、参数读取和设备初始化也都需要时间。

正确做法：

- 客户端调用 service 前使用 `rospy.wait_for_service` 或 C++ 等待逻辑。
- 订阅者不应假定启动瞬间就能收到第一条消息。
- 需要参数的节点在启动时显式读取参数，并对缺失参数给默认值或报错。
- 复杂系统用日志和状态 topic 表示“准备好”，不应依赖 XML 行号。

这个原则在真实机器人里非常重要。比如激光雷达驱动进程启动了，不代表硬件已经出数据；导航节点启动了，不代表 TF 树已经完整。

## 7.6 让节点实际使用参数

第 6 章的 `talker.py` 固定以 1 Hz 发布固定前缀。为了验证参数服务器的作用，本节把它改成读取私有参数。

打开：

```bash
roscd beginner_tutorials
nano scripts/talker.py
```

把核心代码改成：

```python
#!/usr/bin/env python3
from typing import NoReturn

import rospy
from std_msgs.msg import String


def main() -> NoReturn:
    rospy.init_node("talker", anonymous=False)
    rate_hz = float(rospy.get_param("~rate", 1.0))
    text_prefix = str(rospy.get_param("~text_prefix", "hello ros"))

    pub = rospy.Publisher("chatter", String, queue_size=10)
    rate = rospy.Rate(rate_hz)
    count = 0

    while not rospy.is_shutdown():
        msg = String(data=f"{text_prefix} {count}")
        pub.publish(msg)
        rospy.loginfo("published: %s", msg.data)
        count += 1
        rate.sleep()

    raise SystemExit


if __name__ == "__main__":
    main()
```

关键点：

- `~rate` 是节点私有参数，若节点名是 `/talker`，对应参数通常是 `/talker/rate`。
- 第二个参数是默认值。没有设置参数时，节点仍能以默认值运行。
- YAML 或 launch 只是把参数放进参数服务器，节点代码不读取，就不会产生行为变化。

授权仍需保持：

```bash
chmod +x scripts/talker.py
```

## 7.7 参数服务器与 YAML

参数适合放低频配置。例如发布频率、最大速度、文件路径、开关选项。不应把高频传感器数据放进参数服务器。

创建配置目录：

```bash
roscd beginner_tutorials
mkdir -p config
nano config/talker.yaml
```

写入：

```yaml
rate: 2.0
text_prefix: "hello launch"
```

修改 launch：

```xml
<launch>
  <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen">
    <rosparam command="load" file="$(find beginner_tutorials)/config/talker.yaml" />
  </node>

  <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen" />
</launch>
```

运行：

```bash
roslaunch beginner_tutorials chatter.launch
```

另开终端查看参数：

```bash
source ~/catkin_ws/devel/setup.bash
rosparam list
rosparam get /talker/rate
rosparam get /talker/text_prefix
```

正确现象：

```text
2.0
hello launch
```

再观察 topic：

```bash
rostopic echo /chatter
```

应能看到消息前缀变成 `hello launch`，频率接近 2 Hz。可以粗略检查频率：

```bash
rostopic hz /chatter
```

## 7.8 `rosparam` 常用命令

`rosparam` 可以在命令行操作参数服务器：

```bash
rosparam list
rosparam get /talker/rate
rosparam set /talker/rate 5.0
rosparam dump /tmp/talker_params.yaml /talker
rosparam load /tmp/talker_params.yaml /talker
rosparam delete /talker/rate
```

但要注意：运行中的节点是否会立刻响应参数变化，取决于节点代码。第 7.6 节的 `talker.py` 在启动时读取一次参数，之后不会自动重新读取。因此执行：

```bash
rosparam set /talker/rate 5.0
```

不一定会让正在运行的 `talker.py` 立刻变成 5 Hz。要么重启节点，要么把代码写成循环中定期读取参数，或者使用更高级的动态参数机制。初学阶段先掌握“启动参数”即可。

## 7.9 全局参数、私有参数和命名

ROS 名称有全局名、相对名和私有名。初学阶段先掌握下面表格：

| 写法 | 例子 | 解析思路 |
|---|---|---|
| 全局名 | `/chatter`、`/talker/rate` | 从根命名空间开始 |
| 相对名 | `chatter` | 根据当前节点或命名空间解析 |
| 私有名 | `~rate` | 解析到当前节点私有命名空间下 |

在 Python 中：

```python
rate_hz = rospy.get_param("~rate", 1.0)
```

如果节点名是 `/talker`，它通常读取 `/talker/rate`。

launch 中写在 `<node>` 内部的 `<param>` 或 `<rosparam>` 通常会进入节点私有命名空间：

```xml
<node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen">
  <param name="rate" value="2.0" />
</node>
```

这等价于给 `/talker/rate` 设置值。学生最常见错误是把参数加载到了 `/rate`，但代码读取的是 `~rate`，于是节点仍使用默认值。

## 7.10 `arg`：让 launch 文件可配置

如果不想每次改 XML 文件，可以使用 `arg`：

```xml
<launch>
  <arg name="rate" default="2.0" />
  <arg name="text_prefix" default="hello arg" />

  <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen">
    <param name="rate" value="$(arg rate)" />
    <param name="text_prefix" value="$(arg text_prefix)" />
  </node>

  <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen" />
</launch>
```

默认运行：

```bash
roslaunch beginner_tutorials chatter.launch
```

覆盖参数运行：

```bash
roslaunch beginner_tutorials chatter.launch rate:=5.0 text_prefix:="fast hello"
```

`arg` 的价值是让 launch 文件变成可复用模板。比如同一个机器人模型，可以用不同参数启动不同传感器配置。

## 7.11 remap：改变名字而不改代码

假设 talker 代码发布相对 topic `chatter`，listener 代码订阅相对 topic `chatter`。如果想让它们在运行时使用另一个 topic 名，可以用 remap：

```xml
<launch>
  <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen">
    <remap from="chatter" to="renamed_chatter" />
  </node>

  <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen">
    <remap from="chatter" to="renamed_chatter" />
  </node>
</launch>
```

运行后查看：

```bash
rostopic list
rostopic info /renamed_chatter
rostopic echo /renamed_chatter
```

remap 的价值是：代码保持通用，运行时按系统需要改接口名。真实项目中，经常会把通用算法节点的输入从默认名 remap 到机器人实际发布的 topic 名。

常见错误是只 remap 一端。例如发布者被 remap 到 `/renamed_chatter`，订阅者仍订阅 `/chatter`，两者就不会连接。此时 `rqt_graph` 会非常直观地显示断开的两条线。

## 7.12 命名空间

命名空间用于组织大型系统。例如两个机器人都发布 `chatter` 会冲突，可以放入不同命名空间：

```xml
<launch>
  <group ns="robot1">
    <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen" />
    <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen" />
  </group>

  <group ns="robot2">
    <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen" />
    <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen" />
  </group>
</launch>
```

此时 topic 可能变为：

```text
/robot1/chatter
/robot2/chatter
```

节点名可能变为：

```text
/robot1/talker
/robot1/listener
/robot2/talker
/robot2/listener
```

初学阶段不应滥用命名空间，但要知道它解决的是名字冲突和系统组织问题。后续多机器人、仿真机器人和真实机器人同时运行时，命名空间会非常重要。

## 7.13 include：拆分 launch 文件

随着系统变复杂，一个 launch 文件会越来越长。`include` 可以把子系统拆成多个文件：

```xml
<launch>
  <include file="$(find beginner_tutorials)/launch/chatter.launch" />
</launch>
```

常见结构：

```text
launch/
  bringup.launch
  sensors.launch
  visualization.launch
  bag_record.launch
```

本章只要求掌握最小 `include` 的读写方式。第 10 章综合项目会把 bringup、RViz、参数和数据记录组织得更完整。

## 7.14 日志

ROS 节点通常使用日志而不是普通 `print`。Python 中：

```python
rospy.logdebug("debug message")
rospy.loginfo("info message")
rospy.logwarn("warning message")
rospy.logerr("error message")
```

C++ 中：

```cpp
ROS_DEBUG("debug message");
ROS_INFO("info message");
ROS_WARN("warning message");
ROS_ERROR("error message");
```

日志会出现在：

- 当前终端，尤其当 launch 中设置 `output="screen"`。
- `/rosout` topic。
- `~/.ros/log` 目录下的日志文件。

查看日志目录：

```bash
ls ~/.ros/log
ls -l ~/.ros/log/latest
```

使用图形工具观察日志：

```bash
rqt_console
```

当节点启动失败时，`output="screen"` 很适合教学和调试，因为 Python traceback、C++ 报错和 ROS 日志会直接出现在 roslaunch 终端。真实项目里也可以通过日志文件追踪失败原因。

## 7.15 rosbag：记录和回放实验

rosbag 是 ROS1 的数据记录与回放工具。它记录的是 topic 中流动的消息数据，不是节点代码，也不是 Python/C++ 程序的内部变量。

它的价值较大：

- 调试时保存现场。
- 不连接真实传感器也能回放数据。
- 实验可以复现。
- 教师可以提供标准数据集。
- 算法节点可以用同一份数据反复测试。

rosbag 的基本数据流可以理解为：发布者、传感器或仿真节点持续向 topic 发送消息；`rosbag record` 订阅这些 topic 并把消息写入 `.bag` 文件；`rosbag play` 读取 `.bag` 文件并按时间重新发布消息；listener、算法节点或 RViz 像接收实时数据一样接收回放数据。

录制 `/chatter`：

```bash
mkdir -p ~/bagfiles
cd ~/bagfiles
rosbag record -O chatter_demo /chatter /rosout
```

停止录制：按 `Ctrl+C`。

查看 bag 信息：

```bash
rosbag info chatter_demo.bag
```

应关注：

- 记录时长。
- 文件大小。
- 包含哪些 topic。
- 每个 topic 的消息类型和数量。

回放：

```bash
rosbag play chatter_demo.bag
```

循环回放：

```bash
rosbag play --loop chatter_demo.bag
```

不应一开始就使用：

```bash
rosbag record -a
```

`-a` 会记录所有 topic，初学阶段容易产生巨大文件，也会混入尚未理解的数据。更好的习惯是先用 `rostopic list` 看清系统，再只记录关键 topic。

## 7.16 rosbag 回放时要理解什么

rosbag 回放并不会“复活原来的节点”。它只是按照记录的时间戳重新发布 topic 消息。因此：

- 如果回放 `/chatter`，需要有订阅 `/chatter` 的节点才能看到效果。
- 如果原系统还有 service 调用、参数变化、文件读写，bag 不会自动复现这些行为。
- 如果算法依赖 `/clock` 或仿真时间，需要理解 `use_sim_time` 和 `rosbag play --clock`，下一小节会给出最小说明。
- bag 文件越大，记录和回放对磁盘、CPU、网络的压力越大。

一个简单验证流程：

1. 启动 `roslaunch beginner_tutorials chatter.launch`。
2. 录制 `/chatter`。
3. 停止 launch。
4. 单独启动 `rosrun beginner_tutorials listener.py`。
5. 执行 `rosbag play chatter_demo.bag`。
6. 观察 listener 是否输出记录过的数据。

这个流程用于说明：回放时数据来自 bag，而不是来自原来的 talker。

## 7.17 `roswtf`：第一轮自动诊断

`roswtf` 是 ROS1 提供的自动诊断工具。它会检查环境变量、ROS 图、包路径、消息依赖等常见问题，并给出 warning 或 error。它适合做第一轮检查，但不能替代本书一直强调的分层排障。

基本用法：

```bash
source ~/catkin_ws/devel/setup.bash
roswtf
```

建议在两种情况下运行：

- 刚完成安装或工作空间配置后，检查环境是否明显异常。
- launch 启动后系统行为不符合预期，先让工具扫描一遍常见问题。

阅读输出时要区分：

| 输出类型 | 含义 | 处理方式 |
|---|---|---|
| `ERROR` | 很可能影响系统运行 | 优先处理，并回到对应命令验证 |
| `WARNING` | 可能是问题，也可能是当前实验不需要的配置 | 阅读上下文，不要机械修改 |
| 无明显异常 | 只能说明常见问题未被发现 | 仍需用 `rosnode`、`rostopic`、`rosparam`、日志继续验证 |

例如 `roswtf` 提示找不到某个包时，不应直接重装 ROS，而应先执行：

```bash
rospack find 包名
echo $ROS_PACKAGE_PATH
```

`roswtf` 的价值是把部分低层错误提前暴露出来；真正的判断仍要回到系统状态和可观察证据。

## 7.18 `/clock` 与 `use_sim_time`：回放和仿真时间

真实机器人通常使用系统时间；仿真和 rosbag 回放常常需要使用“仿真时间”。ROS1 中，仿真时间通常通过 `/clock` topic 发布，节点是否使用它由全局参数 `/use_sim_time` 决定。

查看当前设置：

```bash
rosparam get /use_sim_time
rostopic echo /clock
```

典型场景：

| 场景 | 常见设置 | 原因 |
|---|---|---|
| 普通真实机器人实验 | `/use_sim_time` 为 `false` 或不存在 | 节点直接使用系统时间 |
| Gazebo 仿真 | `/use_sim_time` 为 `true`，Gazebo 发布 `/clock` | 节点按仿真世界时间运行 |
| rosbag 回放仿真数据 | `rosparam set /use_sim_time true`，`rosbag play --clock 文件.bag` | 回放时重新发布记录的时间 |

最小回放示例：

```bash
rosparam set /use_sim_time true
rosbag play --clock chatter_demo.bag
```

注意：如果设置了 `/use_sim_time=true`，但系统中没有任何节点发布 `/clock`，依赖 ROS 时间的节点可能表现为等待、时间不前进或定时器不触发。排障时先查：

```bash
rosparam get /use_sim_time
rostopic info /clock
```

这个概念在第 9 章 Gazebo 仿真和第 10 章综合项目中会反复出现。它不改变消息内容，但会影响节点对时间戳、定时器、TF 缓存和 bag 回放的解释。

## 7.19 最小可运行实验

### 实验目标

用一个 launch 文件启动 talker/listener，加载私有参数，录制并回放 `/chatter`。实验结束后，应能解释每个节点、参数、topic 和 bag 文件的作用。

### 前置条件

- 已完成第 6 章 Python talker/listener。
- `talker.py` 已修改为读取 `~rate` 和 `~text_prefix`。
- 当前终端能 `rospack find beginner_tutorials`。

### 操作步骤

准备目录：

```bash
source ~/catkin_ws/devel/setup.bash
roscd beginner_tutorials
mkdir -p launch config
```

创建 `config/talker.yaml`：

```yaml
rate: 2.0
text_prefix: "hello launch"
```

创建 `launch/chatter.launch`：

```xml
<launch>
  <node pkg="beginner_tutorials" type="talker.py" name="talker" output="screen">
    <rosparam command="load" file="$(find beginner_tutorials)/config/talker.yaml" />
  </node>

  <node pkg="beginner_tutorials" type="listener.py" name="listener" output="screen" />
</launch>
```

运行：

```bash
roslaunch beginner_tutorials chatter.launch
```

另开终端观察：

```bash
source ~/catkin_ws/devel/setup.bash
rosnode list
rostopic list
rosparam list
rosparam get /talker/rate
rosparam get /talker/text_prefix
rostopic echo /chatter
rostopic hz /chatter
```

录制：

```bash
mkdir -p ~/bagfiles
cd ~/bagfiles
rosbag record -O chatter_demo /chatter /rosout
```

按 `Ctrl+C` 停止录制，然后查看：

```bash
rosbag info chatter_demo.bag
```

回放验证：

```bash
rosrun beginner_tutorials listener.py
rosbag play chatter_demo.bag
```

实际操作时，`listener.py` 和 `rosbag play` 应在不同终端运行。

### 正确现象

- `roslaunch` 一个命令启动两个节点。
- `/chatter` 有持续字符串数据。
- `/talker/rate` 和 `/talker/text_prefix` 存在。
- `rostopic hz /chatter` 频率接近 2 Hz。
- bag 文件包含 `/chatter` 和 `/rosout`。
- 停掉 talker 后，`rosbag play` 仍能重新发布记录过的 `/chatter` 数据，listener 能收到。

### 实验复盘

| 步骤 | 作用 | 验证命令 |
|---|---|---|
| 创建 launch 文件 | 固化节点启动方式 | `roslaunch beginner_tutorials chatter.launch` |
| 加载 YAML | 把参数写入参数服务器 | `rosparam get /talker/rate` |
| 修改 talker 读取参数 | 使参数实际影响节点行为 | `rostopic hz /chatter` |
| 录制 bag | 保存 topic 数据 | `rosbag info chatter_demo.bag` |
| 回放 bag | 重新发布记录过的消息 | listener 日志、`rostopic echo` |

## 7.20 高频错误与排查

| 现象 | 高概率原因 | 第一检查命令 | 修复思路 |
|---|---|---|---|
| `roslaunch` 找不到文件 | launch 文件不在包内或未 source | `roscd beginner_tutorials`; `ls launch` | 确认路径和 source |
| 节点启动后立即退出 | Python 脚本异常或权限错误 | 看 roslaunch 终端日志 | 加 `chmod +x`，检查 traceback |
| 参数不存在 | YAML 未加载或命名空间写错 | `rosparam list` | 检查 `<rosparam>` 位置、路径和缩进 |
| 改 YAML 后行为没变 | 节点没读取参数或未重启 | `rosparam get /talker/rate` | 修改代码读取参数，重启节点 |
| remap 后 listener 收不到 | 两端 remap 不一致 | `rqt_graph`; `rostopic list` | 保持发布和订阅目标一致 |
| 命名空间下找不到 topic | 观察时使用了错误名称 | `rostopic list` | 使用完整 topic 名 |
| bag 太大 | 录制了所有 topic | `rosbag info` | 初学阶段只录关键 topic |
| 回放没效果 | 没有订阅者或 topic 名不同 | `rostopic list`; `rqt_graph` | 启动订阅节点，确认 topic 名 |
| 设置仿真时间后节点不动 | `/clock` 没有发布 | `rosparam get /use_sim_time`; `rostopic info /clock` | 启动 Gazebo 或用 `rosbag play --clock` |
| 日志看不到 | 未设置 `output="screen"` 或看错日志目录 | `ls ~/.ros/log/latest` | 打开 screen 输出或查看日志文件 |

### 排障顺序

运行管理问题可以按下面顺序检查：

1. `roslaunch` 是否能启动。如果不能，先查包路径、`source`、launch 文件名和 XML 语法。
2. 节点是否存在。启动后用 `rosnode list` 和 roslaunch 终端日志确认节点没有立即退出。
3. 参数是否存在且位于正确命名空间。使用 `rosparam list/get`，同时检查 YAML 缩进和 `<rosparam>` 加载位置。
4. topic 是否连通。使用 `rostopic info`、`rqt_graph` 和 remap 配置确认发布者与订阅者指向同一名称。
5. bag 是否记录到预期数据。使用 `rosbag info` 检查 topic、消息类型、数量和时长。
6. 如果启用了仿真时间，检查 `/use_sim_time` 和 `/clock`，确认 Gazebo 或 `rosbag play --clock` 正在发布时间。

## 7.21 本章自测

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

### 参考答案

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

## 7.22 本章小结

本章把 ROS 程序从“能单独运行”推进到“能组织成系统”。launch、参数、remap、命名空间、日志和 bag 是 ROS 工程化的基础。

一个合格的 ROS 项目，不只是代码能跑，还要能：

- 一键启动。
- 参数可配置。
- topic 可观察。
- 名称可组织。
- 日志可定位。
- 数据可记录。
- 实验可复现。

后续仿真和移动机器人章节会大量使用这些能力。从现在开始应养成习惯：每写一个节点，都思考它怎样被 launch 启动，参数从哪里来，topic 名是否可 remap，关键数据是否能用 rosbag 记录。

## 延伸阅读

- ROS Tutorials 总目录：https://mirror.umd.edu/roswiki/ROS%282f%29Tutorials.html
- roslaunch 文档：https://mirror.umd.edu/roswiki/roslaunch.html
- roslaunch XML 参考：https://mirror.umd.edu/roswiki/roslaunch%282f%29XML.html
- rosparam 文档：https://mirror.umd.edu/roswiki/rosparam.html
- rosbag 文档：https://mirror.umd.edu/roswiki/rosbag.html
- ros_comm 官方仓库：https://github.com/ros/ros_comm
- A Gentle Introduction to ROS：https://jokane.net/agitr/
