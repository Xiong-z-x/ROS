# 第 1 章 Ubuntu 与 Linux 入门

## 本章解决什么问题

学习 ROS1 的第一个门槛通常不是机器人算法，而是 Linux 环境。很多初学者第一次遇到 ROS 错误时，根本问题并不在 ROS：可能是当前目录错了、没有权限、软件源不可用、包名写错、环境变量没有生效，或者新打开的终端没有重新加载配置。

本章先建立 Ubuntu 与命令行的基本心智模型。读者不需要在这一章成为 Linux 专家，但必须能回答三个问题：当前目录是什么？这个命令会改动什么？命令失败时应先检查哪里？后面安装 ROS、创建 catkin 工作空间、运行节点、排查 `rosrun` 找不到包，都会依赖这些基础。

本书主线使用 **Ubuntu 20.04 Focal Fossa + ROS1 Noetic**。这是 ROS Noetic 的官方目标平台之一；REP-3 明确列出 Noetic 面向 Ubuntu Focal Fossa 20.04，并说明 Noetic 的目标语言环境包括 C++14 与 Python 3.8。不应把本章理解为“Linux 通用入门大全”，它服务于后续 ROS1 学习。

## 学习完成后应达到的能力

- 解释 Linux、Ubuntu、发行版、桌面环境之间的关系。
- 区分原生 Ubuntu、虚拟机、WSL2、Docker 在学习 ROS 时的作用。
- 使用终端完成目录切换、文件创建、文件查看、软件安装和命令定位。
- 理解 `sudo`、普通用户、系统目录、用户目录之间的权限差异。
- 理解 `apt update` 与 `apt install` 的区别。
- 理解环境变量、`PATH`、`~/.bashrc` 和 `source` 的基本作用。
- 遇到命令失败时，能用最少的检查命令定位第一层原因。

## 1.1 Ubuntu、Linux 和 ROS 的关系

### Linux 是内核，不等于 Ubuntu

Linux 严格来说是操作系统内核。内核负责管理硬件、进程、内存、文件系统、网络等底层资源。普通用户平时接触到的“Linux 系统”，通常是一个完整发行版：内核 + 系统工具 + 包管理器 + 桌面环境 + 默认软件。

Ubuntu 是一个 Linux 发行版。可以把 Ubuntu 理解为“把 Linux 内核和大量软件按某种规则打包、测试、发布出来的一整套系统”。ROS Noetic 的官方二进制安装路径主要围绕 Ubuntu 20.04 展开，所以本书先使用 Ubuntu，而不是任意 Linux 发行版。

### ROS 运行在 Ubuntu 之上

ROS 不是替代 Ubuntu 的操作系统。ROS 的节点、话题、服务、参数、launch、bag 等工具都运行在 Linux 进程、文件系统、网络和包管理机制之上。也就是说：

- Ubuntu 提供系统环境。
- Bash 提供命令行交互。
- APT 提供系统软件安装能力。
- ROS 在这些基础上提供机器人软件通信、构建、运行和调试工具。

后面将执行很多类似下面的命令：

```bash
source /opt/ros/noetic/setup.bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
catkin_make
roscore
rosrun turtlesim turtlesim_node
```

如果读者不了解 `source`、`~`、`cd`、当前目录、工作空间这些概念，ROS 命令就会变成不可解释的命令片段。本章的目的就是避免这种情况。

本书上册的基础依赖关系可以用一句话概括：硬件和 Linux 内核支撑 Ubuntu，Ubuntu 提供 Bash、文件系统、APT 和环境变量，ROS Noetic 安装在 Ubuntu 之上，catkin 工作空间再叠加到 ROS 环境之上，最终才运行节点、话题和服务。Ubuntu 不是 ROS 的附属品，而是 ROS 运行、安装、构建和排障的底座。

## 1.2 学习 ROS 时的几种 Ubuntu 环境

本书后续安装章节会详细比较安装方法。这里先建立直觉。

