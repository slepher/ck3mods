"""
自动生成或更新 copy_plan.py 中的 COPY_PLAN。
支持每个子目录独立白名单规则（不再使用 default）。
"""

import os
import json
import fnmatch
from copy_env import PREFIX_DIR, EXCLUDE_WHITELIST

COPY_PLAN_FILE = "copy_plan.py"

def get_exclude_list(subdir):
    """获取当前子目录的白名单列表（若无定义则为空）"""
    return EXCLUDE_WHITELIST.get(subdir, [])


def is_excluded(filepath, exclude_patterns):
    """判断文件是否匹配任意排除规则"""
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filepath, pattern):
            return True
    return False


def generate_copy_plan(prefix_dir):
    """扫描当前目录，生成拷贝计划（按白名单过滤）"""
    current_dir = os.getcwd()
    copy_plan = {}

    for entry in os.listdir(current_dir):
        sub_path = os.path.join(current_dir, entry)

        # 只处理一级子目录（跳过非目录和前缀目录自身）
        if not os.path.isdir(sub_path) or entry == prefix_dir:
            continue

        prefix_path = os.path.join(sub_path, prefix_dir)
        if not os.path.isdir(prefix_path):
            continue

        exclude_patterns = get_exclude_list(entry)
        file_list = []

        for root, _, files in os.walk(prefix_path):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), prefix_path)
                rel_path = rel_path.replace("\\", "/")
                if not is_excluded(rel_path, exclude_patterns):
                    file_list.append(rel_path)

        if file_list:
            copy_plan[entry] = sorted(file_list)

    return copy_plan


def write_copy_plan(copy_plan):
    """将生成的 COPY_PLAN 写入 copy_plan.py"""
    header = (
        '"""\n'
        '自动生成的拷贝计划文件。\n'
        '由 generate_copy_plan.py 维护，请勿手动修改。\n'
        '"""\n\n'
    )

    body = "COPY_PLAN = " + json.dumps(copy_plan, indent=4, ensure_ascii=False) + "\n"

    # Windows 上务必使用 utf-8 而非 utf-8-sig
    with open(COPY_PLAN_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)

    print(f"✅ 已更新 {COPY_PLAN_FILE} 文件，共 {len(copy_plan)} 个目标目录。")


def main():
    print(f"🔍 正在扫描包含前缀目录 '{PREFIX_DIR}' 的子目录...\n")

    plan = generate_copy_plan(PREFIX_DIR)

    if not plan:
        print("⚠️ 未找到任何包含指定前缀目录的子目录。")
        return

    write_copy_plan(plan)


if __name__ == "__main__":
    main()