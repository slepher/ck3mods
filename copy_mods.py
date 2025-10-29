#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import argparse
from copy_env import DRY_RUN
from copy_plan import COPY_PLAN
from read_config_util import read_config
from copy_env import CONFIG_PATH


def abs_path_str(path):
    """返回绝对路径并统一为正斜杠"""
    return os.path.abspath(path).replace("\\", "/")


def generate_mod_file(src_path, dst_path, mod_root):
    """生成 .mod 文件"""
    descriptor_file = os.path.join(src_path, "descriptor.mod")
    sub_dir = os.path.basename(src_path)
    mod_file_path = os.path.join(mod_root, f"{sub_dir}.mod")

    if not os.path.exists(descriptor_file):
        print(f"⚠️ descriptor.mod 不存在，跳过生成 {sub_dir}.mod 文件")
        return

    dst_path_abs = abs_path_str(dst_path)
    try:
        with open(descriptor_file, "r", encoding="utf-8") as f:
            content = f.read().rstrip()

        content += f'\npath="{dst_path_abs}"\n'

        if DRY_RUN:
            print(f"🧪 [Dry-Run] 生成 .mod 文件: {abs_path_str(mod_file_path)} 内容:\n{content}")
        else:
            with open(mod_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 生成 .mod 文件: {abs_path_str(mod_file_path)}")
    except Exception as e:
        print(f"❌ 生成 {sub_dir}.mod 文件失败: {e}")


def replace_directory(src_path, dst_path):
    """替换目录"""
    if not os.path.isdir(src_path):
        print(f"⚠️ 源目录不存在: {abs_path_str(src_path)}")
        return False

    if os.path.exists(dst_path):
        if DRY_RUN:
            print(f"🧪 [Dry-Run] 删除目标目录: {abs_path_str(dst_path)}")
        else:
            shutil.rmtree(dst_path)
            print(f"🗑️ 删除目标目录: {abs_path_str(dst_path)}")

    if DRY_RUN:
        print(f"🧪 [Dry-Run] 拷贝 {abs_path_str(src_path)} → {abs_path_str(dst_path)}")
    else:
        shutil.copytree(src_path, dst_path)
        print(f"📦 拷贝子目录: {abs_path_str(dst_path)}")

    return True


def copy_subdir(src_root, mod_root, sub_dir):
    """拷贝子目录并生成 .mod 文件"""
    src_path = os.path.join(src_root, sub_dir)
    dst_path = os.path.join(mod_root, sub_dir)

    if replace_directory(src_path, dst_path):
        generate_mod_file(src_path, dst_path, mod_root)


def match_subdirs(inputs):
    """
    根据前缀匹配 COPY_PLAN 子目录
    返回匹配到的唯一子目录列表
    """
    matched = []
    for inp in inputs:
        candidates = [s for s in COPY_PLAN if s.startswith(inp)]
        if not candidates:
            print(f"⚠️ 未匹配到子目录: {inp}")
        elif len(candidates) > 1:
            print(f"⚠️ 前缀 '{inp}' 匹配到多个子目录: {', '.join(candidates)}，请使用更长前缀")
        else:
            matched.append(candidates[0])
    return matched


def main():
    parser = argparse.ArgumentParser(description="拷贝子项目并生成 .mod 文件")
    parser.add_argument(
        "subdirs",
        nargs="*",
        help="指定要拷贝的子项目名称或前缀（默认拷贝 COPY_PLAN 所有子目录）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印操作，不实际删除或拷贝",
    )
    args = parser.parse_args()

    global DRY_RUN
    if args.dry_run:
        DRY_RUN = True

    src_root = os.getcwd()

    # 读取配置获取 paradox_root
    try:
        config = read_config(CONFIG_PATH)
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        exit(1)

    paradox_root = config.get("paradox_root")
    if not paradox_root:
        print("❌ 配置文件中未指定 paradox_root")
        exit(1)
    if not os.path.exists(paradox_root) or not os.path.isdir(paradox_root):
        print(f"❌ paradox_root 不存在或不是目录: {abs_path_str(paradox_root)}")
        exit(1)

    # 实际 mod 根目录为 paradox_root/mod
    mod_root = os.path.join(paradox_root, "mod")
    if not os.path.exists(mod_root) or not os.path.isdir(mod_root):
        print(f"❌ mod 子目录不存在: {abs_path_str(mod_root)}")
        exit(1)

    if args.subdirs:
        sub_dirs = match_subdirs(args.subdirs)
    else:
        sub_dirs = list(COPY_PLAN.keys())

    for sub_dir in sub_dirs:
        copy_subdir(src_root, mod_root, sub_dir)


if __name__ == "__main__":
    main()