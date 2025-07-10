# 应用配置文件
# 管理应用的各种配置参数

import os
from typing import Optional


class Settings:
    """
    应用配置类
    
    从环境变量中读取配置参数，提供默认值
    """
    
    # Alpha Vantage API配置
    ALPHA_VANTAGE_API_KEY: str = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    ALPHA_VANTAGE_BASE_URL: str = os.getenv(
        'ALPHA_VANTAGE_BASE_URL', 
        'https://www.alphavantage.co/query'
    )
    
    # 应用基础配置
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # 缓存配置
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '300'))
    
    # Web服务器配置
    HOST: str = os.getenv('HOST', '127.0.0.1')
    PORT: int = int(os.getenv('PORT', '8050'))
    
    # API请求配置
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: int = int(os.getenv('RETRY_DELAY', '1'))
    
    @classmethod
    def validate(cls) -> bool:
        """
        验证必要的配置是否已设置
        
        Returns:
            bool: 配置是否有效
        """
        if not cls.ALPHA_VANTAGE_API_KEY:
            return False
        return True
    
    @classmethod
    def get_missing_configs(cls) -> list[str]:
        """
        获取缺失的必要配置项
        
        Returns:
            list[str]: 缺失的配置项列表
        """
        missing = []
        if not cls.ALPHA_VANTAGE_API_KEY:
            missing.append('ALPHA_VANTAGE_API_KEY')
        return missing


# 全局配置实例
settings = Settings()