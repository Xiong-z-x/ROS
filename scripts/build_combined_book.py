#!/usr/bin/env python3
"""Build the combined ROS1 textbook Markdown file from source chapters."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "ROS1零基础自学指导书-最终版.md"

PARTS = [
    "docs/06-学习成果验收与排障索引.md",
    "chapters/01-ubuntu-linux入门.md",
    "chapters/02-ros1基本概念.md",
    "chapters/03-ros1安装方法完整说明.md",
    "chapters/04-第一个ros系统.md",
    "chapters/05-catkin工作空间与功能包.md",
    "chapters/06-python与cpp编写ros节点.md",
    "chapters/07-ros运行管理.md",
    "chapters/08-机器人坐标模型与可视化.md",
    "chapters/09-仿真与移动机器人入门.md",
    "chapters/10-综合项目.md",
]

HEADER = """# ROS1 零基础自学指导书（最终版）

生成日期：2026-05-24

本书面向没有 Ubuntu、Linux 命令行和 ROS 经验的大学生，主线环境为 **Ubuntu 20.04 Focal Fossa + ROS1 Noetic Ninjemys**。写作目标不是让读者机械复制命令，而是帮助读者理解每个命令、每个节点、每条 topic、每个参数和每个配置文件在 ROS 系统中的作用。

ROS Noetic 已于 **2025-05-31** 到达官方 EOL。本书继续使用 Noetic，是为了学习 ROS1 体系、维护历史项目和理解现有机器人系统，不是建议新项目默认继续优先选择 ROS1。

## 使用说明

建议按章节顺序学习。每章都包含本章目标、概念解释、最小可运行实验、正确现象、常见错误、自测题、参考答案和延伸阅读。读者应在 Ubuntu 20.04 + ROS Noetic 环境中实际运行命令，并在每次实验后先独立回答自测题，再对照参考答案检查理解是否完整。

本书包含“学习成果验收与排障索引”，用于把每章学习内容转换成可观察交付物。自学时不应只看正文，应按索引保留命令输出、截图、数据流清单或 README 片段，作为确实完成实验的证据。

本书主线不展开后续平台部署主题，也不把高级算法推导作为主体。SLAM、定位、导航等内容只作为 ROS 系统集成案例出现。

## 总目录

0. 学习成果验收与排障索引
1. Ubuntu 与 Linux 入门
2. ROS1 基本概念
3. ROS1 安装方法完整说明
4. 第一个 ROS 系统
5. catkin 工作空间与功能包
6. Python 与 C++ 编写 ROS 节点
7. ROS 运行管理
8. 机器人坐标、模型与可视化
9. 仿真与移动机器人入门
10. 综合项目

---"""


def main() -> None:
    sections = [HEADER.rstrip()]
    for part in PARTS:
        path = ROOT / part
        sections.append(path.read_text(encoding="utf-8").strip())
    OUTPUT.write_text("\n\n---\n\n".join(sections) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
