#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序启动脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.app import create_app
from src.utils.config import config


def main():
    """
    主函数：启动应用程序
    """
    # 检查环境配置
    if not config.get("ALPHA_VANTAGE_API_KEY"):
        print("❌ 错误: 未找到 ALPHA_VANTAGE_API_KEY 环境变量")
        print("请在 .env 文件中设置 ALPHA_VANTAGE_API_KEY")
        sys.exit(1)
    
    print("🚀 启动 iFinance 应用程序...")
    
    try:
        # 创建应用实例
        app = create_app()
        
        # 启动应用
        print("✅ 应用程序已启动")
        print("🌐 访问地址: http://127.0.0.1:8050/")
        print("按 Ctrl+C 停止应用程序")
        
        app.run(
            debug=True,
            host="127.0.0.1",
            port=8050,
            dev_tools_hot_reload=True
        )
        
    except Exception as e:
        print(f"❌ 启动应用程序时出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()