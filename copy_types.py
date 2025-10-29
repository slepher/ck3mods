#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from copy_env import DRY_RUN, TYPES, CONFIG_PATH
from read_config_util import read_config


def abs_path_str(path):
    """返回绝对路径并统一为正斜杠"""
    return os.path.abspath(path).replace("\\", "/")


def copy_file(src_file, dst_file):
    """拷贝单个文件"""
    if not os.path.exists(src_file):
        print(f"⚠️ 文件不存在: {abs_path_str(src_file)}")
        return

    dst_dir = os.path.dirname(dst_file)
    if not os.path.exists(dst_dir):
        if DRY_RUN:
            print(f"🧪 [Dry-Run] 创建目录: {abs_path_str(dst_dir)}")
        else:
            os.makedirs(dst_dir, exist_ok=True)
            print(f"📁 创建目录: {abs_path_str(dst_dir)}")

    if DRY_RUN:
        print(f"🧪 [Dry-Run] 拷贝文件: {abs_path_str(src_file)} → {abs_path_str(dst_file)}")
    else:
        shutil.copy2(src_file, dst_file)
        print(f"📄 拷贝文件: {abs_path_str(dst_file)}")


def copy_logs(paradox_root, target_root):
    logs_dir = os.path.join(paradox_root, "logs")
    if not os.path.exists(logs_dir) or not os.path.isdir(logs_dir):
        print(f"❌ logs 目录不存在: {abs_path_str(logs_dir)}")
        return

    # 拷贝 TYPES 指定的文件，源后缀 .log → 目标后缀 .txt
    for fname in TYPES:
        src_file = os.path.join(logs_dir, f"{fname}.log")
        dst_file = os.path.join(target_root, f"{fname}.txt")
        copy_file(src_file, dst_file)

    # 拷贝 data_types 子目录下所有文件（保留原名）
    data_types_src = os.path.join(logs_dir, "data_types")
    data_types_dst = os.path.join(target_root, "data_types")
    if os.path.exists(data_types_src) and os.path.isdir(data_types_src):
        for root, _, files in os.walk(data_types_src):
            for f in files:
                rel_path = os.path.relpath(root, data_types_src)
                dst_dir = os.path.join(data_types_dst, rel_path)
                src_file = os.path.join(root, f)
                dst_file = os.path.join(dst_dir, f)
                copy_file(src_file, dst_file)
    else:
        print(f"⚠️ data_types 目录不存在: {abs_path_str(data_types_src)}")


def main():
    # 读取 paradox_root 配置
    try:
        config = read_config(CONFIG_PATH)
    except Exception as e:
        print(f"❌ 无法读取配置文件: {e}")
        return

    paradox_root = config.get("paradox_root")
    if not paradox_root or not os.path.exists(paradox_root) or not os.path.isdir(paradox_root):
        print(f"❌ paradox_root 不存在或不是目录: {abs_path_str(paradox_root)}")
        return

    # 目标目录 ck3types
    target_root = os.path.join(os.getcwd(), "ck3types")
    if not os.path.exists(target_root):
        if DRY_RUN:
            print(f"🧪 [Dry-Run] 创建目录: {abs_path_str(target_root)}")
        else:
            os.makedirs(target_root, exist_ok=True)
            print(f"📁 创建目录: {abs_path_str(target_root)}")

    copy_logs(paradox_root, target_root)


if __name__ == "__main__":
    main()