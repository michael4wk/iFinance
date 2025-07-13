# 数据验证模块
# 提供数据验证、清洗和格式化功能

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.exceptions import DataValidationError
from ..utils.logger import get_logger


class DataValidator:
    """
    数据验证器
    提供各种数据验证功能，确保数据的完整性和正确性
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.debug("DataValidator initialized")

    def validate_date_format(self, date_str: str, date_format: str = "%Y-%m-%d") -> str:
        """
        验证日期格式

        Args:
            date_str: 日期字符串
            date_format: 期望的日期格式

        Returns:
            str: 验证后的日期字符串

        Raises:
            DataValidationError: 当日期格式无效时
        """
        if not date_str:
            raise DataValidationError("Date string cannot be empty", field="date")

        try:
            # 尝试解析日期
            parsed_date = datetime.strptime(date_str, date_format)
            # 返回标准化的日期字符串
            return parsed_date.strftime(date_format)
        except ValueError as e:
            raise DataValidationError(
                f"Invalid date format. Expected {date_format}, "
                f"got '{date_str}'. Error: {str(e)}",
                field="date",
                value=date_str,
            )

    def validate_date_range(
        self, start_date: str, end_date: str, date_format: str = "%Y-%m-%d"
    ) -> tuple[str, str]:
        """
        验证日期范围

        Args:
            start_date: 开始日期字符串
            end_date: 结束日期字符串
            date_format: 日期格式

        Returns:
            tuple[str, str]: 验证后的开始和结束日期

        Raises:
            DataValidationError: 当日期范围无效时
        """
        # 验证单个日期格式
        validated_start = self.validate_date_format(start_date, date_format)
        validated_end = self.validate_date_format(end_date, date_format)

        # 解析日期进行比较
        start_dt = datetime.strptime(validated_start, date_format)
        end_dt = datetime.strptime(validated_end, date_format)

        # 检查日期范围逻辑
        if start_dt > end_dt:
            raise DataValidationError(
                f"Start date ({validated_start}) cannot be after "
                f"end date ({validated_end})",
                field="date_range",
                value={"start_date": validated_start, "end_date": validated_end},
            )

        # 检查是否为未来日期（可选验证）
        today = datetime.now().date()
        if end_dt.date() > today:
            self.logger.warning(
                f"End date ({validated_end}) is in the future. "
                f"This might not return any data."
            )

        self.logger.debug(
            f"Validated date range: {validated_start} to {validated_end}"
        )
        return validated_start, validated_end

    def validate_stock_symbol(self, symbol: str) -> str:
        """
        验证股票代码格式

        Args:
            symbol: 股票代码

        Returns:
            str: 清理后的股票代码（大写）

        Raises:
            DataValidationError: 当股票代码无效时
        """
        if not symbol:
            raise DataValidationError(
                "Stock symbol cannot be empty", field="symbol"
            )

        # 清理股票代码
        cleaned_symbol = symbol.strip().upper()

        if not cleaned_symbol:
            raise DataValidationError(
                "Stock symbol cannot be empty after cleaning", field="symbol"
            )

        # 基本格式验证（字母数字，可能包含点号）
        if not re.match(r"^[A-Z0-9.]+$", cleaned_symbol):
            raise DataValidationError(
                f"Invalid stock symbol format: '{cleaned_symbol}'. "
                f"Only letters, numbers, and dots are allowed.",
                field="symbol",
                value=cleaned_symbol,
            )

        # 长度检查
        if len(cleaned_symbol) > 10:
            raise DataValidationError(
                f"Stock symbol too long (max 10 characters): '{cleaned_symbol}'",
                field="symbol",
                value=cleaned_symbol,
            )

        self.logger.debug(f"Validated stock symbol: {cleaned_symbol}")
        return cleaned_symbol

    def validate_numeric_value(
        self,
        value: Any,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_zero: bool = True,
    ) -> float:
        """
        验证数值

        Args:
            value: 要验证的值
            field_name: 字段名称
            min_value: 最小值
            max_value: 最大值
            allow_zero: 是否允许零值

        Returns:
            float: 验证后的数值

        Raises:
            DataValidationError: 当数值无效时
        """
        if value is None or value == "":
            raise DataValidationError(f"{field_name} cannot be empty", field=field_name)

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            raise DataValidationError(
                f"{field_name} must be a valid number, got '{value}'",
                field=field_name,
                value=value,
            )

        # 检查是否为有效数字
        if (
            not isinstance(numeric_value, (int, float))
            or numeric_value != numeric_value
        ):  # NaN check
            raise DataValidationError(
                f"{field_name} must be a valid number", field=field_name, value=value
            )

        # 检查零值
        if not allow_zero and numeric_value == 0:
            raise DataValidationError(
                f"{field_name} cannot be zero", field=field_name, value=numeric_value
            )

        # 检查范围
        if min_value is not None and numeric_value < min_value:
            raise DataValidationError(
                f"{field_name} must be at least {min_value}, got {numeric_value}",
                field=field_name,
                value=numeric_value,
            )

        if max_value is not None and numeric_value > max_value:
            raise DataValidationError(
                f"{field_name} must be at most {max_value}, got {numeric_value}",
                field=field_name,
                value=numeric_value,
            )

        return numeric_value

    def validate_ohlcv_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证OHLCV数据的完整性和逻辑性

        Args:
            data: OHLCV数据字典

        Returns:
            Dict[str, Any]: 验证后的数据

        Raises:
            DataValidationError: 当数据无效时
        """
        required_fields = ["open", "high", "low", "close", "volume"]

        # 检查必需字段
        for field in required_fields:
            if field not in data:
                raise DataValidationError(
                    f"Missing required field: {field}", field=field
                )

        # 验证数值
        validated_data = {}

        for field in ["open", "high", "low", "close"]:
            validated_data[field] = self.validate_numeric_value(
                data[field], field, min_value=0, allow_zero=False
            )

        validated_data["volume"] = self.validate_numeric_value(
            data["volume"], "volume", min_value=0, allow_zero=True
        )

        # 验证OHLC逻辑关系
        open_price = validated_data["open"]
        high_price = validated_data["high"]
        low_price = validated_data["low"]
        close_price = validated_data["close"]

        # High应该是最高价
        if high_price < max(open_price, close_price, low_price):
            raise DataValidationError(
                f"High price ({high_price}) should be the highest among " f"OHLC values"
            )

        # Low应该是最低价
        if low_price > min(open_price, close_price, high_price):
            raise DataValidationError(
                f"Low price ({low_price}) should be the lowest among " f"OHLC values"
            )

        # 检查价格范围是否合理（防止异常数据）
        price_range = high_price - low_price
        avg_price = (high_price + low_price) / 2

        if avg_price > 0 and (price_range / avg_price) > 0.5:  # 50%的日内波动
            self.logger.warning(
                f"Unusually large price range detected: {price_range:.2f} "
                f"({price_range / avg_price * 100:.1f}% of average price)"
            )

        self.logger.debug("OHLCV data validation passed")
        return validated_data

    def validate_search_keywords(self, keywords: str) -> str:
        """
        验证搜索关键词

        Args:
            keywords: 搜索关键词

        Returns:
            str: 清理后的关键词

        Raises:
            DataValidationError: 当关键词无效时
        """
        if not keywords:
            raise DataValidationError(
                "Search keywords cannot be empty", field="keywords"
            )

        cleaned_keywords = keywords.strip()

        if not cleaned_keywords:
            raise DataValidationError(
                "Search keywords cannot be empty after cleaning", field="keywords"
            )

        # 长度检查
        if len(cleaned_keywords) > 100:
            raise DataValidationError(
                f"Search keywords too long (max 100 characters), "
                f"got {len(cleaned_keywords)}",
                field="keywords",
                value=cleaned_keywords,
            )

        # 检查是否包含有效字符
        if not re.search(r"[a-zA-Z0-9]", cleaned_keywords):
            raise DataValidationError(
                "Search keywords must contain at least one alphanumeric " "character",
                field="keywords",
                value=cleaned_keywords,
            )

        self.logger.debug(f"Validated search keywords: {cleaned_keywords}")
        return cleaned_keywords

    def validate_api_response(
        self, response: Dict[str, Any], expected_keys: List[str]
    ) -> None:
        """
        验证API响应的基本结构

        Args:
            response: API响应数据
            expected_keys: 期望的键列表

        Raises:
            DataValidationError: 当响应结构无效时
        """
        if not isinstance(response, dict):
            raise DataValidationError(
                f"API response must be a dictionary, got {type(response).__name__}"
            )

        missing_keys = [key for key in expected_keys if key not in response]
        if missing_keys:
            raise DataValidationError(
                f"API response missing required keys: {', '.join(missing_keys)}"
            )

        self.logger.debug("API response validation passed")
