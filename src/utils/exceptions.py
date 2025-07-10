# 自定义异常类
# 定义应用中使用的各种异常类型


class iFinanceError(Exception):
    """
    iFinance应用的基础异常类
    
    所有自定义异常都应该继承自这个类
    """
    pass


class ConfigurationError(iFinanceError):
    """
    配置相关异常
    
    当配置文件缺失、配置项错误或必需配置未设置时抛出
    """
    pass


class APIError(iFinanceError):
    """
    API调用相关异常
    
    当API调用失败、返回错误或网络问题时抛出
    """
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class APIRateLimitError(APIError):
    """
    API频率限制异常
    
    当API调用超过频率限制时抛出
    """
    pass


class APIAuthenticationError(APIError):
    """
    API认证异常
    
    当API密钥无效或认证失败时抛出
    """
    pass


class DataValidationError(iFinanceError):
    """
    数据验证异常
    
    当数据格式不正确、缺失必需字段或验证失败时抛出
    """
    
    def __init__(self, message: str, field: str = None, value = None):
        super().__init__(message)
        self.field = field
        self.value = value


class DataProcessingError(iFinanceError):
    """
    数据处理异常
    
    当数据转换、计算或处理过程中发生错误时抛出
    """
    pass


class NetworkError(iFinanceError):
    """
    网络连接异常
    
    当网络请求失败、超时或连接问题时抛出
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class CacheError(iFinanceError):
    """
    缓存相关异常
    
    当缓存操作失败时抛出
    """
    pass


class UIError(iFinanceError):
    """
    用户界面异常
    
    当UI组件初始化或渲染失败时抛出
    """
    pass