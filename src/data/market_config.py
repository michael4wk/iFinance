# 市场配置模块
# 管理不同股票市场的时区、交易时间等信息

from datetime import time
from typing import Any, Dict, Optional

import pytz


class MarketConfig:
    """
    市场配置类

    管理不同股票市场的交易时间、时区、节假日等信息
    """

    # 主要市场配置
    MARKET_CONFIGS = {
        # 美国市场
        "US": {
            "timezone": "America/New_York",
            "market_open": time(9, 30),
            "market_close": time(16, 0),
            "currency": "USD",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "美国市场",
        },
        # 中国A股市场
        "CN": {
            "timezone": "Asia/Shanghai",
            "market_open": time(9, 30),
            "market_close": time(15, 0),
            "currency": "CNY",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "中国A股市场",
        },
        # 香港市场
        "HK": {
            "timezone": "Asia/Hong_Kong",
            "market_open": time(9, 30),
            "market_close": time(16, 0),
            "currency": "HKD",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "香港市场",
        },
        # 英国市场
        "GB": {
            "timezone": "Europe/London",
            "market_open": time(8, 0),
            "market_close": time(16, 30),
            "currency": "GBP",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "英国市场",
        },
        # 德国市场
        "DE": {
            "timezone": "Europe/Berlin",
            "market_open": time(9, 0),
            "market_close": time(17, 30),
            "currency": "EUR",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "德国市场",
        },
        # 日本市场
        "JP": {
            "timezone": "Asia/Tokyo",
            "market_open": time(9, 0),
            "market_close": time(15, 0),
            "currency": "JPY",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "日本市场",
        },
        # 韩国市场
        "KR": {
            "timezone": "Asia/Seoul",
            "market_open": time(9, 0),
            "market_close": time(15, 30),
            "currency": "KRW",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "韩国市场",
        },
        # 澳大利亚市场
        "AU": {
            "timezone": "Australia/Sydney",
            "market_open": time(10, 0),
            "market_close": time(16, 0),
            "currency": "AUD",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "澳大利亚市场",
        },
        # 加拿大市场
        "CA": {
            "timezone": "America/Toronto",
            "market_open": time(9, 30),
            "market_close": time(16, 0),
            "currency": "CAD",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "加拿大市场",
        },
        # 印度市场
        "IN": {
            "timezone": "Asia/Kolkata",
            "market_open": time(9, 15),
            "market_close": time(15, 30),
            "currency": "INR",
            "weekend_days": [5, 6],  # 周六、周日
            "name": "印度市场",
        },
    }

    @classmethod
    def get_market_config(cls, region: str) -> Optional[Dict[str, Any]]:
        """
        根据地区代码获取市场配置

        Args:
            region: 地区代码（如 'United States', 'China', 'Hong Kong'等）

        Returns:
            Optional[Dict[str, Any]]: 市场配置信息，如果未找到则返回None
        """
        # 地区名称到市场代码的映射
        region_mapping = {
            # Alpha Vantage API 返回的完整地区名称
            "United States": "US",
            "China": "CN",
            "Hong Kong": "HK",
            "United Kingdom": "GB",
            "Germany": "DE",
            "Japan": "JP",
            "South Korea": "KR",
            "Australia": "AU",
            "Canada": "CA",
            "India": "IN",
            "France": "FR",
            "Italy": "IT",
            "Spain": "ES",
            "Netherlands": "NL",
            "Switzerland": "CH",
            "Sweden": "SE",
            "Norway": "NO",
            "Denmark": "DK",
            "Finland": "FI",
            "Belgium": "BE",
            "Austria": "AT",
            "Brazil": "BR",
            "Mexico": "MX",
            "Russia": "RU",
            "Singapore": "SG",
            "Thailand": "TH",
            "Malaysia": "MY",
            "Indonesia": "ID",
            "Philippines": "PH",
            "Vietnam": "VN",
            "Taiwan": "TW",
            "New Zealand": "NZ",
            "South Africa": "ZA",
            "Israel": "IL",
            "Turkey": "TR",
            "Poland": "PL",
            "Czech Republic": "CZ",
            "Hungary": "HU",
            # 简写形式的映射
            "US": "US",
            "CN": "CN",
            "HK": "HK",
            "GB": "GB",
            "UK": "GB",  # 英国的另一种简写
            "DE": "DE",
            "JP": "JP",
            "KR": "KR",
            "AU": "AU",
            "CA": "CA",
            "IN": "IN",
            "FR": "FR",
            "IT": "IT",
            "ES": "ES",
            "NL": "NL",
            "CH": "CH",
            "SE": "SE",
            "NO": "NO",
            "DK": "DK",
            "FI": "FI",
            "BE": "BE",
            "AT": "AT",
            "BR": "BR",
            "MX": "MX",
            "RU": "RU",
            "SG": "SG",
            "TH": "TH",
            "MY": "MY",
            "ID": "ID",
            "PH": "PH",
            "VN": "VN",
            "TW": "TW",
            "NZ": "NZ",
            "ZA": "ZA",
            "IL": "IL",
            "TR": "TR",
            "PL": "PL",
            "CZ": "CZ",
            "HU": "HU",
        }

        market_code = region_mapping.get(region)
        if market_code:
            return cls.MARKET_CONFIGS.get(market_code)

        return None

    @classmethod
    def parse_timezone_from_api(cls, timezone_str: str) -> Optional[str]:
        """
        解析Alpha Vantage API返回的时区字符串

        Args:
            timezone_str: API返回的时区字符串（如 'UTC+08', 'UTC-05'）

        Returns:
            Optional[str]: 标准时区名称，如果无法解析则返回None
        """
        if not timezone_str or not timezone_str.startswith("UTC"):
            return None

        try:
            # 提取偏移量
            offset_str = timezone_str[3:]  # 去掉"UTC"前缀

            if offset_str.startswith("+"):
                offset_hours = int(offset_str[1:])
            elif offset_str.startswith("-"):
                offset_hours = -int(offset_str[1:])
            else:
                offset_hours = int(offset_str)

            # 根据偏移量推断可能的时区
            timezone_mapping = {
                -5: "America/New_York",  # UTC-5 (EST)
                -4: "America/New_York",  # UTC-4 (EDT)
                0: "Europe/London",  # UTC+0 (GMT)
                1: "Europe/Berlin",  # UTC+1 (CET)
                8: "Asia/Shanghai",  # UTC+8 (CST)
                9: "Asia/Tokyo",  # UTC+9 (JST)
                -8: "America/Los_Angeles",  # UTC-8 (PST)
                -7: "America/Los_Angeles",  # UTC-7 (PDT)
                5.5: "Asia/Kolkata",  # UTC+5:30 (IST)
                10: "Australia/Sydney",  # UTC+10 (AEST)
                11: "Australia/Sydney",  # UTC+11 (AEDT)
            }

            return timezone_mapping.get(offset_hours)

        except (ValueError, IndexError):
            return None

    @classmethod
    def get_timezone_object(cls, timezone_str: str) -> pytz.BaseTzInfo:
        """
        获取时区对象

        Args:
            timezone_str: 时区字符串或API时区格式

        Returns:
            pytz.BaseTzInfo: 时区对象
        """
        # 首先尝试解析API格式的时区
        if timezone_str.startswith("UTC"):
            parsed_tz = cls.parse_timezone_from_api(timezone_str)
            if parsed_tz:
                return pytz.timezone(parsed_tz)

            # 如果无法解析，创建固定偏移时区
            try:
                offset_str = timezone_str[3:]
                if offset_str.startswith("+"):
                    offset_hours = int(offset_str[1:])
                elif offset_str.startswith("-"):
                    offset_hours = -int(offset_str[1:])
                else:
                    offset_hours = int(offset_str)

                return pytz.FixedOffset(offset_hours * 60)
            except (ValueError, IndexError):
                # 默认返回UTC
                return pytz.UTC

        # 尝试直接解析为标准时区名称
        try:
            return pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            # 默认返回UTC
            return pytz.UTC

    @classmethod
    def get_all_markets(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有市场配置

        Returns:
            Dict[str, Dict[str, Any]]: 所有市场配置
        """
        return cls.MARKET_CONFIGS.copy()