| 环境 | 它是什么 | 适合谁 | 主要优点 | 主要限制 |
|---|---|---|---|---|
| 原生 Ubuntu 20.04 | 直接把 Ubuntu 安装在电脑硬盘上 | 实验室机器、双系统用户 | 性能好，硬件访问直接 | 安装系统有风险，误操作影响真实机器 |
| Ubuntu 20.04 虚拟机 | 在 Windows/macOS/Linux 里运行一个完整 Ubuntu | 零基础学生 | 可快照恢复，失败成本低 | 图形和仿真性能可能较弱 |
| WSL2 Ubuntu | Windows 上的 Linux 子系统 | Windows 学生前期学习 | 启动快，命令行方便 | GUI、USB、Gazebo、网络行为需要额外注意 |
| Docker ROS 镜像 | 容器化运行 ROS 环境 | 课堂批量复现、助教备用环境 | 环境一致，容易清理 | GUI、数据持久化、硬件映射需要额外配置 |

本书主线建议：**第一次学习优先使用 Ubuntu 20.04 虚拟机或原生 Ubuntu 20.04**。WSL2 和 Docker 都值得学，但它们引入了额外抽象。对完全零基础学生，先在一个完整 Ubuntu 系统里理解目录、权限、APT 和终端更稳。

注意：不应把“能打开一个 Linux 终端”等同于“所有 ROS 实验都能稳定运行”。例如 WSL2 官方支持 Linux GUI 应用，但 Gazebo 这类图形和仿真负载仍可能受到显卡、显示服务和设备映射影响。

## 1.3 终端、Shell 和命令行

### 终端是什么

终端是用户与 shell 交互的窗口。Ubuntu 官方命令行入门文档把“command line”解释为在终端中输入命令的一行；shell 则负责解释这些命令。输入命令后，命令可能输出很多文字，也可能什么都不输出就返回提示符。没有输出不一定代表失败，很多命令成功时本来就很安静。

### Shell 是什么

Shell 是命令解释器。本书默认使用 Bash。Bash 会读取用户输入的命令，展开变量，寻找可执行程序，然后启动进程。

查看当前 shell：

```bash
echo $SHELL
```

常见输出：

```text
/bin/bash
```

如果使用 Zsh、Fish 或其他 shell，很多命令仍然相似，但 `~/.bashrc`、变量写法、自动补全和 source 行为可能不同。本书默认不处理这些差异。

### 命令大小写敏感

Linux 命令和文件名通常区分大小写。`pwd` 和 `PWD` 不是一回事，`README.md` 和 `readme.md` 也不是一回事。复制命令时要特别注意大小写、空格和英文标点。

## 1.4 目录：当前所在位置

终端始终有一个“当前工作目录”。大多数相对路径操作都以这个目录为起点。Ubuntu 官方命令行教程也强调，`pwd` 的作用就是打印当前工作目录；在不确定当前位置时先执行 `pwd` 是安全习惯。

### 常用目录

| 路径 | 含义 | ROS 学习中的意义 |
|---|---|---|
| `/` | 根目录，整个文件系统起点 | 不应随意修改 |
| `/home/用户名` | 当前用户主目录 | 个人工作空间通常放这里 |
| `~` | 当前用户主目录的简写 | `~/catkin_ws` 较常见 |
| `/opt/ros/noetic` | ROS Noetic 默认安装位置 | 后续 source ROS 环境 |
| `/etc` | 系统配置目录 | 软件源、网络、服务配置常见位置 |
| `/usr/bin` | 系统命令常见位置 | `which` 常会指向这里 |
| `/tmp` | 临时目录 | 重启或清理后可能消失 |

### 观察当前目录

```bash
pwd
```

刚打开终端时，通常会看到：

```text
/home/用户名
```

### 切换目录

```bash
cd ~
pwd

cd /
pwd

cd -
pwd
```

解释：

- `cd ~`：进入当前用户主目录。
- `cd /`：进入根目录。
- `cd -`：回到上一次所在目录。

### 查看目录内容

```bash
ls
ls -l
ls -la
```

解释：

- `ls`：列出当前目录可见文件。
- `ls -l`：显示权限、所有者、大小、时间等详细信息。
- `ls -la`：连隐藏文件也显示出来。Linux 下以 `.` 开头的文件或目录默认隐藏，例如 `.bashrc`。

ROS 学习中经常要检查隐藏文件，因为环境配置通常写入 `~/.bashrc`。

## 1.5 文件和目录操作

### 创建实验目录

本章所有实验都放在用户主目录下，避免误改系统目录。

