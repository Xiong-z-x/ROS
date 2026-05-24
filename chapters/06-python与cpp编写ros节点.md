# 第 6 章 Python 与 C++ 编写 ROS 节点

## 本章解决什么问题

前面已经完成工作空间和功能包的创建。本章开始编写 ROS 节点。节点是 ROS 系统里实际执行计算的进程：发布者产生数据，订阅者消费数据，服务端处理请求，客户端发出请求。

本章采用“同一个通信思想，Python 和 C++ 各实现一遍”的方式。先用 Python 建立通信直觉，再用 C++ 理解编译、链接和类型约束。这样安排不是说 Python 比 C++ 更重要，而是为了避免初学者同时被 ROS 通信、CMake、头文件、链接错误和类型系统淹没。

本章的核心目标不是背 API，而是理解一个 ROS 节点最基本的生命周期：初始化节点、创建通信接口、循环发布或等待回调、输出日志、在 ROS 关闭时退出。还需要学会用 CLI 验证程序是否实际进入 ROS 计算图。

## 学习完成后应达到的能力

- 用 `rospy` 写发布者和订阅者。
- 用 `roscpp` 写发布者和订阅者。
- 用 Python 和 C++ 各写一个最小 service server/client。
- 理解 `init_node`、Publisher、Subscriber、callback、Rate、spin。
- 用 `rosnode`、`rostopic`、`rosservice`、`rosmsg`、`rossrv` 观察自己写的节点和接口。
- 修改 `package.xml` 和 `CMakeLists.txt` 支持 C++ 节点与自定义服务。
- 根据错误信息判断是 Python 权限问题、C++ 编译问题、消息生成问题、topic 名问题还是环境问题。

## 6.1 本章在全书中的位置

第 5 章解决“代码放在哪里、怎样构建”。本章解决“代码怎样成为 ROS 计算图中的节点”。第 7 章会继续把这些节点组织成可复现实验。

应把本章看成 ROS 编程的最低闭环：写代码、编译或授权、运行节点、观察图、定位错误。

## 6.2 必须理解的概念

| 概念 | 简明定义 | 容易误解的点 |
|---|---|---|
| 节点 | 参与 ROS 计算图的进程 | 不是每个 Python/C++ 文件自动就是 ROS 节点 |
| 发布者 Publisher | 向 topic 写消息的对象 | 发布者不直接调用订阅者函数 |
| 订阅者 Subscriber | 从 topic 接收消息并触发回调的对象 | 回调什么时候执行由 ROS 通信和事件循环决定 |
| 回调 callback | 数据到达后被调用的函数 | 回调内不应做长时间阻塞工作 |
| `Rate` | 控制循环频率的工具 | 它不是实时控制保证，只是循环节奏控制 |
| `spin` | 让节点进入回调处理循环 | 没有 `spin`，订阅节点可能启动后立刻退出 |
| Service | 一次请求、一次响应的通信接口 | 不适合高频连续数据流 |
| 消息/服务生成 | 根据 `.msg`、`.srv` 文件生成语言绑定代码 | 修改 `.srv` 后必须重新编译并 source |

## 6.3 Python 和 C++ 怎么选

本书两个都讲。原因不是为了增加负担，而是因为 ROS1 生态中两者都常见。

| 维度 | Python `rospy` | C++ `roscpp` |
|---|---|---|
| 上手速度 | 快，适合初学和原型 | 慢，需要编译和 CMake |
| 性能 | 通常低于 C++ | 更适合高频、低延迟、计算密集任务 |
| 错误类型 | 运行时报错、权限、解释器、缩进 | 编译、链接、头文件、类型不匹配 |
| 常见用途 | 实验脚本、配置节点、数据处理原型 | 控制、驱动、实时性更高的模块 |
| 本章目标 | 建立通信直觉 | 理解工程构建与类型约束 |

初学时不应把“Python 能跑”误解为“ROS 工程只需要 Python”，也不应把“C++ 更快”误解为“所有节点都必须用 C++”。工程选择取决于频率、延迟、硬件接口、团队维护能力和项目规模。

## 6.4 发布订阅模型回顾

发布订阅模型里，发布者不直接调用订阅者函数。发布者只把消息发到某个 topic；订阅者声明自己对某个 topic 感兴趣。ROS Master 负责注册和发现，节点之间建立连接后传输消息。

本章先使用：

