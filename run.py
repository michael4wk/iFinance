#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iFinance 快速启动脚本

这是一个便捷的启动脚本，用户可以直接运行此文件来启动应用
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入主模块
from src.main import main

if __name__ == '__main__':
    main()