```bash
mkdir -p ~/ros_textbook_lab/ch01
cd ~/ros_textbook_lab/ch01
pwd
```

解释：

- `mkdir` 创建目录。
- `-p` 表示父目录不存在时一起创建；如果目录已存在，不报错。
- `~/ros_textbook_lab/ch01` 是本章实验目录。

正确现象：

```text
/home/用户名/ros_textbook_lab/ch01
```

### 创建和查看文件

```bash
echo "hello ubuntu" > note.txt
cat note.txt
```

解释：

- `echo` 输出一段文本。
- `>` 把输出重定向到文件。如果文件已存在，会覆盖原内容。
- `cat` 把文件内容打印到终端。

正确现象：

```text
hello ubuntu
```

追加内容：

```bash
echo "this is chapter 1" >> note.txt
cat note.txt
```

区别：

- `>` 覆盖文件。
- `>>` 追加到文件末尾。

这对 ROS 学习十分重要。写 `~/.bashrc` 时，如果误用 `>`，可能把原来的配置全部覆盖；正确做法通常是用文本编辑器打开，或谨慎使用 `>>` 追加一行。

### 复制、移动和删除

```bash
cp note.txt note_backup.txt
mv note_backup.txt note_copy.txt
ls -l
rm note_copy.txt
ls -l
```

解释：

- `cp` 复制。
- `mv` 移动或重命名。
- `rm` 删除文件。

注意：`rm` 删除后通常不会进入回收站。不应在不理解路径时执行 `rm -rf`。本书不会要求使用破坏性命令清理系统。

## 1.6 权限和 sudo

### 普通用户和超级用户

Ubuntu 默认不让普通用户随意修改系统目录。这样做是为了保护系统。比如 `/etc`、`/usr`、`/opt` 下的很多文件需要管理员权限才能修改。

查看当前用户名：

```bash
whoami
```

查看一个文件的权限：

```bash
ls -l note.txt
```

典型输出类似：

```text
-rw-rw-r-- 1 user user 31 May 19 10:00 note.txt
```

粗略理解：

- 第一个字符表示类型：`-` 是普通文件，`d` 是目录。
- 后面九个字符分三组：文件所有者、同组用户、其他用户的读写执行权限。
- `r` 是读，`w` 是写，`x` 是执行。

### sudo 的含义

`sudo` 表示以管理员权限运行后面的一个命令。Ubuntu 官方命令行教程提醒：使用 `sudo` 前要理解命令在做什么，因为它让该命令拥有超级用户级别的能力。

例子：

```bash
sudo apt update
```

这不是“让命令更强”的机制，而是因为更新系统软件包索引需要访问系统级包管理数据库。

错误用法：

```bash
sudo cd /opt
```

这通常没有意义。`cd` 是 shell 内建命令，不是独立程序；即使某些 shell 接受这种写法，它也不会按预期方式改变当前终端目录。

ROS 学习中的原则：

- 安装系统包时通常需要 `sudo apt install ...`。
- 在自己的工作空间 `~/catkin_ws` 下写代码、编译，不应该依赖 `sudo`。
- 如果在 `~/catkin_ws` 中必须用 `sudo` 才能修改文件，通常说明权限已经被此前的错误命令污染。

检查文件所有者：

```bash
ls -l ~/catkin_ws 2>/dev/null
```

如果看到大量文件所有者是 `root root`，后续 catkin 编译可能出现权限问题。

## 1.7 APT：Ubuntu 的软件包管理

### apt 解决什么问题

APT 是 Ubuntu/Debian 系统常用的软件包管理工具。Ubuntu 官方文档说明，`apt` 可以安装新软件包、升级已有软件包、更新本地软件包索引。可以把 APT 理解为系统级软件安装和依赖管理工具。

在 ROS 学习中，APT 是关键工具，因为官方二进制安装通常长这样：

```bash
sudo apt install ros-noetic-desktop-full
```

这行命令背后做了几件事：

- 从配置好的软件源中查找 `ros-noetic-desktop-full`。
- 计算它依赖哪些包。
- 下载包文件。
- 安装到系统目录。
- 更新系统包数据库。

### update 和 install 的区别

```bash
sudo apt update
sudo apt install tree
```

解释：

