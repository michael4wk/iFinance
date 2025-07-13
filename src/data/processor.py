# 数据处理模块
# 负责处理和转换从API获取的金融数据

from typing import Any, Dict, List, Optional

import pandas as pd

from ..utils.exceptions import DataProcessingError
from ..utils.logger import get_logger


class DataProcessor:
    """
    数据处理器

    负责处理和转换金融数据，包括格式化、计算技术指标等
    """

    def __init__(self):
        """
        初始化数据处理器
        """
        self.logger = get_logger(__name__)
        self.logger.info("DataProcessor initialized")

    def process_symbol_search_results(
        self, search_results: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        处理股票搜索结果

        Args:
            search_results: 原始搜索结果

        Returns:
            List[Dict[str, str]]: 处理后的搜索结果
        """
        if not search_results:
            return []

        try:
            processed_results = []

            for result in search_results:
                # 验证必需字段
                if not result.get("symbol") or not result.get("name"):
                    continue

                # 清理和格式化数据
                processed_result = {
                    "symbol": result["symbol"].strip().upper(),
                    "name": result["name"].strip(),
                    "type": result.get("type", "").strip(),
                    "region": result.get("region", "").strip(),
                    "market_open": result.get("market_open", "").strip(),
                    "market_close": result.get("market_close", "").strip(),
                    "timezone": result.get("timezone", "").strip(),
                    "currency": result.get("currency", "").strip(),
                    "match_score": float(result.get("match_score", 0)),
                }

                # 添加货币符号
                processed_result["currency_symbol"] = self.get_currency_symbol(
                    processed_result["currency"]
                )

                # 添加市场状态信息
                processed_result["market_status"] = self.get_market_status(
                    processed_result["market_open"],
                    processed_result["market_close"],
                    processed_result["timezone"],
                    processed_result["region"],  # 传入地区信息
                )

                # 添加显示标签
                processed_result["display_label"] = (
                    f"{processed_result['symbol']} - {processed_result['name']}"
                )

                processed_results.append(processed_result)

            # 按匹配分数排序
            processed_results.sort(key=lambda x: x["match_score"], reverse=True)

            self.logger.info(
                f"Processed {len(processed_results)} symbol search results"
            )
            return processed_results

        except Exception as e:
            self.logger.error(f"Failed to process symbol search results: {str(e)}")
            raise DataProcessingError(f"Failed to process search results: {str(e)}")

    def get_currency_symbol(self, currency_code: str) -> str:
        """
        根据货币代码获取货币符号

        Args:
            currency_code: 货币代码 (如 'USD', 'CNY', 'EUR')

        Returns:
            str: 货币符号
        """
        currency_symbols = {
            "USD": "$",
            "CNY": "¥",
            "EUR": "€",
            "GBP": "£",
            "GBX": "p",  # 英国便士
            "JPY": "¥",
            "KRW": "₩",
            "HKD": "HK$",
            "CAD": "C$",
            "AUD": "A$",
            "SGD": "S$",
            "INR": "₹",
            "BRL": "R$",
            "RUB": "₽",
            "CHF": "CHF",
            "SEK": "kr",
            "NOK": "kr",
            "DKK": "kr",
            "PLN": "zł",
            "CZK": "Kč",
            "HUF": "Ft",
            "TRY": "₺",
            "ZAR": "R",
            "MXN": "$",
            "THB": "฿",
            "MYR": "RM",
            "IDR": "Rp",
            "PHP": "₱",
            "VND": "₫",
            "TWD": "NT$",
            "NZD": "NZ$",
        }
        return currency_symbols.get(currency_code.upper(), currency_code)

    def get_market_status(
        self, market_open: str, market_close: str, timezone: str, region: str = ""
    ) -> Dict[str, str]:
        """
        根据交易时间和地区判断市场状态

        Args:
            market_open: 开市时间 (格式: "HH:MM")
            market_close: 闭市时间 (格式: "HH:MM")
            timezone: 时区 (格式: "UTC+08" 或 "UTC-05")
            region: 地区信息（可选，用于获取更准确的市场配置）

        Returns:
            Dict[str, str]: 包含市场状态和相关信息
        """
        try:
            from datetime import datetime, time, timedelta

            import pytz

            from .market_config import MarketConfig

            # 尝试从市场配置获取更准确的信息
            market_config = None
            if region:
                market_config = MarketConfig.get_market_config(region)

            # 获取时区对象
            if market_config:
                # 使用市场配置中的时区
                market_tz = pytz.timezone(market_config["timezone"])
                # 使用市场配置中的交易时间
                open_time = market_config["market_open"]
                close_time = market_config["market_close"]
                weekend_days = market_config.get("weekend_days", [5, 6])
                market_name = market_config.get("name", "市场")
            else:
                # 使用API提供的信息
                market_tz = MarketConfig.get_timezone_object(timezone)
                # 解析API提供的交易时间
                try:
                    open_hour, open_minute = map(int, market_open.split(":"))
                    close_hour, close_minute = map(int, market_close.split(":"))
                    open_time = time(open_hour, open_minute)
                    close_time = time(close_hour, close_minute)
                except (ValueError, AttributeError):
                    # 如果解析失败，使用默认时间
                    open_time = time(9, 30)
                    close_time = time(15, 0)

                weekend_days = [5, 6]  # 默认周六、周日
                market_name = "市场"

            # 获取当前市场时间
            utc_now = datetime.now(pytz.UTC)
            market_now = utc_now.astimezone(market_tz)

            # 创建今天的开市和闭市时间
            today = market_now.date()
            market_open_time = market_tz.localize(datetime.combine(today, open_time))
            market_close_time = market_tz.localize(datetime.combine(today, close_time))

            # 判断当前状态
            if market_now.weekday() in weekend_days:
                # 周末休市
                # 计算下一个工作日开市时间
                days_ahead = 0
                next_date = today
                while next_date.weekday() in weekend_days:
                    days_ahead += 1
                    next_date = today + timedelta(days=days_ahead)

                next_open = market_tz.localize(datetime.combine(next_date, open_time))
                time_diff = next_open - market_now

                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if days > 0:
                    if next_date.weekday() == 0:  # 下周一
                        next_event = (
                            f"距离下周一开市还有{days}天{hours}小时{minutes}分钟"
                        )
                    else:
                        next_event = (
                            f"距离下个交易日开市还有{days}天{hours}小时{minutes}分钟"
                        )
                else:
                    next_event = f"距离开市还有{hours}小时{minutes}分钟"

                return {
                    "status": "closed",
                    "status_text": f"{market_name}休市中（周末）",
                    "next_event": next_event,
                }

            elif market_now < market_open_time:
                # 开市前
                time_diff = market_open_time - market_now
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                return {
                    "status": "pre_market",
                    "status_text": f"{market_name}开市前",
                    "next_event": f"距离开市还有{hours}小时{minutes}分钟",
                }

            elif market_now <= market_close_time:
                # 交易时间内
                time_diff = market_close_time - market_now
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                return {
                    "status": "open",
                    "status_text": f"{market_name}开市中",
                    "next_event": f"距离闭市还有{hours}小时{minutes}分钟",
                }

            else:
                # 闭市后
                # 计算下一个交易日开市时间
                next_date = today + timedelta(days=1)

                # 跳过周末
                while next_date.weekday() in weekend_days:
                    next_date += timedelta(days=1)

                next_open = market_tz.localize(datetime.combine(next_date, open_time))
                time_diff = next_open - market_now

                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if days > 0:
                    if next_date.weekday() == 0:  # 下周一
                        next_event = (
                            f"距离下周一开市还有{days}天{hours}小时{minutes}分钟"
                        )
                    else:
                        next_event = (
                            f"距离下个交易日开市还有{days}天{hours}小时{minutes}分钟"
                        )
                else:
                    next_event = f"距离下个交易日开市还有{hours}小时{minutes}分钟"

                return {
                    "status": "closed",
                    "status_text": f"{market_name}闭市",
                    "next_event": next_event,
                }

        except Exception as e:
            self.logger.error(f"计算市场状态时出错: {str(e)}")
            return {"status": "unknown", "status_text": "状态未知", "next_event": ""}

    def process_daily_data(
        self, daily_data: Dict[str, Any], days_limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        处理日线OHLCV数据

        Args:
            daily_data: 原始日线数据
            days_limit: 限制返回的天数，None表示返回所有数据

        Returns:
            pd.DataFrame: 处理后的数据框

        Raises:
            DataProcessingError: 当数据处理失败时
        """
        try:
            if not daily_data or "time_series" not in daily_data:
                raise DataProcessingError("Invalid daily data format")

            time_series = daily_data["time_series"]
            if not time_series:
                raise DataProcessingError("Empty time series data")

            # 转换为DataFrame
            df = pd.DataFrame.from_dict(time_series, orient="index")

            # 确保索引为日期类型
            df.index = pd.to_datetime(df.index)
            df.index.name = "date"

            # 按日期排序（最新的在前）
            df = df.sort_index(ascending=False)

            # 限制天数
            if days_limit and days_limit > 0:
                df = df.head(days_limit)

            # 确保数据类型正确
            numeric_columns = ["open", "high", "low", "close", "volume"]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # 检查是否有无效数据
            if df.isnull().any().any():
                self.logger.warning("Found null values in daily data")
                df = df.dropna()

            # 添加计算字段
            df = self._add_calculated_fields(df)

            self.logger.info(f"Processed daily data: {len(df)} records")
            return df

        except Exception as e:
            self.logger.error(f"Failed to process daily data: {str(e)}")
            raise DataProcessingError(f"Failed to process daily data: {str(e)}")

    def _add_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加计算字段

        Args:
            df: 原始数据框（按降序排列，最新在前）

        Returns:
            pd.DataFrame: 包含计算字段的数据框
        """
        try:
            # 为了正确计算日变化，先转为升序排列
            df_asc = df.sort_index(ascending=True)

            # 在升序数据中计算日变化（当前日 - 前一交易日）
            df_asc["change"] = df_asc["close"].diff()  # diff() 等同于当前值减去前一个值
            df_asc["change_percent"] = (
                df_asc["change"] / df_asc["close"].shift(1) * 100
            ).round(2)

            # 价格范围（与排序无关）
            df_asc["range"] = df_asc["high"] - df_asc["low"]
            df_asc["range_percent"] = (df_asc["range"] / df_asc["close"] * 100).round(2)

            # 移动平均线（在升序数据中计算更直观）
            if len(df_asc) >= 5:
                df_asc["ma5"] = df_asc["close"].rolling(window=5).mean().round(2)

            if len(df_asc) >= 10:
                df_asc["ma10"] = df_asc["close"].rolling(window=10).mean().round(2)

            if len(df_asc) >= 20:
                df_asc["ma20"] = df_asc["close"].rolling(window=20).mean().round(2)

            # 转回降序排列（保持原有的显示顺序）
            df_result = df_asc.sort_index(ascending=False)

            self.logger.info("Successfully added calculated fields with correct logic")
            return df_result

        except Exception as e:
            self.logger.warning(f"Failed to add calculated fields: {str(e)}")
            return df

    def format_for_display(
        self, df: pd.DataFrame, format_numbers: bool = True
    ) -> List[Dict[str, Any]]:
        """
        格式化数据用于显示

        Args:
            df: 数据框
            format_numbers: 是否格式化数字

        Returns:
            List[Dict[str, Any]]: 格式化后的数据列表
        """
        try:
            if df.empty:
                return []

            # 重置索引以包含日期列
            display_df = df.reset_index()

            # 格式化日期
            display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")

            if format_numbers:
                # 格式化数字
                price_columns = ["open", "high", "low", "close"]
                for col in price_columns:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(
                            lambda x: f"{x:.2f}" if pd.notna(x) else "-"
                        )

                # 格式化成交量
                if "volume" in display_df.columns:
                    display_df["volume"] = display_df["volume"].apply(
                        lambda x: f"{x:,}" if pd.notna(x) else "-"
                    )

                # 格式化变化百分比
                if "change_percent" in display_df.columns:
                    display_df["change_percent"] = display_df["change_percent"].apply(
                        lambda x: f"{x:+.2f}%" if pd.notna(x) else "-"
                    )

            # 转换为字典列表
            result = display_df.to_dict("records")

            self.logger.info(f"Formatted {len(result)} records for display")
            return result

        except Exception as e:
            self.logger.error(f"Failed to format data for display: {str(e)}")
            raise DataProcessingError(f"Failed to format data: {str(e)}")

    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算数据的汇总统计信息

        Args:
            df: 数据框

        Returns:
            Dict[str, Any]: 汇总统计信息
        """
        try:
            if df.empty:
                return {}

            # 基础统计
            latest_data = df.iloc[0] if not df.empty else None

            stats = {
                "total_records": len(df),
                "date_range": {
                    "start": df.index.min().strftime("%Y-%m-%d"),
                    "end": df.index.max().strftime("%Y-%m-%d"),
                },
            }

            if latest_data is not None:
                stats["latest"] = {
                    "date": df.index[0].strftime("%Y-%m-%d"),
                    "close": float(latest_data["close"]),
                    "volume": int(latest_data["volume"]),
                    "change": float(latest_data.get("change", 0)),
                    "change_percent": float(latest_data.get("change_percent", 0)),
                }

            # 价格统计
            if "close" in df.columns:
                close_prices = df["close"].dropna()
                if not close_prices.empty:
                    stats["price_stats"] = {
                        "min": float(close_prices.min()),
                        "max": float(close_prices.max()),
                        "mean": float(close_prices.mean()),
                        "std": float(close_prices.std()),
                    }

            # 成交量统计
            if "volume" in df.columns:
                volumes = df["volume"].dropna()
                if not volumes.empty:
                    stats["volume_stats"] = {
                        "min": int(volumes.min()),
                        "max": int(volumes.max()),
                        "mean": int(volumes.mean()),
                        "total": int(volumes.sum()),
                    }

            self.logger.info("Generated summary statistics")
            return stats

        except Exception as e:
            self.logger.error(f"Failed to generate summary statistics: {str(e)}")
            return {}

    def filter_by_date_range(
        self,
        df: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        按日期范围过滤数据

        Args:
            df: 数据框
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 过滤后的数据框
        """
        try:
            if df.empty:
                return df

            filtered_df = df.copy()

            if start_date:
                start_dt = pd.to_datetime(start_date)
                filtered_df = filtered_df[filtered_df.index >= start_dt]

            if end_date:
                end_dt = pd.to_datetime(end_date)
                filtered_df = filtered_df[filtered_df.index <= end_dt]

            self.logger.info(
                f"Filtered data from {len(df)} to {len(filtered_df)} records"
            )
            return filtered_df

        except Exception as e:
            self.logger.error(f"Failed to filter data by date range: {str(e)}")
            raise DataProcessingError(f"Failed to filter data: {str(e)}")