- topic：`/chatter`
- message：`std_msgs/String`
- Python 发布者：`talker.py`
- Python 订阅者：`listener.py`
- C++ 发布者：`cpp_talker`
- C++ 订阅者：`cpp_listener`

发布订阅的运行关系可以按五步理解：发布者向 Master 注册 `/chatter` 及其类型，订阅者向 Master 查询并订阅 `/chatter`，Master 返回发布者连接信息，订阅者与发布者建立数据连接，发布者持续发送 `std_msgs/String` 消息，订阅者收到消息后触发回调。

真实机器人里的 `/scan`、`/odom`、`/cmd_vel` 也是同样思想。区别只是消息类型和频率更复杂。

## 6.5 准备包结构

进入包：

```bash
source ~/catkin_ws/devel/setup.bash
roscd beginner_tutorials
mkdir -p scripts src srv
```

如果 `roscd beginner_tutorials` 失败，回到第 5 章检查工作空间和 source：

```bash
rospack find beginner_tutorials
echo $ROS_PACKAGE_PATH
```

## 6.6 Python 发布者

创建文件：

```bash
nano scripts/talker.py
```

写入：

```python
#!/usr/bin/env python3
from typing import NoReturn

import rospy
from std_msgs.msg import String


def main() -> NoReturn:
    rospy.init_node("talker", anonymous=False)
    pub = rospy.Publisher("chatter", String, queue_size=10)
    rate = rospy.Rate(1.0)
    count = 0

    while not rospy.is_shutdown():
        text = f"hello ros {count}"
        msg = String(data=text)
        pub.publish(msg)
        rospy.loginfo("published: %s", msg.data)
        count += 1
        rate.sleep()

    raise SystemExit


if __name__ == "__main__":
    main()
```

添加执行权限：

```bash
chmod +x scripts/talker.py
```

逐行理解：

| 代码 | 作用 |
|---|---|
| `#!/usr/bin/env python3` | 让系统用 Python 3 运行脚本 |
| `rospy.init_node("talker")` | 把当前进程初始化为 ROS 节点 |
| `rospy.Publisher("chatter", String, queue_size=10)` | 创建向 `chatter` 发布 `String` 消息的发布者 |
| `rospy.Rate(1.0)` | 设置循环目标频率为 1 Hz |
| `while not rospy.is_shutdown()` | ROS 未要求关闭时持续运行 |
| `String(data=text)` | 构造标准字符串消息 |
| `pub.publish(msg)` | 发布消息 |
| `rospy.loginfo(...)` | 写 ROS 日志，进入终端和 `/rosout` |

`queue_size=10` 表示发送队列长度。初学阶段可以先理解为“订阅者或网络短时间跟不上时，发布端最多缓存多少条待发送消息”。队列太小可能丢旧消息，队列太大可能让延迟积累。真实控制系统通常宁可丢旧数据，也不希望处理很久以前的数据。

## 6.7 Python 订阅者

创建文件：

```bash
nano scripts/listener.py
```

写入：

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import String


def callback(msg: String) -> None:
    rospy.loginfo("I heard: %s", msg.data)


def main() -> None:
    rospy.init_node("listener", anonymous=False)
    rospy.Subscriber("chatter", String, callback)
    rospy.spin()


if __name__ == "__main__":
    main()
```

添加执行权限：

```bash
chmod +x scripts/listener.py
```

解释：

- `callback` 是收到消息后自动调用的函数。
- `rospy.Subscriber("chatter", String, callback)` 表示订阅 `chatter`，消息类型必须是 `std_msgs/String`。
- `rospy.spin()` 让节点保持运行，等待回调。如果没有它，脚本可能创建订阅者后直接结束。

订阅者本身没有显式循环。它依赖 ROS 的回调机制：数据到达时，`callback` 被调用。

## 6.8 运行 Python 节点

终端 1：

```bash
roscore
```

终端 2：

```bash
source ~/catkin_ws/devel/setup.bash
rosrun beginner_tutorials talker.py
```

终端 3：

```bash
source ~/catkin_ws/devel/setup.bash
rosrun beginner_tutorials listener.py
```

终端 4：

```bash
source ~/catkin_ws/devel/setup.bash
rosnode list
rostopic list
rostopic info /chatter
rostopic echo /chatter
rqt_graph
```

正确现象：

- `talker.py` 每秒打印一条 `published: hello ros N`。
- `listener.py` 打印 `I heard: hello ros N`。
- `rostopic echo /chatter` 能看到 `data: "hello ros N"`。
- `rostopic info /chatter` 显示一个 publisher 和至少一个 subscriber。
- `rqt_graph` 显示 `/talker` 通过 `/chatter` 连接 `/listener`。

如果 `listener.py` 没有输出，暂不应改代码，先看图和 topic：

```bash
rostopic info /chatter
rqt_graph
```

这能区分“发布者根本没发布”“订阅者没连上”“topic 名不一致”“消息类型不一致”等不同问题。

## 6.9 C++ 发布者

创建文件：

```bash
nano src/talker.cpp
```

写入：

```cpp
#include "ros/ros.h"
#include "std_msgs/String.h"