- `sudo apt update`：更新本机“软件包索引”。它不等于升级所有软件，也不等于安装新软件。
- `sudo apt install tree`：根据已有索引安装名为 `tree` 的软件包。

如果刚添加了 ROS 软件源，却没有执行 `sudo apt update`，系统可能还不知道新源里有哪些包，于是报：

```text
Unable to locate package ros-noetic-...
```

这类错误不一定说明包不存在，第一步应检查软件源和索引。

### 安装 tree 和 git

```bash
sudo apt update
sudo apt install -y tree git
```

解释：

- `tree` 用树状结构显示目录，非常适合观察工作空间。
- `git` 用于下载和管理代码仓库，后续会用到。
- `-y` 自动回答 yes。课堂演示可以用，自己操作时建议先不加，观察 apt 准备安装哪些包。

验证：

```bash
which tree
which git
tree ~/ros_textbook_lab
git --version
```

正确现象：

- `which tree` 输出类似 `/usr/bin/tree`。
- `git --version` 输出 Git 版本。
- `tree` 显示本章实验目录结构。

## 1.8 命令从哪里来：PATH 和 which

输入：

```bash
tree
```

shell 需要知道去哪找 `tree` 这个程序。它会按环境变量 `PATH` 中列出的目录逐个查找。

查看 `PATH`：

```bash
echo $PATH
```

典型输出：

