#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
copy_files.py
--------------
从指定目录中拷贝预定义文件到当前目录下对应的子目录中。

功能特点：
✅ 从 copy_env.py 和 copy_plan.py 读取配置
✅ 从 read_config_util.py 导入统一 TOML 读取函数
✅ 检查当前 Git 分支是否匹配
✅ 支持 dry-run 模式（仅打印不实际拷贝）
✅ 检查目标子目录是否存在，否则报错
✅ 自动创建缺失的目标文件夹
✅ 打印“新建”或“覆盖”状态
"""

import os
import sys
import shutil
import subprocess
from read_config_util import read_config
from copy_env import CONFIG_PATH, PREFIX_DIR, BRANCH_NAME, DRY_RUN
from copy_plan import COPY_PLAN


# ===== 函数定义 =====

def check_git_branch(required_branch):
    """检查当前 git 分支是否正确"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        current_branch = result.stdout.strip()
        print(f"📦 当前分支: {current_branch}")
        if current_branch != required_branch:
            print(f"❌ 当前分支不是要求的分支：{required_branch}")
            sys.exit(1)
    except subprocess.CalledProcessError:
        print("⚠️ 未检测到 Git 仓库或无法获取分支名。")
    except Exception as e:
        print(f"⚠️ 检查 Git 分支时出错: {e}")


def copy_files(prefix_dir, files, target_dir, src_root):
    """
    拷贝文件：
    - 从 src_root/prefix_dir/file -> ./target_dir/prefix_dir/file
    - 目录不存在时报错
    - 文件不存在时跳过
    """
    if not os.path.isdir(target_dir):
        print(f"❌ 子目录不存在: {target_dir}")
        raise FileNotFoundError(target_dir)

    for file in files:
        src_path = os.path.join(src_root, prefix_dir, file)
        dst_path = os.path.join(target_dir, prefix_dir, file)

        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)

        if not os.path.exists(src_path):
            print(f"⚠️ 源文件不存在: {src_path}")
            continue

        if DRY_RUN:
            print(f"🧪 [Dry-Run] {src_path} → {dst_path}")
            continue

        if os.path.exists(dst_path):
            shutil.copy2(src_path, dst_path)
            print(f"🔁 覆盖: {dst_path}")
        else:
            shutil.copy2(src_path, dst_path)
            print(f"🆕 新建: {dst_path}")


# ===== 主程序入口 =====

def main():
    print("🚀 启动拷贝任务...\n")

    # 1. 检查 Git 分支
    if BRANCH_NAME:
        check_git_branch(BRANCH_NAME)

    # 2. 读取 TOML 配置
    try:
        config = read_config(CONFIG_PATH)
    except Exception:
        print("❌ 无法加载配置文件，程序终止。")
        sys.exit(1)

    src_root = config.get("source_dir")
    if not src_root or not os.path.isdir(src_root):
        print(f"❌ 配置文件中指定的源目录不存在: {src_root}")
        sys.exit(1)

    # 3. 执行拷贝
    print(f"\n📂 源目录: {src_root}")
    print(f"📂 前缀目录: {PREFIX_DIR}")
    print(f"🧩 Dry-Run 模式: {'启用' if DRY_RUN else '关闭'}\n")

    for target_dir, files in COPY_PLAN.items():
        if not files:
            print(f"⚙️ 跳过目录 {target_dir}（无文件可拷贝）")
            continue
        print(f"\n📦 拷贝到子目录: {target_dir}")
        copy_files(PREFIX_DIR, files, target_dir, src_root)

    print("\n✅ 拷贝任务完成！")


if __name__ == "__main__":
    main()