#!/usr/bin/env python3
"""
Render配置问题修复脚本
用于诊断和修复Render环境中的配置加载问题
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def log_message(message: str):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def analyze_config_loading_issue():
    """分析配置加载问题"""
    log_message("=== 分析配置加载问题 ===")
    
    # 检查.env文件
    env_file_path = project_root / "config" / ".env"
    log_message(f"检查.env文件: {env_file_path}")
    
    if env_file_path.exists():
        log_message("✅ .env文件存在")
        
        # 读取.env文件内容
        with open(env_file_path, 'r') as f:
            content = f.read()
        
        log_message("📄 .env文件内容:")
        for line in content.strip().split('\n'):
            if line.strip() and not line.startswith('#'):
                if 'API_KEY' in line:
                    key, value = line.split('=', 1)
                    log_message(f"  {key}={value[:8]}...")
                else:
                    log_message(f"  {line}")
    else:
        log_message("❌ .env文件不存在")
    
    # 检查当前环境变量
    log_message("\n📋 当前环境变量:")
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if api_key:
        log_message(f"  ALPHA_VANTAGE_API_KEY={api_key[:8]}...")
    else:
        log_message("  ALPHA_VANTAGE_API_KEY=未设置")
    
    render_env = os.getenv('RENDER')
    log_message(f"  RENDER={render_env}")
    
    environment = os.getenv('ENVIRONMENT')
    log_message(f"  ENVIRONMENT={environment}")

def test_config_loading_behavior():
    """测试配置加载行为"""
    log_message("\n=== 测试配置加载行为 ===")
    
    # 设置测试环境变量
    test_api_key = "TEST_RENDER_API_KEY"
    os.environ['ALPHA_VANTAGE_API_KEY'] = test_api_key
    log_message(f"设置测试环境变量: ALPHA_VANTAGE_API_KEY={test_api_key}")
    
    # 测试配置系统加载
    try:
        # 重新导入配置系统
        import importlib
        if 'src.utils.config' in sys.modules:
            importlib.reload(sys.modules['src.utils.config'])
        
        from src.utils.config import Config
        
        # 创建新的配置实例
        test_config = Config()
        loaded_api_key = test_config.get('ALPHA_VANTAGE_API_KEY')
        
        log_message(f"配置系统加载的API密钥: {loaded_api_key}")
        
        if loaded_api_key == test_api_key:
            log_message("✅ 配置系统正确使用环境变量")
            return True
        else:
            log_message("❌ 配置系统被.env文件覆盖")
            return False
            
    except Exception as e:
        log_message(f"❌ 配置测试失败: {e}")
        return False

def create_render_safe_config():
    """创建Render安全的配置类"""
    log_message("\n=== 创建Render安全配置 ===")
    
    config_content = '''# Render安全的配置管理工具
# 优先使用环境变量，避免.env文件覆盖

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from ..utils.exceptions import ConfigurationError


class RenderSafeConfig:
    """
    Render安全的配置管理类
    
    在Render环境中优先使用环境变量，避免.env文件覆盖
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            env_file: 环境变量文件路径，默认为项目根目录的.env文件
        """
        self._loaded = False
        self._is_render_env = self._detect_render_environment()
        self.load_env(env_file)

    def _detect_render_environment(self) -> bool:
        """
        检测是否在Render环境中运行
        
        Returns:
            bool: 是否在Render环境中
        """
        # 检查Render特有的环境变量
        render_indicators = [
            os.getenv('RENDER'),
            os.getenv('RENDER_SERVICE_ID'),
            os.getenv('RENDER_SERVICE_NAME'),
            'onrender.com' in os.getenv('RENDER_EXTERNAL_URL', ''),
            os.getenv('ENVIRONMENT') == 'production'
        ]
        
        return any(render_indicators)

    def load_env(self, env_file: Optional[str] = None) -> None:
        """
        加载环境变量文件
        
        在Render环境中，不加载.env文件以避免覆盖环境变量

        Args:
            env_file: 环境变量文件路径
        """
        if load_dotenv is None:
            return
        
        # 在Render环境中，跳过.env文件加载
        if self._is_render_env:
            self._loaded = True
            return

        if env_file is None:
            # 查找config目录下的.env文件
            current_dir = Path(__file__).parent  # src/utils
            project_root = current_dir.parent.parent  # 项目根目录
            env_file = project_root / "config" / ".env"

        if Path(env_file).exists():
            # 在非Render环境中，不覆盖现有环境变量
            load_dotenv(env_file, override=False)
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

    @property
    def is_render_environment(self) -> bool:
        """
        检查是否在Render环境中
        
        Returns:
            bool: 是否在Render环境中
        """
        return self._is_render_env

    @property
    def is_loaded(self) -> bool:
        """
        检查环境变量是否已加载

        Returns:
            bool: 是否已加载
        """
        return self._loaded


# 全局配置实例
config = RenderSafeConfig()
'''
    
    # 保存到新文件
    new_config_path = project_root / "src" / "utils" / "render_safe_config.py"
    
    with open(new_config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    log_message(f"✅ 创建Render安全配置文件: {new_config_path}")
    return new_config_path

def test_render_safe_config():
    """测试Render安全配置"""
    log_message("\n=== 测试Render安全配置 ===")
    
    # 设置Render环境
    os.environ['RENDER'] = 'true'
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'SDMG58OJI9FOIUWW'
    
    try:
        # 导入新的配置
        sys.path.insert(0, str(project_root / "src" / "utils"))
        import render_safe_config
        
        config = render_safe_config.config
        
        log_message(f"检测到Render环境: {config.is_render_environment}")
        
        api_key = config.get('ALPHA_VANTAGE_API_KEY')
        log_message(f"获取的API密钥: {api_key[:8] if api_key else 'None'}...")
        
        if api_key == 'SDMG58OJI9FOIUWW':
            log_message("✅ Render安全配置工作正常")
            return True
        else:
            log_message(f"❌ API密钥不正确: {api_key}")
            return False
            
    except Exception as e:
        log_message(f"❌ 测试失败: {e}")
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}")
        return False

def create_config_patch():
    """创建配置补丁"""
    log_message("\n=== 创建配置补丁 ===")
    
    # 备份原始配置文件
    original_config = project_root / "src" / "utils" / "config.py"
    backup_config = project_root / "src" / "utils" / "config.py.backup"
    
    if not backup_config.exists():
        import shutil
        shutil.copy2(original_config, backup_config)
        log_message(f"✅ 备份原始配置: {backup_config}")
    
    # 创建修复后的配置内容
    fixed_config_content = '''# 配置管理工具
# 提供配置加载和验证功能
# 修复版本：在Render环境中优先使用环境变量

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
    在Render环境中优先使用环境变量
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            env_file: 环境变量文件路径，默认为项目根目录的.env文件
        """
        self._loaded = False
        self._is_render_env = self._detect_render_environment()
        self.load_env(env_file)

    def _detect_render_environment(self) -> bool:
        """
        检测是否在Render环境中运行
        
        Returns:
            bool: 是否在Render环境中
        """
        # 检查Render特有的环境变量或域名
        render_indicators = [
            os.getenv('RENDER') is not None,
            os.getenv('RENDER_SERVICE_ID') is not None,
            os.getenv('RENDER_SERVICE_NAME') is not None,
            'onrender.com' in os.getenv('RENDER_EXTERNAL_URL', ''),
            os.getenv('ENVIRONMENT') == 'production'
        ]
        
        return any(render_indicators)

    def load_env(self, env_file: Optional[str] = None) -> None:
        """
        加载环境变量文件
        
        在Render环境中，不覆盖现有环境变量

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
            # 在Render环境中，不覆盖现有环境变量
            override = not self._is_render_env
            load_dotenv(env_file, override=override)
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
    def is_render_environment(self) -> bool:
        """
        检查是否在Render环境中
        
        Returns:
            bool: 是否在Render环境中
        """
        return self._is_render_env

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
'''
    
    # 保存修复后的配置
    fixed_config_path = project_root / "src" / "utils" / "config_fixed.py"
    
    with open(fixed_config_path, 'w', encoding='utf-8') as f:
        f.write(fixed_config_content)
    
    log_message(f"✅ 创建修复后的配置文件: {fixed_config_path}")
    return fixed_config_path

def main():
    """主函数"""
    log_message("开始Render配置问题诊断和修复")
    log_message("="*60)
    
    # 1. 分析配置加载问题
    analyze_config_loading_issue()
    
    # 2. 测试当前配置行为
    current_config_ok = test_config_loading_behavior()
    
    # 3. 创建Render安全配置
    render_safe_config_path = create_render_safe_config()
    
    # 4. 测试Render安全配置
    render_safe_ok = test_render_safe_config()
    
    # 5. 创建配置补丁
    fixed_config_path = create_config_patch()
    
    # 总结
    log_message("\n" + "="*60)
    log_message("=== 诊断和修复总结 ===")
    log_message(f"当前配置系统: {'✅ 正常' if current_config_ok else '❌ 有问题'}")
    log_message(f"Render安全配置: {'✅ 正常' if render_safe_ok else '❌ 有问题'}")
    
    if not current_config_ok:
        log_message("\n🔧 问题确认:")
        log_message("配置系统在加载.env文件时覆盖了环境变量")
        log_message("这导致Render环境中的API密钥被本地.env文件覆盖")
        
        log_message("\n💡 解决方案:")
        log_message(f"1. 使用修复后的配置文件: {fixed_config_path}")
        log_message("2. 或者在Render部署时确保不包含config/.env文件")
        log_message("3. 或者修改.env文件加载逻辑，在Render环境中不覆盖环境变量")
        
        log_message("\n📋 立即修复步骤:")
        log_message("1. 备份当前config.py文件")
        log_message("2. 用config_fixed.py替换config.py")
        log_message("3. 重新部署到Render")
        log_message("4. 验证股票搜索功能")
    else:
        log_message("\n🎉 配置系统工作正常")

if __name__ == "__main__":
    main()