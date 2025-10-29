"""
环境配置文件（固定参数，不包含文件清单）
"""

# TOML 配置路径
CONFIG_PATH = "config.toml"

# Git 分支要求
BRANCH_NAME = "original"

# 前缀目录（源与目标目录的中间层）
PREFIX_DIR = "gui"

# 默认是否 Dry-Run 模式
DRY_RUN = False

# 每个子目录的白名单配置（不含 default）
# 键为目标目录名，值为要排除的文件或模式
EXCLUDE_WHITELIST = {
    "forbes_world_top_remake_mod": [
        "forbes.gui"
    ]
}