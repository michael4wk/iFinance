# 基础API客户端
# 提供通用的API调用功能和错误处理


from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.config import config
from ..utils.exceptions import (
    APIAuthenticationError,
    APIError,
    APIRateLimitError,
    NetworkError,
)
from ..utils.logger import LoggerMixin


class BaseAPIClient(LoggerMixin, ABC):
    """
    基础API客户端抽象类

    提供通用的HTTP请求功能、错误处理和重试机制
    """

    def __init__(self, base_url: str, timeout: int = None, max_retries: int = None):
        """
        初始化API客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or config.get_int("REQUEST_TIMEOUT", 30)
        self.max_retries = max_retries or config.get_int("MAX_RETRIES", 3)
        self.retry_delay = config.get_int("RETRY_DELAY", 1)

        # 配置会话和重试策略
        self.session = self._create_session()

        self.logger.info(
            f"Initialized {self.__class__.__name__} with base_url: {self.base_url}"
        )

    def _create_session(self) -> requests.Session:
        """
        创建配置好的requests会话

        Returns:
            requests.Session: 配置好的会话对象
        """
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 设置默认请求头
        session.headers.update(
            {
                "User-Agent": "iFinance/1.0.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: HTTP方法 (GET, POST, etc.)
            endpoint: API端点
            params: URL参数
            data: 请求体数据
            headers: 额外的请求头

        Returns:
            Dict[str, Any]: API响应数据

        Raises:
            NetworkError: 网络连接错误
            APIError: API调用错误
            APIRateLimitError: API频率限制错误
            APIAuthenticationError: API认证错误
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        self.logger.debug(f"Making {method} request to {url} with params: {params}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.timeout,
            )

            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise NetworkError(f"Request timeout after {self.timeout} seconds", e)

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise NetworkError(f"Failed to connect to {url}", e)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise NetworkError(f"Request failed: {str(e)}", e)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理API响应

        Args:
            response: requests响应对象

        Returns:
            Dict[str, Any]: 解析后的响应数据

        Raises:
            APIError: API调用错误
            APIRateLimitError: API频率限制错误
            APIAuthenticationError: API认证错误
        """
        self.logger.debug(f"Response status: {response.status_code}")

        # 检查HTTP状态码
        if response.status_code == 401:
            raise APIAuthenticationError("Invalid API key or authentication failed")

        if response.status_code == 429:
            raise APIRateLimitError("API rate limit exceeded")

        if not response.ok:
            raise APIError(
                f"API request failed with status {response.status_code}",
                status_code=response.status_code,
            )

        # 解析JSON响应
        try:
            data = response.json()
        except ValueError as e:
            raise APIError(f"Failed to parse JSON response: {str(e)}")

        # 检查API特定的错误信息
        self._check_api_errors(data)

        return data

    @abstractmethod
    def _check_api_errors(self, data: Dict[str, Any]) -> None:
        """
        检查API特定的错误信息

        Args:
            data: API响应数据

        Raises:
            APIError: 当检测到API错误时
        """
        pass

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送GET请求

        Args:
            endpoint: API端点
            params: URL参数

        Returns:
            Dict[str, Any]: API响应数据
        """
        return self._make_request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送POST请求

        Args:
            endpoint: API端点
            data: 请求体数据

        Returns:
            Dict[str, Any]: API响应数据
        """
        return self._make_request("POST", endpoint, data=data)

    def close(self) -> None:
        """
        关闭会话
        """
        if hasattr(self, "session"):
            self.session.close()
            self.logger.debug("API client session closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
