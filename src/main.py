#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iFinance 应用主入口文件

这是应用程序的启动入口，负责初始化各个组件并启动Web服务器
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import config
from src.utils.logger import get_logger
from src.utils.exceptions import ConfigurationError
from src.ui.app import create_app

# 获取主应用日志记录器
logger = get_logger(__name__)

# 创建全局应用实例供gunicorn使用
server = None


def validate_environment() -> None:
    """
    验证运行环境和必要配置
    
    Raises:
        ConfigurationError: 当环境配置无效时
    """
    logger.info("Validating environment configuration...")
    
    # 检查必要的配置项
    required_configs = ['ALPHA_VANTAGE_API_KEY']
    
    try:
        config.validate_required_configs(required_configs)
        logger.info("Environment validation passed")
    except Exception as e:
        logger.error(f"Environment validation failed: {str(e)}")
        raise ConfigurationError(f"Environment validation failed: {str(e)}")


def setup_application() -> object:
    """
    设置并初始化应用程序
    
    Returns:
        object: Dash应用实例
    
    Raises:
        Exception: 当应用初始化失败时
    """
    logger.info("Setting up iFinance application...")
    
    try:
        # 验证环境
        validate_environment()
        
        # 创建应用实例
        app = create_app()
        
        logger.info("Application setup completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to setup application: {str(e)}")
        raise


def run_application(app, debug: bool = False, host: str = None, port: int = None) -> None:
    """
    运行应用程序
    
    Args:
        app: Dash应用实例
        debug: 是否启用调试模式
        host: 服务器主机地址
        port: 服务器端口
    """
    global server
    
    # 设置全局server变量供gunicorn使用
    server = app.server
    
    # 获取端口配置（支持环境变量PORT）
    import os
    host = host or os.environ.get('HOST', config.get('HOST', '127.0.0.1'))
    port = port or int(os.environ.get('PORT', config.get_int('PORT', 8050)))
    
    # 生产环境下禁用调试模式
    if os.environ.get('ENVIRONMENT') == 'production':
        debug = False
    
    logger.info(f"Starting iFinance server on {host}:{port}")
    logger.info(f"Debug mode: {'enabled' if debug else 'disabled'}")
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    
    try:
        # 启动服务器
        app.run(
            debug=debug,
            host=host,
            port=port,
            dev_tools_hot_reload=debug,
            dev_tools_ui=debug
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application crashed: {str(e)}")
        raise


def init_server():
    """初始化服务器实例供gunicorn使用"""
    global server
    if server is None:
        try:
            validate_environment()
            app = setup_application()
            server = app.server
        except Exception as e:
            logger.error(f"服务器初始化失败: {str(e)}")
            raise
    return server


def main() -> None:
    """
    主函数 - 应用程序入口点
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='iFinance - 智能金融数据查询系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python -m src.main                    # 使用默认配置启动
  python -m src.main --debug            # 启用调试模式
  python -m src.main --host 0.0.0.0     # 监听所有网络接口
  python -m src.main --port 8080        # 使用自定义端口
        """
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式（热重载、详细错误信息等）'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        help='服务器主机地址（默认: 127.0.0.1）'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='服务器端口（默认: 8050）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='iFinance 1.0.0'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
    
    try:
        # 显示启动信息
        logger.info("="*50)
        logger.info("iFinance - 智能金融数据查询系统")
        logger.info("版本: 1.0.0")
        logger.info("="*50)
        
        # 设置应用
        app = setup_application()
        
        # 运行应用
        run_application(
            app,
            debug=args.debug,
            host=args.host,
            port=args.port
        )
        
    except ConfigurationError as e:
        logger.error(f"配置错误: {str(e)}")
        logger.error("请检查您的环境变量配置，特别是 ALPHA_VANTAGE_API_KEY")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        if args.debug:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


# 在模块级别初始化server变量供gunicorn使用
try:
    server = init_server()
except Exception:
    # 如果初始化失败，设置为None，稍后再尝试
    server = None


if __name__ == '__main__':
    main()
else:
    # 当作为模块导入时，确保server已初始化
    if server is None:
        try:
            server = init_server()
        except Exception as e:
            logger.warning(f"模块导入时服务器初始化失败: {str(e)}")