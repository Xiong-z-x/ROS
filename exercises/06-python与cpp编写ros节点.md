# 第 6 章 Python 与 C++ 编写 ROS 节点：自测题与参考答案

## 自测题

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

## 参考答案

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
