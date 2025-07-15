# API 参考文档

## Alpha Vantage API 使用说明

### 基础信息

- **官方文档**: [https://www.alphavantage.co/documentation/](https://www.alphavantage.co/documentation/)
- **API Key**: 在 `.env` 文件中配置
- **基础URL**: `https://www.alphavantage.co/query`

### 使用的API端点

#### 1. 股票搜索 (SYMBOL_SEARCH)

**用途**: 根据关键词搜索股票代码和公司名称

**请求参数**:
- `function`: SYMBOL_SEARCH
- `keywords`: 搜索关键词
- `apikey`: API密钥

**示例请求**:
```
https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=AAPL&apikey=YOUR_API_KEY
```

**响应格式**:
```json
{
    "bestMatches": [
        {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc.",
            "3. type": "Equity",
            "4. region": "United States",
            "5. marketOpen": "09:30",
            "6. marketClose": "16:00",
            "7. timezone": "UTC-04",
            "8. currency": "USD",
            "9. matchScore": "1.0000"
        }
    ]
}
```

#### 2. 日线数据 (TIME_SERIES_DAILY)

**用途**: 获取股票的日线OHLCV数据

**请求参数**:
- `function`: TIME_SERIES_DAILY
- `symbol`: 股票代码
- `apikey`: API密钥
- `outputsize`: compact (最近100个交易日) 或 full (完整历史数据)

**示例请求**:
```
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=YOUR_API_KEY
```

**响应格式**:
```json
{
    "Meta Data": {
        "1. Information": "Daily Prices (open, high, low, close) and Volumes",
        "2. Symbol": "AAPL",
        "3. Last Refreshed": "2023-12-01",
        "4. Output Size": "Compact",
        "5. Time Zone": "US/Eastern"
    },
    "Time Series (Daily)": {
        "2023-12-01": {
            "1. open": "189.84",
            "2. high": "190.32",
            "3. low": "188.19",
            "4. close": "189.95",
            "5. volume": "48744366"
        }
    }
}
```

### API限制

- **免费版本**: 每天25次请求
- **请求频率**: 建议在请求之间添加适当的延迟
- **错误处理**: 需要处理API限流、网络错误等异常情况
- **升级选项**: 如需更多请求次数，可考虑升级到付费版本

### 错误响应

当API调用失败时，可能返回以下错误信息：

```json
{
    "Error Message": "Invalid API call. Please retry or visit the documentation..."
}
```

或

```json
{
    "Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."
}
```