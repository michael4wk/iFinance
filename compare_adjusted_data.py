#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比Alpha Vantage TIME_SERIES_DAILY和TIME_SERIES_DAILY_ADJUSTED的数据差异
验证JD股票2025-01-08的价格差异是否由于调整价格导致
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
from src.utils.config import config

def compare_adjusted_data():
    """
    对比TIME_SERIES_DAILY和TIME_SERIES_DAILY_ADJUSTED的数据
    """
    print("=" * 80)
    print("对比Alpha Vantage调整和未调整价格数据")
    print("=" * 80)
    
    # 用户期望的数据
    expected_data = {
        'open': 33.629,
        'high': 33.862,
        'low': 33.313,
        'close': 33.726
    }
    
    target_date = '2025-01-08'
    symbol = 'JD'
    
    print(f"\n目标股票: {symbol}")
    print(f"目标日期: {target_date}")
    print(f"期望数据: Open=${expected_data['open']:.3f}, High=${expected_data['high']:.3f}, Low=${expected_data['low']:.3f}, Close=${expected_data['close']:.3f}")
    
    # 获取API密钥
    api_key = config.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        print("错误: 未找到Alpha Vantage API密钥")
        return
    
    base_url = 'https://www.alphavantage.co/query'
    
    try:
        # 1. 获取TIME_SERIES_DAILY数据（当前应用使用的）
        print(f"\n1. 获取TIME_SERIES_DAILY数据（当前应用使用）...")
        
        params_daily = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': api_key
        }
        
        response_daily = requests.get(base_url, params=params_daily)
        data_daily = response_daily.json()
        
        if 'Time Series (Daily)' in data_daily:
            time_series_daily = data_daily['Time Series (Daily)']
            print(f"   TIME_SERIES_DAILY: 获取到 {len(time_series_daily)} 条数据")
            
            if target_date in time_series_daily:
                daily_data = time_series_daily[target_date]
                print(f"   找到 {target_date} 的数据:")
                print(f"     开盘价: ${float(daily_data['1. open']):.3f}")
                print(f"     最高价: ${float(daily_data['2. high']):.3f}")
                print(f"     最低价: ${float(daily_data['3. low']):.3f}")
                print(f"     收盘价: ${float(daily_data['4. close']):.3f}")
                print(f"     成交量: {int(daily_data['5. volume']):,}")
            else:
                print(f"   未找到 {target_date} 的数据")
                daily_data = None
        else:
            print(f"   TIME_SERIES_DAILY API调用失败")
            if 'Error Message' in data_daily:
                print(f"   错误信息: {data_daily['Error Message']}")
            daily_data = None
        
        # 2. 获取TIME_SERIES_DAILY_ADJUSTED数据
        print(f"\n2. 获取TIME_SERIES_DAILY_ADJUSTED数据（调整后价格）...")
        
        params_adjusted = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': api_key
        }
        
        response_adjusted = requests.get(base_url, params=params_adjusted)
        data_adjusted = response_adjusted.json()
        
        if 'Time Series (Daily)' in data_adjusted:
            time_series_adjusted = data_adjusted['Time Series (Daily)']
            print(f"   TIME_SERIES_DAILY_ADJUSTED: 获取到 {len(time_series_adjusted)} 条数据")
            
            if target_date in time_series_adjusted:
                adjusted_data = time_series_adjusted[target_date]
                print(f"   找到 {target_date} 的数据:")
                print(f"     开盘价: ${float(adjusted_data['1. open']):.3f}")
                print(f"     最高价: ${float(adjusted_data['2. high']):.3f}")
                print(f"     最低价: ${float(adjusted_data['3. low']):.3f}")
                print(f"     收盘价: ${float(adjusted_data['4. close']):.3f}")
                print(f"     调整收盘价: ${float(adjusted_data['5. adjusted close']):.3f}")
                print(f"     成交量: {int(adjusted_data['6. volume']):,}")
                print(f"     分红金额: ${float(adjusted_data['7. dividend amount']):.4f}")
                print(f"     拆股系数: {float(adjusted_data['8. split coefficient']):.4f}")
            else:
                print(f"   未找到 {target_date} 的数据")
                adjusted_data = None
        else:
            print(f"   TIME_SERIES_DAILY_ADJUSTED API调用失败")
            print(f"   响应状态码: {response_adjusted.status_code}")
            print(f"   响应内容: {data_adjusted}")
            if 'Error Message' in data_adjusted:
                print(f"   错误信息: {data_adjusted['Error Message']}")
            if 'Note' in data_adjusted:
                print(f"   注意事项: {data_adjusted['Note']}")
            adjusted_data = None
        
        # 3. 对比两个API的数据
        if daily_data and adjusted_data:
            print(f"\n3. 对比两个API的数据:")
            
            daily_open = float(daily_data['1. open'])
            daily_high = float(daily_data['2. high'])
            daily_low = float(daily_data['3. low'])
            daily_close = float(daily_data['4. close'])
            
            adjusted_open = float(adjusted_data['1. open'])
            adjusted_high = float(adjusted_data['2. high'])
            adjusted_low = float(adjusted_data['3. low'])
            adjusted_close = float(adjusted_data['4. close'])
            adjusted_close_adj = float(adjusted_data['5. adjusted close'])
            
            print(f"   开盘价: Daily=${daily_open:.3f}, Adjusted=${adjusted_open:.3f}, 差异=${abs(daily_open-adjusted_open):.3f}")
            print(f"   最高价: Daily=${daily_high:.3f}, Adjusted=${adjusted_high:.3f}, 差异=${abs(daily_high-adjusted_high):.3f}")
            print(f"   最低价: Daily=${daily_low:.3f}, Adjusted=${adjusted_low:.3f}, 差异=${abs(daily_low-adjusted_low):.3f}")
            print(f"   收盘价: Daily=${daily_close:.3f}, Adjusted=${adjusted_close:.3f}, 差异=${abs(daily_close-adjusted_close):.3f}")
            print(f"   调整收盘价: ${adjusted_close_adj:.3f}")
            
            # 检查是否相同
            same_data = (
                abs(daily_open - adjusted_open) < 0.001 and
                abs(daily_high - adjusted_high) < 0.001 and
                abs(daily_low - adjusted_low) < 0.001 and
                abs(daily_close - adjusted_close) < 0.001
            )
            
            if same_data:
                print(f"   ✅ 两个API返回的OHLC数据相同")
            else:
                print(f"   ❌ 两个API返回的OHLC数据不同")
        
        # 4. 对比期望数据
        print(f"\n4. 对比期望数据:")
        
        if daily_data:
            print(f"\n   TIME_SERIES_DAILY vs 期望数据:")
            daily_open = float(daily_data['1. open'])
            daily_high = float(daily_data['2. high'])
            daily_low = float(daily_data['3. low'])
            daily_close = float(daily_data['4. close'])
            
            daily_matches = [
                abs(daily_open - expected_data['open']) <= 0.01,
                abs(daily_high - expected_data['high']) <= 0.01,
                abs(daily_low - expected_data['low']) <= 0.01,
                abs(daily_close - expected_data['close']) <= 0.01
            ]
            
            print(f"     开盘价: API=${daily_open:.3f}, 期望=${expected_data['open']:.3f}, 差异=${abs(daily_open-expected_data['open']):.3f} {'✅' if daily_matches[0] else '❌'}")
            print(f"     最高价: API=${daily_high:.3f}, 期望=${expected_data['high']:.3f}, 差异=${abs(daily_high-expected_data['high']):.3f} {'✅' if daily_matches[1] else '❌'}")
            print(f"     最低价: API=${daily_low:.3f}, 期望=${expected_data['low']:.3f}, 差异=${abs(daily_low-expected_data['low']):.3f} {'✅' if daily_matches[2] else '❌'}")
            print(f"     收盘价: API=${daily_close:.3f}, 期望=${expected_data['close']:.3f}, 差异=${abs(daily_close-expected_data['close']):.3f} {'✅' if daily_matches[3] else '❌'}")
            
            if all(daily_matches):
                print(f"     结论: TIME_SERIES_DAILY数据与期望数据匹配 ✅")
            else:
                print(f"     结论: TIME_SERIES_DAILY数据与期望数据不匹配 ❌")
        
        if adjusted_data:
            print(f"\n   TIME_SERIES_DAILY_ADJUSTED vs 期望数据:")
            adjusted_open = float(adjusted_data['1. open'])
            adjusted_high = float(adjusted_data['2. high'])
            adjusted_low = float(adjusted_data['3. low'])
            adjusted_close = float(adjusted_data['4. close'])
            
            adjusted_matches = [
                abs(adjusted_open - expected_data['open']) <= 0.01,
                abs(adjusted_high - expected_data['high']) <= 0.01,
                abs(adjusted_low - expected_data['low']) <= 0.01,
                abs(adjusted_close - expected_data['close']) <= 0.01
            ]
            
            print(f"     开盘价: API=${adjusted_open:.3f}, 期望=${expected_data['open']:.3f}, 差异=${abs(adjusted_open-expected_data['open']):.3f} {'✅' if adjusted_matches[0] else '❌'}")
            print(f"     最高价: API=${adjusted_high:.3f}, 期望=${expected_data['high']:.3f}, 差异=${abs(adjusted_high-expected_data['high']):.3f} {'✅' if adjusted_matches[1] else '❌'}")
            print(f"     最低价: API=${adjusted_low:.3f}, 期望=${expected_data['low']:.3f}, 差异=${abs(adjusted_low-expected_data['low']):.3f} {'✅' if adjusted_matches[2] else '❌'}")
            print(f"     收盘价: API=${adjusted_close:.3f}, 期望=${expected_data['close']:.3f}, 差异=${abs(adjusted_close-expected_data['close']):.3f} {'✅' if adjusted_matches[3] else '❌'}")
            
            if all(adjusted_matches):
                print(f"     结论: TIME_SERIES_DAILY_ADJUSTED数据与期望数据匹配 ✅")
            else:
                print(f"     结论: TIME_SERIES_DAILY_ADJUSTED数据与期望数据不匹配 ❌")
        
        # 5. 总结和建议
        print(f"\n5. 总结和建议:")
        
        if daily_data and adjusted_data:
            same_data = (
                abs(float(daily_data['1. open']) - float(adjusted_data['1. open'])) < 0.001 and
                abs(float(daily_data['2. high']) - float(adjusted_data['2. high'])) < 0.001 and
                abs(float(daily_data['3. low']) - float(adjusted_data['3. low'])) < 0.001 and
                abs(float(daily_data['4. close']) - float(adjusted_data['4. close'])) < 0.001
            )
            
            if same_data:
                print(f"   📊 两个API返回相同的OHLC数据，说明JD在{target_date}没有拆股或分红调整")
            else:
                print(f"   📊 两个API返回不同的OHLC数据，说明存在拆股或分红调整")
        
        # 检查哪个API更接近期望数据
        if daily_data and adjusted_data:
            daily_total_diff = (
                abs(float(daily_data['1. open']) - expected_data['open']) +
                abs(float(daily_data['2. high']) - expected_data['high']) +
                abs(float(daily_data['3. low']) - expected_data['low']) +
                abs(float(daily_data['4. close']) - expected_data['close'])
            )
            
            adjusted_total_diff = (
                abs(float(adjusted_data['1. open']) - expected_data['open']) +
                abs(float(adjusted_data['2. high']) - expected_data['high']) +
                abs(float(adjusted_data['3. low']) - expected_data['low']) +
                abs(float(adjusted_data['4. close']) - expected_data['close'])
            )
            
            print(f"   📈 TIME_SERIES_DAILY总差异: {daily_total_diff:.3f}")
            print(f"   📈 TIME_SERIES_DAILY_ADJUSTED总差异: {adjusted_total_diff:.3f}")
            
            if adjusted_total_diff < daily_total_diff:
                print(f"   💡 建议: 使用TIME_SERIES_DAILY_ADJUSTED API，因为它更接近期望数据")
                print(f"   💡 这可能解决用户反馈的数据不一致问题")
            elif daily_total_diff < adjusted_total_diff:
                print(f"   💡 当前使用的TIME_SERIES_DAILY API更接近期望数据")
                print(f"   💡 数据差异可能来自其他原因（数据源、时区等）")
            else:
                print(f"   💡 两个API与期望数据的差异相同")
                print(f"   💡 需要进一步调查数据差异的原因")
        
        print(f"\n   🔧 技术建议:")
        print(f"      1. 考虑在应用中添加API选择选项（调整/未调整价格）")
        print(f"      2. 在UI中显示数据源信息，告知用户可能的差异")
        print(f"      3. 提供数据来源说明，解释Alpha Vantage与其他数据源的差异")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_adjusted_data()