```text
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

冒号 `:` 分隔多个目录。

查看命令位置：

```bash
which ls
which tree
which git
```

如果命令找不到：

```bash
which roscore
```

在未安装 ROS 或未 source ROS 环境时，可能没有输出。这不一定是“系统坏了”，只是 shell 当前找不到这个命令。

后面安装 ROS 后，`source /opt/ros/noetic/setup.bash` 会修改当前 shell 的环境，让 ROS 命令和包路径可见。

## 1.9 环境变量和 `.bashrc`

### 环境变量是什么

环境变量是进程启动时携带的一组键值对。程序可以通过环境变量判断当前系统配置。例如：

```bash
echo $HOME
echo $USER
echo $SHELL
echo $PATH
```

常见含义：

| 变量 | 含义 |
|---|---|
| `HOME` | 当前用户主目录 |
| `USER` | 当前用户名 |
| `SHELL` | 当前默认 shell |
| `PATH` | 命令搜索路径 |
| `ROS_DISTRO` | 当前 ROS 发行版，安装并 source ROS 后常见 |
| `ROS_MASTER_URI` | ROS1 Master 地址，后续会学 |

### 临时变量

```bash
export MY_ROS_NOTE="chapter1"
echo $MY_ROS_NOTE
```

这个变量只在当前 shell 及它启动的子进程中有效。关掉终端后，它就消失。

### `.bashrc` 是什么

`~/.bashrc` 是 Bash 在启动交互式 shell 时读取的配置文件。很多 ROS 安装教程会建议追加：

```bash
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
```

这表示：以后每次打开新的 Bash 终端，都自动加载 ROS Noetic 环境。

但要注意两点：

1. `source /opt/ros/noetic/setup.bash` 只影响当前 shell。
2. 写入 `~/.bashrc` 后，新终端才会自动生效；当前终端需要手动 `source ~/.bashrc` 或直接 source 对应文件。

查看 `.bashrc` 末尾：

```bash
tail ~/.bashrc
```

不应在未确认内容的情况下覆盖 `.bashrc`。如果要编辑，建议先备份：

```bash
cp ~/.bashrc ~/.bashrc.backup
```

## 1.10 文本编辑器：先会一种就够

ROS 学习会频繁编辑文件：`package.xml`、`CMakeLists.txt`、`.launch`、`.yaml`、Python 脚本、URDF。学习者至少需要熟练一种文本编辑器。

零基础建议：

- 图形界面：VS Code、gedit。
- 终端界面：nano。

用 nano 编辑文件：

```bash
nano note.txt
```

常用操作：

- 保存：`Ctrl + O`，回车确认。
- 退出：`Ctrl + X`。
- 取消：根据底部提示操作。

用 VS Code 打开当前目录：

```bash
code .
```

如果提示 `code: command not found`，说明 VS Code 命令行入口未安装或未配置。不应在这一章纠结，先用 `nano` 或 `gedit` 完成学习。

## 1.11 Git：为什么 ROS 学习需要它

Git 是版本控制工具。ROS 生态大量代码以 Git 仓库形式发布，例如 `ros_tutorials`、TurtleBot3、很多机器人驱动包。读者不需要一开始掌握复杂分支模型，但要会克隆仓库和查看状态。

配置用户名和邮箱：

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

查看配置：

```bash
git config --global --list
```

克隆一个小仓库的基本形式：

```bash
git clone https://github.com/ros/ros_tutorials.git
```

本章不要求实际克隆 ROS 仓库；这里仅用于说明后续会看到的命令结构。

## 1.12 本章最小可运行实验

### 实验目标

完成一个从目录创建、文件操作、软件安装、命令定位、环境变量观察到清理的闭环。这个实验不是为了展示命令数量，而是为了建立后续 ROS 学习所需的最低操作能力。

### 前置条件

- 已进入 Ubuntu 20.04。
- 使用 Bash。
- 网络可访问 Ubuntu 软件源。
- 当前用户有 sudo 权限。

### 操作步骤

先确认系统和 shell：

```bash
lsb_release -a
echo $SHELL
whoami
pwd
```

创建实验目录：

```bash
mkdir -p ~/ros_textbook_lab/ch01
cd ~/ros_textbook_lab/ch01
pwd
```

创建并查看文件：

```bash
echo "hello ubuntu" > note.txt
echo "this directory is for ROS textbook chapter 1" >> note.txt
cat note.txt
ls -la
```

安装并使用工具：

```bash
sudo apt update
sudo apt install -y tree git
which tree
which git
tree ~/ros_textbook_lab
git --version
```

观察环境变量：

```bash
echo $HOME
echo $USER
echo $SHELL
echo $PATH
```

备份 `.bashrc`：

```bash
cp ~/.bashrc ~/.bashrc.backup
ls -l ~/.bashrc ~/.bashrc.backup
```

清理本章临时文件时，只删除本章实验目录：

```bash
rm -r ~/ros_textbook_lab/ch01
ls ~/ros_textbook_lab
```

若希望保留实验结果，可以不执行清理命令。

### 正确现象

- `lsb_release -a` 显示 Ubuntu 系统信息。若是本书主线环境，应能看到 Ubuntu 20.04 或 Focal。
- `pwd` 在创建目录后显示 `/home/用户名/ros_textbook_lab/ch01`。
- `cat note.txt` 能看到两行文本。
- `which tree` 和 `which git` 能显示可执行程序路径。
- `tree ~/ros_textbook_lab` 能以树状结构显示目录。
- `echo $PATH` 输出多个用冒号分隔的目录。
- `.bashrc.backup` 被成功创建。

### 如果失败，先检查什么

| 失败点 | 第一检查命令 | 判断 |
|---|---|---|
| `sudo apt update` 失败 | `ping -c 3 archive.ubuntu.com` | 判断是否网络或源问题 |
| `apt install tree` 找不到包 | `sudo apt update` | 先更新包索引 |
| `tree` 仍找不到 | `which tree` | 判断是否安装成功 |
| 写文件失败 | `pwd`; `ls -ld .` | 判断当前目录和权限 |
| 删除时报错 | `pwd`; `ls ~/ros_textbook_lab` | 确认只删除实验目录 |

## 1.13 命令与代码解释

### `pwd`

打印当前工作目录。后续 ROS 编译时，如果不确定是否在 `~/catkin_ws`，先执行 `pwd`。

### `mkdir -p`

创建目录。`-p` 让命令在父目录不存在时自动创建父目录。创建 ROS 工作空间时会用：

```bash
mkdir -p ~/catkin_ws/src
```

### `cd`

切换目录。`cd ~/catkin_ws` 表示进入主目录下的 `catkin_ws`。如果目录不存在，会报错。

### `ls -la`

查看目录内容，包括隐藏文件。检查 `.bashrc`、`.git`、隐藏配置时常用。

### `echo`、`>`、`>>`

输出文本并可重定向到文件。`>` 覆盖，`>>` 追加。修改环境配置时要非常谨慎。

### `sudo apt update`

更新本地软件包索引。它不安装新软件，只让本机知道软件源中当前有哪些包和版本。

### `sudo apt install`

安装软件包。安装 ROS、Git、构建工具、驱动依赖时都会用。

### `which`

查看命令对应的可执行文件路径。遇到 `command not found` 或怀疑环境没有生效时，先用 `which`。

### `source`

在当前 shell 中执行一个脚本，并让脚本对当前环境的修改立即生效。后续 ROS 最常见命令之一是：

```bash
source /opt/ros/noetic/setup.bash
```

注意：`source` 当前终端生效，不自动影响已经打开的其他终端。

## 1.14 高频错误与排查

| 现象 | 高概率原因 | 第一检查命令 | 修复思路 |
|---|---|---|---|
| `Permission denied` | 当前用户没有写入目标目录的权限 | `pwd`; `ls -ld .` | 回到 `~` 下操作；不应在系统目录里建学习文件 |
| `Unable to locate package tree` | 包索引未更新或软件源不可用 | `sudo apt update` | 先更新索引；若仍失败，检查网络和软件源 |
| `command not found` | 软件未安装或不在 `PATH` 中 | `which 命令名`; `echo $PATH` | 安装软件，或检查环境变量 |
| `cd: no such file or directory` | 目录不存在或路径写错 | `ls`; `pwd` | 先确认父目录存在，注意大小写 |
| `.bashrc` 修改后没效果 | 当前终端未重新加载 | `tail ~/.bashrc` | 执行 `source ~/.bashrc` 或重开终端 |
| 后续在工作空间编译时权限异常 | 曾用 `sudo` 创建或编译用户文件 | `ls -l ~/catkin_ws` | 修复所有者；以后不应在用户工作空间滥用 `sudo` |
| 复制命令失败 | 中文标点、换行、大小写错误 | 逐字符检查命令 | 使用英文半角符号，先复制一行短命令测试 |

这张表不应当成孤立的“错误答案表”。排障时，应先判断错误属于哪一层：路径、权限、软件包、命令搜索路径，还是 shell 环境。比如 `command not found` 和 `Permission denied` 都表现为“命令不能正常运行”，但前者通常是系统找不到可执行文件，后者通常是文件存在却没有执行权限或当前用户没有访问权限。两类错误的第一检查命令完全不同。

可以把本章的排障顺序压缩成下面四步：

```text
pwd / ls      -> 先确认当前所在目录、文件是否存在
ls -l         -> 再确认文件所有者、当前用户是否具备读写执行权限
which / PATH  -> 再确认命令能不能被 shell 找到
source / env  -> 最后确认环境变量是否在当前终端生效
```

举例：以后如果运行 `rosrun beginner_tutorials talker.py` 失败，不应首先重装 ROS。应先用 `rospack find beginner_tutorials` 检查功能包是否被当前环境识别，再用 `ls -l scripts/talker.py` 检查脚本是否具有执行权限，最后用 `head -1 scripts/talker.py` 检查 shebang 是否正确。这样可以把问题从难以解释的现象转换为几个可验证的系统状态。

## 1.15 本章自测

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

### 参考答案

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

## 1.16 本章小结

本章没有正式进入 ROS，但已经建立了后续学习的底层操作能力。应记住：终端不是神秘工具，而是一个可观察、可推理的系统接口。当前目录决定相对路径，权限决定能否修改文件，APT 决定系统软件安装，环境变量决定命令和程序如何找到依赖。

后续学习 ROS 时，很多错误都可以回到本章方法排查：

- 找不到命令：查 `which` 和 `PATH`。
- 找不到包：查当前目录、工作空间、source。
- 安装失败：查 Ubuntu 版本、软件源、`apt update`。
- 权限失败：查 `pwd`、`ls -l`、是否误用 `sudo`。

掌握这些基础，下一章再看 ROS 的节点、话题、服务和参数时，命令就不再是孤立片段，而是可以解释的系统操作。

## 延伸阅读

- Ubuntu 官方命令行入门：https://documentation.ubuntu.com/desktop/en/latest/tutorial/the-linux-command-line-for-beginners/
- Ubuntu APT 包管理文档：https://ubuntu.com/server/docs/how-to/software/package-management/
- Ubuntu 环境变量社区文档：https://help.ubuntu.com/community/EnvironmentVariables
- REP-3 Target Platforms：https://www.ros.org/reps/rep-0003.html
- A Gentle Introduction to ROS：https://jokane.net/agitr/
