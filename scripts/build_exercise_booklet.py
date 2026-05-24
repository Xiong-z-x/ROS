#!/usr/bin/env python3
"""Build the standalone self-test and answer booklet."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "ROS1零基础自学指导书-自测题与参考答案小册.md"

PARTS = [
    "exercises/01-ubuntu-linux入门.md",
    "exercises/02-ros1基本概念.md",
    "exercises/03-ros1安装方法完整说明.md",
    "exercises/04-第一个ros系统.md",
    "exercises/05-catkin工作空间与功能包.md",
    "exercises/06-python与cpp编写ros节点.md",
    "exercises/07-ros运行管理.md",
    "exercises/08-机器人坐标模型与可视化.md",
    "exercises/09-仿真与移动机器人入门.md",
    "exercises/10-综合项目.md",
]

HEADER = """# ROS1 零基础自学指导书：自测题与参考答案小册

生成日期：2026-05-24

本小册从《ROS1 零基础自学指导书（最终版）》正文中独立出来，集中收录 10 个主体章节的自测题与参考答案。这样可以减少正文篇幅，也方便学生先完成练习，再对照答案检查理解。

建议使用方式：

1. 学完对应正文章节后，先独立完成本小册中的自测题。
2. 作答时不要只写结论，应写清原因、命令、观察现象和排障路径。
3. 完成后再阅读参考答案，检查自己的解释是否覆盖关键事实。
4. 如果答案中涉及命令，应回到 Ubuntu 20.04 + ROS Noetic 环境中实际验证。"""


def main() -> None:
    sections = [HEADER.rstrip()]
    for part in PARTS:
        path = ROOT / part
        sections.append(path.read_text(encoding="utf-8").strip())
    OUTPUT.write_text("\n\n---\n\n".join(sections) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
