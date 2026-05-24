# 第 4 章 第一个 ROS 系统：自测题与参考答案

## 自测题

1. 为什么 turtlesim 适合作为第一个 ROS 系统？
2. `/turtle1/cmd_vel` 和 `/turtle1/pose` 分别代表命令还是反馈？
3. `rostopic type` 和 `rosmsg show` 的区别是什么？
4. `rostopic pub -1` 和 `rostopic pub -r 10` 的区别是什么？
5. 如果 `rqt_graph` 看不到 teleop 和 turtlesim 的连接，应先检查哪些命令？
6. 为什么 teleop 节点不需要知道 turtlesim 内部代码？
7. `rosnode info` 中 Publications 和 Subscriptions 分别代表什么？
8. 如果 `rostopic echo /turtle1/cmd_vel` 有数据但模拟海龟不动，可能是什么原因？
9. 为什么 `rostopic info` 有时比 `rostopic echo` 更适合作为第一步排查？
10. turtlesim 中学到的观察方法如何迁移到移动机器人？

## 参考答案

1. turtlesim 足够小，启动快、依赖少、现象直观，同时包含节点、topic、message、service、参数和 rqt_graph 等 ROS 核心观察对象。它把真实机器人中的“控制输入”和“状态反馈”简化成模拟海龟运动，适合初学者先理解 ROS 计算图，而不是一开始面对复杂硬件和仿真。

2. `/turtle1/cmd_vel` 是命令输入，通常由 teleop 或手动 `rostopic pub` 发布，表示模拟海龟的期望速度；`/turtle1/pose` 是状态反馈，由 turtlesim 节点发布，描述当前位姿和速度信息。真实移动机器人中，类似关系是 `/cmd_vel` 作为控制输入，`/odom` 作为运动反馈。

3. `rostopic type /turtle1/cmd_vel` 只显示 topic 使用的消息类型，例如 `geometry_msgs/Twist`；`rosmsg show geometry_msgs/Twist` 会展开这个类型的字段结构，例如 `linear.x`、`angular.z`。前者解决“这条 topic 是什么类型”，后者解决“这个类型里有哪些字段”。

4. `rostopic pub -1` 只发布一次消息，适合测试单次命令是否能被接收；`rostopic pub -r 10` 以 10 Hz 持续发布，适合模拟持续控制输入。速度控制通常需要持续发布，因为很多机器人或仿真系统会在命令停止后逐渐停止或触发安全机制。

5. 先查 `rosnode list` 确认 teleop 和 turtlesim 节点是否存在，再查 `rostopic list` 确认 `/turtle1/cmd_vel` 是否存在，接着用 `rostopic info /turtle1/cmd_vel` 看 publisher 和 subscriber 是否连接。必要时用 `rostopic echo /turtle1/cmd_vel` 判断是否真的有速度数据。

6. teleop 节点只需要知道自己向哪个 topic 发布什么消息类型，不需要知道 turtlesim 内部如何更新画面。ROS 的发布订阅模型通过 topic 和 message 解耦节点实现。真实机器人中，键盘控制节点也不需要知道底盘驱动内部如何控制电机，只需要按约定发布 `/cmd_vel`。

7. Publications 表示该节点发布了哪些 topic，即它向外输出哪些数据；Subscriptions 表示该节点订阅了哪些 topic，即它依赖哪些输入数据。对 turtlesim 来说，它订阅 `/turtle1/cmd_vel` 并发布 `/turtle1/pose`，这能直接说明它的输入和输出边界。

8. 可能原因包括：发布的是零速度、消息字段不符合预期、turtlesim 节点没有订阅同一个 topic、节点长时间无响应或窗口未响应、topic 命名空间不一致。排查顺序应先看 `rostopic info /turtle1/cmd_vel` 是否有 turtlesim 作为 subscriber，再看 echo 出来的速度值是否非零。

9. `rostopic info` 能快速显示 topic 类型、发布者和订阅者，比 `echo` 更适合判断连接关系。`echo` 只能看数据流，如果没有输出，仍无法区分是没有 publisher、没有 subscriber、topic 名错，还是发布频率太低。第一步看 info，可以先确定系统结构。

10. 可以把 `/turtle1/cmd_vel` 对应到移动机器人的 `/cmd_vel`，把 `/turtle1/pose` 对应到 `/odom` 或机器人状态，把 turtlesim 节点对应为底盘或仿真节点。迁移后的观察顺序仍然是：`rosnode list` 看节点，`rostopic list` 看接口，`rostopic info` 看连接，`rostopic echo/hz` 看数据，`rqt_graph` 看整体关系。
