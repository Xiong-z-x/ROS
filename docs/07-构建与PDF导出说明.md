# 构建与 PDF 导出说明

## 目标

本仓库同时维护分章文件和最终合订版。为避免长期手工同步漂移，合订版应由 `docs/` 与 `chapters/` 中的源文件重新生成；PDF 则由合订版 Markdown 导出。

## 合订版生成规则

合订版文件为：

```text
ROS1零基础自学指导书-最终版.md
```

当前合订版顺序为：

1. `docs/06-学习成果验收与排障索引.md`
2. `chapters/01-ubuntu-linux入门.md`
3. `chapters/02-ros1基本概念.md`
4. `chapters/03-ros1安装方法完整说明.md`
5. `chapters/04-第一个ros系统.md`
6. `chapters/05-catkin工作空间与功能包.md`
7. `chapters/06-python与cpp编写ros节点.md`
8. `chapters/07-ros运行管理.md`
9. `chapters/08-机器人坐标模型与可视化.md`
10. `chapters/09-仿真与移动机器人入门.md`
11. `chapters/10-综合项目.md`

修改章节后，应重新生成合订版，再检查分章与合订版是否同步：

```bash
python scripts/build_combined_book.py
```

## PDF 导出

PDF 导出脚本为：

```bash
python scripts/export_book_pdf.py
```

脚本会生成：

```text
ROS1零基础自学指导书-最终版.html
ROS1零基础自学指导书-最终版.pdf
```

脚本使用 Python Markdown 生成 HTML，再调用本机 Chrome 或 Edge 的 headless print 功能导出 PDF。教材正文已改为文字说明、表格和清单，不再依赖额外图形渲染工具。

`book-build/` 是临时构建目录，不提交到 Git。

## 提交前检查

提交前至少运行：

```bash
git diff --check
rg -n "自定义未完成标记" README.md docs chapters "ROS1零基础自学指导书-最终版.md"
```

若修改了主体章节，还应确认：

```bash
rg -n "LoongArch64|龙芯|loong|交叉编译|Yocto|meta-ros" chapters "ROS1零基础自学指导书-最终版.md"
```

当前上册正文不应展开后续平台部署内容。