#include <sstream>

int main(int argc, char** argv) {
  ros::init(argc, argv, "cpp_talker");
  ros::NodeHandle nh;

  ros::Publisher pub = nh.advertise<std_msgs::String>("chatter_cpp", 10);
  ros::Rate rate(1.0);

  int count = 0;
  while (ros::ok()) {
    std_msgs::String msg;
    std::stringstream ss;
    ss << "hello roscpp " << count;
    msg.data = ss.str();

    pub.publish(msg);
    ROS_INFO("%s", msg.data.c_str());

    ros::spinOnce();
    rate.sleep();
    ++count;
  }

  return 0;
}
```

关键解释：

- `ros::init` 初始化 ROS 节点。
- `ros::NodeHandle nh` 是访问 ROS 通信接口的句柄。
- `nh.advertise<std_msgs::String>("chatter_cpp", 10)` 创建发布者。
- `ros::ok()` 类似 Python 中的 `not rospy.is_shutdown()`。
- `ros::spinOnce()` 处理一次回调。这个发布者暂时没有订阅回调，写上它是为了便于熟悉常见循环结构。
- `ROS_INFO` 是 C++ 里的 ROS 日志宏。

## 6.10 C++ 订阅者

创建文件：

```bash
nano src/listener.cpp
```

写入：

```cpp
#include "ros/ros.h"
#include "std_msgs/String.h"

void chatterCallback(const std_msgs::String::ConstPtr& msg) {
  ROS_INFO("I heard: %s", msg->data.c_str());
}

int main(int argc, char** argv) {
  ros::init(argc, argv, "cpp_listener");
  ros::NodeHandle nh;

  ros::Subscriber sub = nh.subscribe("chatter_cpp", 10, chatterCallback);
  ros::spin();

  return 0;
}
```

解释：

- `ConstPtr&` 表示回调收到的是消息智能指针的常量引用，避免复制较大的消息。
- `nh.subscribe("chatter_cpp", 10, chatterCallback)` 表示订阅 `chatter_cpp`。
- `ros::spin()` 进入回调处理循环。

Python 版本和 C++ 版本通信结构相同，但 C++ 多了编译、链接和头文件约束。写 C++ 节点时，代码正确只是第一步，CMake 规则也必须正确。

## 6.11 修改 `CMakeLists.txt`

打开：

```bash
roscd beginner_tutorials
nano CMakeLists.txt
```

确认 `find_package` 至少包含：

```cmake
find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
)
```

在 `include_directories(...)` 后面或文件中合适位置添加：

```cmake
add_executable(cpp_talker src/talker.cpp)
target_link_libraries(cpp_talker ${catkin_LIBRARIES})

add_executable(cpp_listener src/listener.cpp)
target_link_libraries(cpp_listener ${catkin_LIBRARIES})
```

回到工作空间根目录编译：

```bash
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

运行：

```bash
rosrun beginner_tutorials cpp_talker
rosrun beginner_tutorials cpp_listener
```

注意：C++ 节点的可执行名是 `add_executable` 中写的名字，不一定和源文件名完全相同。`rosrun beginner_tutorials cpp_talker` 找的是编译出的可执行文件，不是 `talker.cpp` 文件。

## 6.12 发布订阅实验复盘

| 观察命令 | 应能看到什么 | 说明什么 |
|---|---|---|
| `rosnode list` | `/talker`、`/listener` 或 `/cpp_talker`、`/cpp_listener` | 节点已加入计算图 |
| `rostopic list` | `/chatter` 或 `/chatter_cpp` | topic 已注册 |
| `rostopic info /chatter` | publishers/subscribers 列表 | 连接关系是否建立 |
| `rostopic echo /chatter` | `data: ...` | 消息正在流动 |
| `rostopic type /chatter` | `std_msgs/String` | topic 消息类型 |
| `rosmsg show std_msgs/String` | `string data` | 消息字段结构 |
| `rqt_graph` | 节点通过 topic 相连 | 计算图结构正确 |

