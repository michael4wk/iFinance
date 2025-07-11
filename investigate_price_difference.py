#!/usr/bin/env python3
"""
深入调查JD股票价格差异的原因
对比不同数据源和可能的解决方案
"""

import os
import sys
import requests
from datetime import datetime, timedelta
import json

# 添加项目路径
sys.path.append('/Users/michael/Documents/Code/Trae/iFinance/src')

def get_alpha_vantage_api_key():
    """获取Alpha Vantage API密钥"""
    try:
        with open('/Users/michael/Documents/Code/Trae/iFinance/.env', 'r') as f:
            for line in f:
                if line.startswith('ALPHA_VANTAGE_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    
    # 从环境变量获取
    return os.getenv('ALPHA_VANTAGE_API_KEY')

def test_intraday_adjusted_data(symbol, date_str, api_key):
    """测试intraday API的adjusted参数"""
    print(f"\n3. 测试TIME_SERIES_INTRADAY的adjusted参数...")
    
    # 尝试获取指定日期的intraday数据（adjusted=true）
    url_adjusted = f"https://www.alphavantage.co/query"
    params_adjusted = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '60min',  # 1小时间隔
        'adjusted': 'true',
        'outputsize': 'full',
        'apikey': api_key
    }
    
    try:
        response = requests.get(url_adjusted, params=params_adjusted, timeout=30)
        data = response.json()
        
        if 'Time Series (60min)' in data:
            time_series = data['Time Series (60min)']
            print(f"   获取到 {len(time_series)} 条intraday数据（adjusted=true）")
            
            # 查找指定日期的数据
            target_date_data = []
            for timestamp, values in time_series.items():
                if timestamp.startswith(date_str):
                    target_date_data.append((timestamp, values))
            
            if target_date_data:
                print(f"   找到 {len(target_date_data)} 条 {date_str} 的intraday数据:")
                # 显示开盘和收盘数据
                target_date_data.sort()  # 按时间排序
                first_data = target_date_data[0][1]
                last_data = target_date_data[-1][1]
                
                print(f"     开盘时段: {target_date_data[0][0]}")
                print(f"       开盘价: ${float(first_data['1. open']):.3f}")
                print(f"     收盘时段: {target_date_data[-1][0]}")
                print(f"       收盘价: ${float(last_data['4. close']):.3f}")
                
                # 计算当日的最高和最低价
                highs = [float(item[1]['2. high']) for item in target_date_data]
                lows = [float(item[1]['3. low']) for item in target_date_data]
                print(f"     当日最高价: ${max(highs):.3f}")
                print(f"     当日最低价: ${min(lows):.3f}")
            else:
                print(f"   未找到 {date_str} 的数据")
        else:
            print(f"   Intraday API调用失败")
            if 'Information' in data:
                print(f"   信息: {data['Information']}")
            if 'Error Message' in data:
                print(f"   错误: {data['Error Message']}")
    except Exception as e:
        print(f"   Intraday API调用异常: {e}")

def analyze_price_difference():
    """分析价格差异的可能原因"""
    print("\n" + "="*80)
    print("JD股票价格差异深度分析")
    print("="*80)
    
    symbol = "JD"
    target_date = "2025-01-08"
    expected_data = {
        'open': 33.629,
        'high': 33.862,
        'low': 33.313,
        'close': 33.726
    }
    
    api_key = get_alpha_vantage_api_key()
    if not api_key:
        print("错误: 无法获取Alpha Vantage API密钥")
        return
    
    print(f"\n目标股票: {symbol}")
    print(f"目标日期: {target_date}")
    print(f"期望数据: Open=${expected_data['open']}, High=${expected_data['high']}, Low=${expected_data['low']}, Close=${expected_data['close']}")
    
    # 1. 重新确认TIME_SERIES_DAILY数据
    print(f"\n1. 重新确认TIME_SERIES_DAILY数据...")
    url_daily = f"https://www.alphavantage.co/query"
    params_daily = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'full',
        'apikey': api_key
    }
    
    time_series = None
    try:
        response = requests.get(url_daily, params=params_daily, timeout=30)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            if target_date in time_series:
                daily_data = time_series[target_date]
                print(f"   TIME_SERIES_DAILY数据:")
                print(f"     开盘价: ${float(daily_data['1. open']):.3f}")
                print(f"     最高价: ${float(daily_data['2. high']):.3f}")
                print(f"     最低价: ${float(daily_data['3. low']):.3f}")
                print(f"     收盘价: ${float(daily_data['4. close']):.3f}")
                print(f"     成交量: {int(float(daily_data['5. volume'])):,}")
                
                # 计算与期望数据的差异
                open_diff = float(daily_data['1. open']) - expected_data['open']
                high_diff = float(daily_data['2. high']) - expected_data['high']
                low_diff = float(daily_data['3. low']) - expected_data['low']
                close_diff = float(daily_data['4. close']) - expected_data['close']
                
                print(f"\n   与期望数据的差异:")
                print(f"     开盘价差异: ${open_diff:.3f}")
                print(f"     最高价差异: ${high_diff:.3f}")
                print(f"     最低价差异: ${low_diff:.3f}")
                print(f"     收盘价差异: ${close_diff:.3f}")
                
                # 分析差异模式
                avg_diff = (open_diff + high_diff + low_diff + close_diff) / 4
                print(f"     平均差异: ${avg_diff:.3f}")
                
                if abs(avg_diff - 0.99) < 0.02:  # 差异接近0.99
                    print(f"     ⚠️  差异模式: 所有价格都比期望高约$0.99，可能是数据源差异")
            else:
                print(f"   未找到 {target_date} 的数据")
    except Exception as e:
        print(f"   Daily API调用异常: {e}")
    
    # 2. 测试其他日期的数据一致性
    print(f"\n2. 测试其他日期的数据一致性...")
    if time_series:
        test_dates = ["2025-01-07", "2025-01-06", "2025-01-03"]
        
        for test_date in test_dates:
            if test_date in time_series:
                test_data = time_series[test_date]
                print(f"   {test_date}: Open=${float(test_data['1. open']):.3f}, Close=${float(test_data['4. close']):.3f}")
    else:
        print(f"   无法获取历史数据进行对比")
    
    # 3. 测试intraday数据
    test_intraday_adjusted_data(symbol, target_date, api_key)
    
    # 4. 分析可能的原因
    print(f"\n4. 可能原因分析:")
    print(f"   📊 数据源差异:")
    print(f"      - Alpha Vantage使用原始交易价格（as-traded prices）")
    print(f"      - 您的交易软件可能使用调整后价格或不同的数据提供商")
    print(f"      - 不同数据源的价格可能因为数据处理方式不同而有差异")
    
    print(f"\n   🕐 时区和交易时间:")
    print(f"      - Alpha Vantage使用美国东部时间")
    print(f"      - 您的交易软件可能使用不同时区")
    print(f"      - 开盘/收盘时间定义可能不同")
    
    print(f"\n   💰 价格类型:")
    print(f"      - Alpha Vantage TIME_SERIES_DAILY返回原始价格")
    print(f"      - 交易软件可能显示调整后价格（考虑分红、拆股等）")
    print(f"      - 约$0.99的固定差异可能表明存在某种调整")
    
    print(f"\n   🔧 建议解决方案:")
    print(f"      1. 在应用中添加数据源说明")
    print(f"      2. 提供多个数据源选项")
    print(f"      3. 添加价格类型选择（原始/调整后）")
    print(f"      4. 考虑使用其他免费API作为备选")
    print(f"      5. 在UI中显示数据免责声明")

if __name__ == "__main__":
    analyze_price_difference()