# 配置管理工具
# 提供配置加载和验证功能

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from ..utils.exceptions import ConfigurationError


class Config:
    """
    配置管理类

    负责加载环境变量和提供配置访问接口
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            env_file: 环境变量文件路径，默认为项目根目录的.env文件
        """
        self._loaded = False
        self.load_env(env_file)

    def load_env(self, env_file: Optional[str] = None) -> None:
        """
        加载环境变量文件

        Args:
            env_file: 环境变量文件路径
        """
        if load_dotenv is None:
            return

        if env_file is None:
            # 查找config目录下的.env文件
            current_dir = Path(__file__).parent  # src/utils
            project_root = current_dir.parent.parent  # 项目根目录
            env_file = project_root / "config" / ".env"

        if Path(env_file).exists():
            load_dotenv(env_file, override=True)  # 强制覆盖现有环境变量
            self._loaded = True

    def get(
        self, key: str, default: Optional[str] = None, required: bool = False
    ) -> str:
        """
        获取配置值

        Args:
            key: 配置键名
            default: 默认值
            required: 是否为必需配置

        Returns:
            str: 配置值

        Raises:
            ConfigurationError: 当必需配置缺失时
        """
        value = os.getenv(key, default)

        if required and not value:
            raise ConfigurationError(f"Required configuration '{key}' is missing")

        return value or ""

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        获取布尔类型配置值

        Args:
            key: 配置键名
            default: 默认值

        Returns:
            bool: 配置值
        """
        value = self.get(key, str(default).lower())
        return value.lower() in ("true", "1", "yes", "on")

    def get_int(self, key: str, default: int = 0) -> int:
        """
        获取整数类型配置值

        Args:
            key: 配置键名
            default: 默认值

        Returns:
            int: 配置值

        Raises:
            ConfigurationError: 当配置值无法转换为整数时
        """
        value = self.get(key, str(default))
        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(
                f"Configuration '{key}' must be an integer, got '{value}'"
            )

    def validate_required_configs(self, required_keys: list[str]) -> None:
        """
        验证必需的配置项

        Args:
            required_keys: 必需的配置键名列表

        Raises:
            ConfigurationError: 当有必需配置缺失时
        """
        missing_keys = []
        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)

        if missing_keys:
            raise ConfigurationError(
                f"Missing required configurations: {', '.join(missing_keys)}"
            )

    @property
    def is_loaded(self) -> bool:
        """
        检查环境变量是否已加载

        Returns:
            bool: 是否已加载
        """
        return self._loaded


# 全局配置实例
config = Config()