如果只看终端打印，容易误判。例如发布者在打印日志，不代表订阅者已经收到；订阅者没输出，也不一定是代码错，可能是 topic 名或类型不一致。CLI 观察是 ROS 编程的一部分。

## 6.13 Service 最小概念

topic 适合持续流动的数据，例如速度、雷达、图像、里程计。Service 适合一次请求、一次响应，例如“两个数相加”“重置仿真”“保存地图”“查询当前状态”。

本章使用最小加法服务：

- service 名：`add_two_ints`
- 请求：`a`、`b`
- 响应：`sum`

服务调用的运行关系可以按五步理解：服务端向 Master 注册 `add_two_ints`，客户端向 Master 查询该服务，Master 返回服务端连接信息，客户端向服务端发送请求 `a=3, b=5`，服务端回传响应 `sum=8`。

Service 的关键特点是客户端会等待服务端响应。它不适合高频传感器数据，也不适合需要持续反馈和取消的长任务。长任务后续应学习 action。

## 6.14 创建自定义 service

创建 srv 文件：

```bash
roscd beginner_tutorials
mkdir -p srv
nano srv/AddTwoInts.srv
```

写入：

```text
int64 a
int64 b
---
int64 sum
```

`---` 上面是请求，下面是响应。

现在需要修改 `package.xml`。确保有：

```xml
<build_depend>message_generation</build_depend>
<exec_depend>message_runtime</exec_depend>
```

如果 `package.xml` 中已经有 `roscpp`、`rospy`、`std_msgs`，保留它们。

再修改 `CMakeLists.txt`。把 `find_package` 改成包含 `message_generation`：

```cmake
find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  message_generation
)
```

在 `catkin_package()` 之前添加：

```cmake
add_service_files(
  FILES
  AddTwoInts.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
)
```

把 `catkin_package()` 改成：

```cmake
catkin_package(
  CATKIN_DEPENDS roscpp rospy std_msgs message_runtime
)
```

重新编译：

```bash
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

验证服务类型已经生成：

```bash
rossrv show beginner_tutorials/AddTwoInts
```

正确输出：

```text
int64 a
int64 b
---
int64 sum
```

如果 `rossrv show` 找不到类型，优先检查：

```bash
ls ~/catkin_ws/src/beginner_tutorials/srv
grep -n "message_generation" ~/catkin_ws/src/beginner_tutorials/package.xml
grep -n "add_service_files" ~/catkin_ws/src/beginner_tutorials/CMakeLists.txt
```

## 6.15 Python service server

创建文件：

```bash
nano scripts/add_two_ints_server.py
```

写入：

```python
#!/usr/bin/env python3
import rospy
from beginner_tutorials.srv import (
    AddTwoInts,
    AddTwoIntsRequest,
    AddTwoIntsResponse,
)


def handle_add_two_ints(req: AddTwoIntsRequest) -> AddTwoIntsResponse:
    result = req.a + req.b
    rospy.loginfo("request: %d + %d = %d", req.a, req.b, result)
    return AddTwoIntsResponse(sum=result)


def main() -> None:
    rospy.init_node("add_two_ints_server")
    service = rospy.Service("add_two_ints", AddTwoInts, handle_add_two_ints)
    rospy.loginfo("ready to add two ints: %s", service.resolved_name)
    rospy.spin()


if __name__ == "__main__":
    main()
```

添加执行权限：

```bash
chmod +x scripts/add_two_ints_server.py
```

运行：

```bash
rosrun beginner_tutorials add_two_ints_server.py
```

另开终端观察：

```bash
source ~/catkin_ws/devel/setup.bash
rosservice list
rosservice type /add_two_ints
rossrv show beginner_tutorials/AddTwoInts
rosservice call /add_two_ints 3 5
```

正确响应：

```text
sum: 8
```

## 6.16 Python service client

创建文件：

```bash
nano scripts/add_two_ints_client.py
```

写入：

```python
#!/usr/bin/env python3
import sys
from typing import Sequence

import rospy
from beginner_tutorials.srv import AddTwoInts


def add_two_ints(a: int, b: int) -> int:
    rospy.wait_for_service("add_two_ints")
    proxy = rospy.ServiceProxy("add_two_ints", AddTwoInts)
    response = proxy(a, b)
    return int(response.sum)


