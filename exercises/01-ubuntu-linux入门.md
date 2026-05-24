# 第 1 章 Ubuntu 与 Linux 入门：自测题与参考答案

## 自测题

1. Linux 和 Ubuntu 是什么关系？为什么本书不直接说“安装 Linux”？
2. ROS Noetic 为什么要以 Ubuntu 20.04 作为主线学习环境？
3. `pwd` 的输出为什么会影响后续命令的意义？
4. `>` 和 `>>` 有什么区别？为什么修改 `.bashrc` 时要谨慎？
5. `sudo apt update` 和 `sudo apt install tree` 分别做了什么？
6. 如果 `roscore` 将来提示 `command not found`，应先检查哪三个对象？
7. 为什么不建议在 `~/catkin_ws` 中不加区分地使用 `sudo`？
8. `.bashrc` 修改后，为什么已经打开的终端可能还没有新配置？
9. 原生 Ubuntu、虚拟机、WSL2、Docker 的根本区别是什么？
10. 如果一个教程要求执行 `curl ... | sudo bash`，应先问哪些问题？

## 参考答案

1. Linux 严格来说是内核，Ubuntu 是基于 Linux 内核并集成系统工具、包管理器、桌面环境和软件仓库的完整发行版。本书说“安装 Ubuntu 20.04”，是因为 ROS Noetic 的官方二进制安装、包名、系统依赖和教程都围绕这个发行版版本展开；只说“安装 Linux”会过于模糊，学生可能装到不匹配的发行版或版本。

2. ROS Noetic 的官方目标平台包含 Ubuntu 20.04 Focal，本书选择它可以让 apt 包、Python 3、C++14、ROS Wiki 教程和社区排障经验保持一致。Ubuntu 22.04/24.04 不是 Noetic 的新手主线目标，在非目标平台安装会引入源码构建、依赖版本和兼容性问题，不适合零基础阶段。

3. `pwd` 显示当前工作目录，而很多命令的意义都依赖当前位置。例如在 `~/catkin_ws` 执行 `catkin_make` 和在 `~/catkin_ws/src/beginner_tutorials` 执行 `catkin_make`，结果完全不同；复制、删除、创建文件也都受当前目录影响。排障时先看 `pwd`，可以避免把文件建到错误位置。

4. `>` 会覆盖目标文件，`>>` 会追加到目标文件末尾。修改 `.bashrc` 时要谨慎，是因为它会影响以后每次打开终端的初始化环境；如果用 `>` 误覆盖 `.bashrc`，可能丢失原有配置。如果要追加 ROS 环境，通常使用 `echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc`，并在追加后用 `tail ~/.bashrc` 检查。

5. `sudo apt update` 更新本机的软件包索引，让 apt 知道软件源里有哪些包和版本；它本身通常不安装软件。`sudo apt install tree` 根据当前索引下载并安装 `tree` 包及其依赖。安装 ROS 前必须先确保软件源和索引正确，否则会出现找不到包或安装旧信息的问题。

6. 先查三层：第一，`echo $ROS_DISTRO` 或 `ls /opt/ros/noetic` 判断 ROS 是否安装；第二，`echo $PATH` 和 `which roscore` 判断命令是否在当前 shell 可搜索路径中；第三，`source /opt/ros/noetic/setup.bash` 判断是否只是环境没有加载。如果 source 后可用，说明安装可能正常，问题在当前终端环境。

7. 不建议在 `~/catkin_ws` 中不加区分地使用 `sudo`，因为这可能把工作空间中的文件所有者变成 root，导致普通用户后续无法编辑、编译或删除生成文件。catkin 工作空间通常应由普通用户创建和编译；只有安装系统软件包、改系统目录时才需要 `sudo`。如果权限异常，应先用 `ls -l ~/catkin_ws` 检查所有者。

8. `.bashrc` 是新 Bash 交互 shell 启动时读取的配置文件，已经打开的终端不会自动重新执行它。修改后要么新开终端，要么在当前终端执行 `source ~/.bashrc`。因此“已经写进 `.bashrc`，为什么当前终端还不生效”通常不是配置没写入，而是当前 shell 没重新加载。

9. 原生 Ubuntu 是直接安装在硬盘上的完整系统，性能和硬件访问最好；虚拟机是在现有系统里运行一个完整 Ubuntu，便于快照恢复但图形性能较弱；WSL2 是 Windows 上的 Linux 子系统，适合命令行和轻量实验但 GUI、USB、仿真有额外限制；Docker 是容器化环境，适合复现和隔离，但默认不持久保存工作空间，GUI 和硬件访问需要额外映射。

10. 先问：脚本来自哪里，是否官方或可信？脚本会改哪些文件、安装哪些软件、是否需要 root 权限？是否能先打开脚本内容阅读？失败后如何恢复？有没有更透明的手动安装步骤？`curl ... | sudo bash` 把网络下载内容直接交给 root 执行，风险比普通命令高，不能仅因教程中出现该命令就直接复制执行。
