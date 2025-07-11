# 日志工具模块
# 提供统一的日志记录功能

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import config


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    设置并返回一个配置好的日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则只输出到控制台
        format_string: 自定义日志格式字符串

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 设置日志级别
    if level is None:
        level = config.get("LOG_LEVEL", "INFO")

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 设置日志格式
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    formatter = logging.Formatter(format_string)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器的便捷函数

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        logging.Logger: 日志记录器实例
    """
    return setup_logger(name)


class LoggerMixin:
    """
    日志记录器混入类

    为其他类提供日志记录功能
    """

    @property
    def logger(self) -> logging.Logger:
        """
        获取当前类的日志记录器

        Returns:
            logging.Logger: 日志记录器实例
        """
        if not hasattr(self, "_logger"):
            self._logger = get_logger(
                self.__class__.__module__ + "." + self.__class__.__name__
            )
        return self._logger


# 应用主日志记录器
app_logger = get_logger("ifinance")