def main(argv: Sequence[str]) -> None:
    if len(argv) != 3:
        raise SystemExit("用法: rosrun beginner_tutorials add_two_ints_client.py A B")

    a = int(argv[1])
    b = int(argv[2])
    rospy.init_node("add_two_ints_client")
    result = add_two_ints(a, b)
    rospy.loginfo("%d + %d = %d", a, b, result)


if __name__ == "__main__":
    main(sys.argv)
```

添加执行权限：

```bash
chmod +x scripts/add_two_ints_client.py
```

运行前确保服务端已经启动，然后执行：

```bash
rosrun beginner_tutorials add_two_ints_client.py 10 32
```

正确现象：

```text
[INFO] ... 10 + 32 = 42
```

`rospy.wait_for_service("add_two_ints")` 重要。没有它时，客户端可能在服务端还没注册完成之前就发起调用，导致偶发失败。真实系统中，等待 topic/service/action 就绪比依赖启动顺序更可靠。

## 6.17 C++ service server

创建文件：

```bash
nano src/add_two_ints_server.cpp
```

写入：

```cpp
#include "ros/ros.h"
#include "beginner_tutorials/AddTwoInts.h"

bool handleAddTwoInts(beginner_tutorials::AddTwoInts::Request& req,
                      beginner_tutorials::AddTwoInts::Response& res) {
  res.sum = req.a + req.b;
  ROS_INFO("request: %ld + %ld = %ld",
           static_cast<long>(req.a),
           static_cast<long>(req.b),
           static_cast<long>(res.sum));
  return true;
}

int main(int argc, char** argv) {
  ros::init(argc, argv, "cpp_add_two_ints_server");
  ros::NodeHandle nh;

  ros::ServiceServer service = nh.advertiseService("cpp_add_two_ints",
                                                   handleAddTwoInts);
  ROS_INFO("ready to add two ints: %s", service.getService().c_str());
  ros::spin();

  return 0;
}
```

创建客户端：

```bash
nano src/add_two_ints_client.cpp
```

写入：

```cpp
#include "ros/ros.h"
#include "beginner_tutorials/AddTwoInts.h"

#include <cstdlib>

int main(int argc, char** argv) {
  ros::init(argc, argv, "cpp_add_two_ints_client");

  if (argc != 3) {
    ROS_ERROR("usage: rosrun beginner_tutorials cpp_add_two_ints_client A B");
    return 1;
  }

  ros::NodeHandle nh;
  ros::ServiceClient client =
      nh.serviceClient<beginner_tutorials::AddTwoInts>("cpp_add_two_ints");

  beginner_tutorials::AddTwoInts srv;
  srv.request.a = std::atoll(argv[1]);
  srv.request.b = std::atoll(argv[2]);

  if (client.call(srv)) {
    ROS_INFO("sum: %ld", static_cast<long>(srv.response.sum));
    return 0;
  }

  ROS_ERROR("failed to call service cpp_add_two_ints");
  return 1;
}
```

修改 `CMakeLists.txt`，在前面的 C++ 可执行文件规则后继续添加：

```cmake
add_executable(cpp_add_two_ints_server src/add_two_ints_server.cpp)
add_dependencies(cpp_add_two_ints_server
  ${${PROJECT_NAME}_EXPORTED_TARGETS}
  ${catkin_EXPORTED_TARGETS}
)
target_link_libraries(cpp_add_two_ints_server ${catkin_LIBRARIES})

add_executable(cpp_add_two_ints_client src/add_two_ints_client.cpp)
add_dependencies(cpp_add_two_ints_client
  ${${PROJECT_NAME}_EXPORTED_TARGETS}
  ${catkin_EXPORTED_TARGETS}
)
target_link_libraries(cpp_add_two_ints_client ${catkin_LIBRARIES})
```

这里的 `add_dependencies` 关键。因为 `beginner_tutorials/AddTwoInts.h` 是根据 `.srv` 生成的头文件，C++ 节点必须等服务头文件生成后再编译。

编译：

```bash
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

运行服务端：

```bash
rosrun beginner_tutorials cpp_add_two_ints_server
```

另开终端运行客户端：

```bash
source ~/catkin_ws/devel/setup.bash
rosrun beginner_tutorials cpp_add_two_ints_client 7 8
```

正确现象：

