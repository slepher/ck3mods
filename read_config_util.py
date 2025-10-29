#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
read_config_util.py
-------------------
通用 TOML 配置读取函数。

功能：
✅ 自动检测 BOM（UTF-8 with BOM）
✅ 提供详细的 TOML 语法错误上下文
✅ 捕获异常时，打印调用者 Python 文件和行号
✅ 统一在项目中复用
"""

import toml
import traceback
import inspect


def read_config(config_path):
    """
    读取 TOML 文件，增强错误提示。
    如果解析失败，会打印出 TOML 文件中错误上下文，
    以及调用此函数的 Python 文件和行号。
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("\ufeff"):
            print(f"⚠️ 警告: 文件 {config_path} 含 BOM，请保存为 UTF-8 (无 BOM)。")

        config = toml.loads(content)
        print(f"✅ 成功读取配置文件: {config_path}")
        return config

    except toml.TomlDecodeError as e:
        # 定位调用者位置
        caller = inspect.stack()[1]
        caller_file = caller.filename
        caller_line = caller.lineno

        print(f"\n❌ TOML 解析失败: {config_path}")
        print(f"   错误信息: {e}")
        print(f"   出错位置: 行 {getattr(e, 'lineno', '?')}, 列 {getattr(e, 'colno', '?')}")
        print(f"   触发位置: {caller_file}:{caller_line}")

        # 打印上下文内容
        try:
            with open(config_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                if hasattr(e, "lineno"):
                    start = max(0, e.lineno - 3)
                    end = min(len(lines), e.lineno + 2)
                    print("📄 错误上下文：")
                    for i in range(start, end):
                        mark = ">>" if (i + 1) == e.lineno else "  "
                        print(f"{mark} {i + 1:03d}: {lines[i].rstrip()}")
        except Exception as fe:
            print(f"⚠️ 无法打印上下文: {fe}")

        print("\n💡 请检查 TOML 文件语法，例如：")
        print("   - 是否缺少引号、等号")
        print("   - 是否多余逗号、方括号或缩进错误")
        raise

    except UnicodeDecodeError as e:
        caller = inspect.stack()[1]
        print(f"\n❌ 编码错误: 无法读取 {config_path}")
        print(f"   错误信息: {e}")
        print(f"   触发位置: {caller.filename}:{caller.lineno}")
        print("💡 请确保文件使用 UTF-8（无 BOM）编码。")
        raise

    except FileNotFoundError:
        caller = inspect.stack()[1]
        print(f"\n❌ 配置文件不存在: {config_path}")
        print(f"   触发位置: {caller.filename}:{caller.lineno}")
        print("💡 请确认路径是否正确。")
        raise

    except Exception as e:
        caller = inspect.stack()[1]
        print(f"\n❌ 读取配置文件时发生未知错误: {type(e).__name__}")
        print(f"   错误信息: {e}")
        print(f"   触发位置: {caller.filename}:{caller.lineno}")
        print("📄 Traceback:")
        print(traceback.format_exc())
        raise