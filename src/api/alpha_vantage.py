# Alpha Vantage API客户端
# 实现Alpha Vantage API的具体调用逻辑

from typing import Any, Dict, List, Optional

from .base import BaseAPIClient
from ..utils.config import config
from ..utils.exceptions import (
    APIError,
    APIRateLimitError,
    APIAuthenticationError,
    ConfigurationError
)


class AlphaVantageClient(BaseAPIClient):
    """
    Alpha Vantage API客户端
    
    提供股票搜索和OHLCV数据查询功能
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化Alpha Vantage客户端
        
        Args:
            api_key: API密钥，如果为None则从配置中获取
            base_url: API基础URL，如果为None则使用默认值
        
        Raises:
            ConfigurationError: 当API密钥未配置时
        """
        self.api_key = api_key or config.get('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ConfigurationError(
                "Alpha Vantage API key is required. "
                "Please set ALPHA_VANTAGE_API_KEY in your environment variables."
            )
        
        base_url = base_url or config.get(
            'ALPHA_VANTAGE_BASE_URL',
            'https://www.alphavantage.co/query'
        )
        
        super().__init__(base_url)
        self.logger.info("Alpha Vantage client initialized successfully")
    
    def _check_api_errors(self, data: Dict[str, Any]) -> None:
        """
        检查Alpha Vantage API特定的错误信息
        
        Args:
            data: API响应数据
        
        Raises:
            APIError: 当检测到API错误时
            APIRateLimitError: 当检测到频率限制时
            APIAuthenticationError: 当检测到认证错误时
        """
        # 检查错误消息
        if 'Error Message' in data:
            error_msg = data['Error Message']
            self.logger.error(f"Alpha Vantage API error: {error_msg}")
            
            if 'Invalid API call' in error_msg:
                raise APIAuthenticationError(f"Invalid API call: {error_msg}")
            else:
                raise APIError(f"Alpha Vantage API error: {error_msg}")
        
        # 检查频率限制
        if 'Note' in data:
            note = data['Note']
            if 'call frequency' in note.lower() or 'rate limit' in note.lower():
                self.logger.warning(f"Alpha Vantage rate limit warning: {note}")
                raise APIRateLimitError(f"Rate limit exceeded: {note}")
    
    def _add_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        向请求参数中添加API密钥
        
        Args:
            params: 原始请求参数
        
        Returns:
            Dict[str, Any]: 包含API密钥的请求参数
        """
        params = params.copy() if params else {}
        params['apikey'] = self.api_key
        return params
    
    def search_symbols(self, keywords: str) -> List[Dict[str, str]]:
        """
        搜索股票代码
        
        Args:
            keywords: 搜索关键词（股票代码或公司名称）
        
        Returns:
            List[Dict[str, str]]: 搜索结果列表，每个元素包含股票信息
        
        Raises:
            APIError: 当API调用失败时
        """
        if not keywords or not keywords.strip():
            return []
        
        params = self._add_api_key({
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords.strip()
        })
        
        self.logger.info(f"Searching symbols for keywords: {keywords}")
        
        try:
            response = self.get('', params=params)
            
            # 提取搜索结果
            best_matches = response.get('bestMatches', [])
            
            # 格式化结果
            results = []
            for match in best_matches:
                result = {
                    'symbol': match.get('1. symbol', ''),
                    'name': match.get('2. name', ''),
                    'type': match.get('3. type', ''),
                    'region': match.get('4. region', ''),
                    'market_open': match.get('5. marketOpen', ''),
                    'market_close': match.get('6. marketClose', ''),
                    'timezone': match.get('7. timezone', ''),
                    'currency': match.get('8. currency', ''),
                    'match_score': match.get('9. matchScore', '0')
                }
                results.append(result)
            
            self.logger.info(f"Found {len(results)} symbol matches for '{keywords}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search symbols for '{keywords}': {str(e)}")
            raise
    
    def get_daily_data(
        self,
        symbol: str,
        output_size: str = 'compact'
    ) -> Dict[str, Any]:
        """
        获取股票的日线OHLCV数据
        
        Args:
            symbol: 股票代码
            output_size: 输出大小，'compact'（最近100个交易日）或'full'（完整历史数据）
        
        Returns:
            Dict[str, Any]: 包含元数据和时间序列数据的字典
        
        Raises:
            APIError: 当API调用失败时
        """
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        if output_size not in ['compact', 'full']:
            raise ValueError("output_size must be 'compact' or 'full'")
        
        params = self._add_api_key({
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol.strip().upper(),
            'outputsize': output_size
        })
        
        self.logger.info(f"Getting daily data for symbol: {symbol} (output_size: {output_size})")
        
        try:
            response = self.get('', params=params)
            
            # 检查响应结构
            if 'Time Series (Daily)' not in response:
                if 'Meta Data' not in response:
                    raise APIError(f"Invalid response format for symbol '{symbol}'")
                else:
                    # 可能是无效的股票代码
                    raise APIError(f"No daily data found for symbol '{symbol}'")
            
            # 提取元数据和时间序列数据
            meta_data = response.get('Meta Data', {})
            time_series = response.get('Time Series (Daily)', {})
            
            # 格式化元数据
            formatted_meta = {
                'information': meta_data.get('1. Information', ''),
                'symbol': meta_data.get('2. Symbol', ''),
                'last_refreshed': meta_data.get('3. Last Refreshed', ''),
                'output_size': meta_data.get('4. Output Size', ''),
                'time_zone': meta_data.get('5. Time Zone', '')
            }
            
            # 格式化时间序列数据
            formatted_data = {}
            for date, values in time_series.items():
                formatted_data[date] = {
                    'open': float(values.get('1. open', 0)),
                    'high': float(values.get('2. high', 0)),
                    'low': float(values.get('3. low', 0)),
                    'close': float(values.get('4. close', 0)),
                    'volume': int(values.get('5. volume', 0))
                }
            
            result = {
                'meta_data': formatted_meta,
                'time_series': formatted_data
            }
            
            self.logger.info(
                f"Successfully retrieved {len(formatted_data)} days of data for '{symbol}'"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get daily data for '{symbol}': {str(e)}")
            raise
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票的实时报价信息
        
        Args:
            symbol: 股票代码
        
        Returns:
            Dict[str, Any]: 股票报价信息
        
        Raises:
            APIError: 当API调用失败时
        """
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        params = self._add_api_key({
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol.strip().upper()
        })
        
        self.logger.info(f"Getting quote for symbol: {symbol}")
        
        try:
            response = self.get('', params=params)
            
            # 检查响应结构
            if 'Global Quote' not in response:
                raise APIError(f"Invalid response format for symbol '{symbol}'")
            
            quote_data = response['Global Quote']
            
            # 格式化报价数据
            formatted_quote = {
                'symbol': quote_data.get('01. symbol', ''),
                'open': float(quote_data.get('02. open', 0)),
                'high': float(quote_data.get('03. high', 0)),
                'low': float(quote_data.get('04. low', 0)),
                'price': float(quote_data.get('05. price', 0)),
                'volume': int(quote_data.get('06. volume', 0)),
                'latest_trading_day': quote_data.get('07. latest trading day', ''),
                'previous_close': float(quote_data.get('08. previous close', 0)),
                'change': float(quote_data.get('09. change', 0)),
                'change_percent': quote_data.get('10. change percent', '0%')
            }
            
            self.logger.info(f"Successfully retrieved quote for '{symbol}'")
            return formatted_quote
            
        except Exception as e:
            self.logger.error(f"Failed to get quote for '{symbol}': {str(e)}")
            raise