```text
[ INFO] ... sum: 15
```

## 6.18 Service 实验复盘

| 操作内容 | 系统发生了什么 | 验证方式 |
|---|---|---|
| 创建 `srv/AddTwoInts.srv` | 定义请求和响应结构 | `cat srv/AddTwoInts.srv` |
| 修改 `package.xml` | 声明消息生成和运行依赖 | `grep message package.xml` |
| 修改 `CMakeLists.txt` | 注册 srv 生成规则 | `grep add_service_files CMakeLists.txt` |
| `catkin_make` | 生成 Python/C++ service 代码 | `rossrv show beginner_tutorials/AddTwoInts` |
| 启动 server | 注册 `/add_two_ints` 服务 | `rosservice list` |
| 调用 client | 发送请求并接收响应 | 客户端日志或 `rosservice call` |

Service 的错误通常分成三类，必须分清楚：

1. **类型没有生成**：`.srv` 文件存在，但 `rossrv show beginner_tutorials/AddTwoInts` 失败。这说明问题在构建规则、依赖声明或没有重新 `catkin_make`，还没有进入运行阶段。
2. **服务没有注册**：`rossrv show` 成功，但 `rosservice list` 看不到 `/add_two_ints`。这说明类型已经生成，问题在 server 节点没有启动、启动后崩溃、服务名写错或没有连接到同一个 Master。
3. **调用参数或逻辑错误**：`rosservice list` 能看到服务，但 `rosservice call /add_two_ints "a: 1 b: 2"` 报类型或字段错误，或者返回值不符合预期。这时才检查请求字段、client 传参、server 回调逻辑。

这三类错误的检查命令不同。不应在类型未生成时反复启动 server，也不应在服务未注册时修改 `.srv` 文件。正确顺序是：

```text
rossrv show 包/服务类型 -> rosservice list -> rosservice type 服务名 -> rosservice call 服务名 参数
```

发布订阅也有类似层次：先用 `rostopic type` 确认类型，再用 `rostopic info` 确认发布者和订阅者，最后用 `rostopic echo/hz` 判断数据是否真的流动。这样写节点时，错误会被限定在“构建、注册、类型、数据、逻辑”中的某一层。

## 6.19 最小可运行实验

### 实验目标

完成 Python 和 C++ 两组发布订阅节点，再完成 Python 和 C++ 两组加法服务。所有节点都能用 CLI 观察。

### 前置条件

- 已完成第 5 章工作空间和 `beginner_tutorials` 包。
- 当前终端能 `rospack find beginner_tutorials`。
- 已安装 `std_msgs`、`rospy`、`roscpp`，Noetic apt 安装主线默认具备。

### 操作步骤

准备目录：

```bash
source ~/catkin_ws/devel/setup.bash
roscd beginner_tutorials
mkdir -p scripts src srv
```

写入：

- `scripts/talker.py`
- `scripts/listener.py`
- `src/talker.cpp`
- `src/listener.cpp`
- `srv/AddTwoInts.srv`
- `scripts/add_two_ints_server.py`
- `scripts/add_two_ints_client.py`
- `src/add_two_ints_server.cpp`
- `src/add_two_ints_client.cpp`

按上文修改 `package.xml` 和 `CMakeLists.txt`。

授权 Python 脚本：

```bash
chmod +x scripts/*.py
```

编译：

```bash
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

运行发布订阅：

```bash
roscore
rosrun beginner_tutorials talker.py
rosrun beginner_tutorials listener.py
rosrun beginner_tutorials cpp_talker
rosrun beginner_tutorials cpp_listener
```

运行服务：

```bash
rosrun beginner_tutorials add_two_ints_server.py
rosrun beginner_tutorials add_two_ints_client.py 10 32
rosrun beginner_tutorials cpp_add_two_ints_server
rosrun beginner_tutorials cpp_add_two_ints_client 7 8
```

观察：

```bash
rosnode list
rostopic list
rostopic info /chatter
rostopic info /chatter_cpp
rosservice list
rosservice type /add_two_ints
rossrv show beginner_tutorials/AddTwoInts
rqt_graph
```

### 正确现象

- Python talker/listener 通过 `/chatter` 通信。
- C++ talker/listener 通过 `/chatter_cpp` 通信。
- `rqt_graph` 能显示两组独立通信链路。
- `rosservice call /add_two_ints 3 5` 返回 `sum: 8`。
- C++ 客户端调用 `cpp_add_two_ints` 返回正确求和结果。

## 6.20 高频错误与排查

| 现象 | 高概率原因 | 第一检查命令 | 修复思路 |
|---|---|---|---|
| `Permission denied` 运行 Python | 脚本没有执行权限 | `ls -l scripts/talker.py` | `chmod +x scripts/*.py` |
| `bad interpreter` | shebang 写错或 Windows 换行 | `head -1 scripts/talker.py` | 使用 `#!/usr/bin/env python3`，必要时转换换行 |
| `rosrun` 找不到 Python 脚本 | 未 source 工作空间或脚本不在包内 | `rospack find beginner_tutorials` | source `devel/setup.bash`，确认脚本路径 |
| C++ 编译没生成节点 | 未加 `add_executable` | `grep add_executable CMakeLists.txt` | 添加 CMake 规则 |
| C++ 链接失败 | 未链接 `${catkin_LIBRARIES}` | 看 `catkin_make` 错误 | 添加 `target_link_libraries` |
| 找不到 `AddTwoInts.h` | srv 生成顺序或 CMake 依赖错误 | `grep add_dependencies CMakeLists.txt` | 添加 `add_dependencies` 后重编译 |
| Python 无法导入 `beginner_tutorials.srv` | 没编译或没 source | `rossrv show beginner_tutorials/AddTwoInts` | `catkin_make` 后重新 source |
| listener 没收到消息 | topic 名不一致 | `rostopic list`; `rqt_graph` | 确认发布和订阅 topic 相同 |
| `rostopic echo` 没输出 | 发布者没运行或消息频率太低 | `rostopic info /chatter` | 启动发布者，检查 publishers |
| service call 长时间无响应 | server 未启动或服务名不一致 | `rosservice list` | 启动 server，确认服务名 |

### 排障顺序

自写节点运行失败时，按下面顺序检查：

1. `roscore` 是否运行，当前终端是否能连接 Master。
2. 功能包是否可见：`rospack find beginner_tutorials`，必要时重新 `source ~/catkin_ws/devel/setup.bash`。
3. 如果是 Python 节点，检查 shebang、执行权限、导入错误和终端 traceback。
4. 如果是 C++ 节点，检查 `catkin_make` 输出、`CMakeLists.txt`、链接库和生成的服务头文件。
5. 节点是否进入计算图：`rosnode list` 和节点终端日志。
6. Topic 或 service 是否存在、类型是否正确、是否真的有数据或响应：分别用 `rostopic info/type/echo` 和 `rosservice list/type/call` 检查。

## 6.21 本章自测

1. Python 版本和 C++ 版本的发布订阅通信结构是否相同？不同点在哪里？
2. 为什么 Python 脚本需要执行权限？
3. 为什么 C++ 节点需要修改 `CMakeLists.txt`？
4. `rospy.spin()` 和循环发布中的 `rate.sleep()` 分别解决什么问题？
5. `ros::spin()` 和 `ros::spinOnce()` 有什么区别？
6. `queue_size` 太小或太大可能有什么影响？
7. Topic 名相同但消息类型不同会发生什么？
8. Service 和 topic 的本质差异是什么？
9. 修改 `.srv` 文件后为什么必须重新 `catkin_make` 并重新 source？
10. 如果客户端调用 service 后长时间无响应，应先检查哪些命令？
11. 为什么 C++ service 节点需要 `add_dependencies`？
12. 如何判断一个节点没有收到数据是发布者问题还是订阅者问题？

### 参考答案

1. 通信结构相同，都是节点通过 topic 发布和订阅消息：发布者向 topic 写数据，订阅者从 topic 收数据并触发回调。不同点在于 Python 节点由解释器运行，主要关注脚本权限、导入和运行时错误；C++ 节点需要先编译链接，主要关注 `CMakeLists.txt`、头文件、类型和链接错误。

2. `rosrun` 运行 Python 脚本时，本质上要把脚本当作可执行文件启动。没有执行权限时，Linux 会拒绝执行，即使脚本内容正确也会报 `Permission denied`。通常用 `chmod +x scripts/*.py` 解决，同时确保第一行 shebang 是 `#!/usr/bin/env python3`。

3. C++ 源文件不会被 catkin 自动猜测并编译。必须在 `CMakeLists.txt` 中写 `add_executable` 告诉 CMake 要生成哪个可执行文件，再用 `target_link_libraries` 链接 ROS 库。否则 `catkin_make` 可能成功结束，但不会生成预期的 C++ 节点。

4. `rospy.spin()` 让订阅节点保持运行并处理回调，否则程序可能创建订阅者后直接退出。`rate.sleep()` 用在循环发布中，用于按指定频率休眠，控制发布节奏。一个解决“等待回调”，一个解决“循环频率”。

5. `ros::spin()` 会进入持续回调处理循环，通常用于纯订阅者或 service server；`ros::spinOnce()` 只处理一次回调，常用于自己写 `while (ros::ok())` 循环的节点。发布者如果还需要处理订阅回调，通常在循环中调用 `spinOnce()` 再 `rate.sleep()`。

6. `queue_size` 太小，在订阅者或网络短时间跟不上时容易丢弃消息；太大则可能积累旧消息，导致延迟变高。对控制类数据，处理很久以前的速度命令通常没有意义，因此队列不宜过大。选择队列长度要结合消息频率、实时性和是否允许丢旧数据。

7. ROS 要求同一个 topic 上发布者和订阅者的消息类型一致。如果 topic 名相同但类型不同，连接通常无法正常建立，工具会显示类型不匹配或订阅者收不到数据。排查时要同时用 `rostopic type 话题名` 和代码中的消息类型核对。

8. Topic 是持续、异步的数据流，适合传感器、状态、速度命令等；Service 是一次请求、一次响应，适合查询、重置、计算等离散操作。Topic 不要求接收方立即回应，service 客户端通常会等待服务端响应。选错通信方式会让系统语义不清，例如用 service 传激光数据就不合适。

9. `.srv` 文件只是接口定义，必须经过 catkin 的消息生成流程，才能生成 Python 可导入模块和 C++ 头文件。修改后如果不重新 `catkin_make`，代码仍看不到新生成类型；不重新 source，当前终端也可能找不到生成结果。因此改 `.srv` 后要编译并重新加载工作空间环境。

10. 先查 `rosservice list` 看服务是否注册；再查 `rosservice type /服务名` 和 `rossrv show 类型` 看类型是否正确；用 `rosnode list` 看 server 节点是否运行；必要时查看 server 终端日志。如果服务不存在，客户端通常是在等待服务；如果服务存在但调用失败，要检查请求参数和服务端异常。

11. `AddTwoInts.h` 这类 C++ 头文件是由 `.srv` 生成的，不是源码目录中一开始就存在的文件。`add_dependencies` 告诉 CMake：编译 service 节点前，必须先完成消息/服务代码生成。否则可能出现偶发的“找不到生成头文件”或并行构建顺序错误。

12. 先用 `rostopic info 话题名` 看 publisher 和 subscriber 是否都存在。如果没有 publisher，是发布者没启动或 topic 名错；如果没有 subscriber，是订阅者没启动或订阅名错；如果两者都有，再用 `rostopic echo`、`rostopic type`、`rqt_graph` 和节点日志检查数据是否发布、类型是否一致、回调是否处理。

## 6.22 本章小结

本章完成了第一个自写 ROS 节点闭环。读者现在应理解：ROS 节点不是孤立程序，而是计算图中的参与者。写节点时要同时考虑代码、包结构、构建规则、运行环境和观察工具。

后续写更复杂的机器人程序时，调试顺序仍然不变：

1. 当前终端环境是否正确？
2. 节点是否启动？
3. topic 或 service 是否存在？
4. 消息或服务类型是否正确？
5. 是否有 publisher/subscriber 或 server/client？
6. 数据是否真的在流动？
7. 代码逻辑是否处理了数据？

本章代码很小，但工程结构已经完整：Python、C++、topic、service、CMake、package.xml、CLI 观察都出现了。第 7 章会把这些节点用 launch、参数、日志和 bag 管理起来。

## 延伸阅读

- ROS Tutorials 总目录：https://mirror.umd.edu/roswiki/ROS%282f%29Tutorials.html
- rospy 文档：https://mirror.umd.edu/roswiki/rospy.html
- rospy API：https://docs.ros.org/en/noetic/api/rospy/html/
- roscpp 文档：https://mirror.umd.edu/roswiki/roscpp.html
- roscpp API：https://docs.ros.org/en/noetic/api/roscpp/html/
- std_msgs/String 消息定义：https://docs.ros.org/en/noetic/api/std_msgs/html/msg/String.html
- A Gentle Introduction to ROS：https://jokane.net/agitr/
