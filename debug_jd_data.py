#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试JD股票2025-01-08数据问题
对比API原始数据和处理后数据
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import json
from datetime import datetime
from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor

def debug_jd_data():
    """
    调试JD股票2025-01-08的数据问题
    """
    print("=" * 80)
    print("调试JD股票2025-01-08数据问题")
    print("=" * 80)
    
    # 用户提供的正确数据（来自其他交易软件）
    expected_data = {
        'open': 33.629,
        'high': 33.862,
        'low': 33.313,
        'close': 33.726
    }
    
    target_date = '2025-01-08'
    print(f"\n目标验证日期: {target_date}")
    print(f"期望数据（来自其他交易软件）:")
    print(f"  开盘价: ${expected_data['open']:.3f}")
    print(f"  最高价: ${expected_data['high']:.3f}")
    print(f"  最低价: ${expected_data['low']:.3f}")
    print(f"  收盘价: ${expected_data['close']:.3f}")
    
    # 初始化客户端
    api_client = AlphaVantageClient()
    processor = DataProcessor()
    
    try:
        # 1. 获取JD的原始API数据（使用full模式获取完整历史数据）
        print(f"\n1. 获取JD原始API数据...")
        raw_data = api_client.get_daily_data('JD', 'full')
        print(f"   API返回数据条数: {len(raw_data['time_series'])}")
        
        # 2. 检查原始API数据中是否包含目标日期
        print(f"\n2. 检查原始API数据中的 {target_date}...")
        time_series = raw_data['time_series']
        
        if target_date in time_series:
            raw_target_data = time_series[target_date]
            print(f"   ✅ 在原始API数据中找到 {target_date}:")
            print(f"      原始数据结构: {json.dumps(raw_target_data, indent=6)}")
            
            # 解析原始数据
            api_open = float(raw_target_data['open'])
            api_high = float(raw_target_data['high'])
            api_low = float(raw_target_data['low'])
            api_close = float(raw_target_data['close'])
            api_volume = float(raw_target_data['volume'])
            
            print(f"\n   解析后的API数据:")
            print(f"      开盘价: ${api_open:.3f}")
            print(f"      最高价: ${api_high:.3f}")
            print(f"      最低价: ${api_low:.3f}")
            print(f"      收盘价: ${api_close:.3f}")
            print(f"      成交量: {api_volume:,.0f}")
            
            # 3. 对比API数据和期望数据
            print(f"\n3. 对比API数据和期望数据:")
            open_diff = abs(api_open - expected_data['open'])
            high_diff = abs(api_high - expected_data['high'])
            low_diff = abs(api_low - expected_data['low'])
            close_diff = abs(api_close - expected_data['close'])
            
            tolerance = 0.01  # 允许的误差范围
            
            print(f"      开盘价: API={api_open:.3f}, 期望={expected_data['open']:.3f}, 差异={open_diff:.3f} {'✅' if open_diff <= tolerance else '❌'}")
            print(f"      最高价: API={api_high:.3f}, 期望={expected_data['high']:.3f}, 差异={high_diff:.3f} {'✅' if high_diff <= tolerance else '❌'}")
            print(f"      最低价: API={api_low:.3f}, 期望={expected_data['low']:.3f}, 差异={low_diff:.3f} {'✅' if low_diff <= tolerance else '❌'}")
            print(f"      收盘价: API={api_close:.3f}, 期望={expected_data['close']:.3f}, 差异={close_diff:.3f} {'✅' if close_diff <= tolerance else '❌'}")
            
        else:
            print(f"   ❌ 在原始API数据中未找到 {target_date}")
            print(f"   可用日期范围:")
            dates = list(time_series.keys())
            dates.sort(reverse=True)
            for i, date in enumerate(dates[:10]):
                print(f"      {i+1}. {date}")
            if len(dates) > 10:
                print(f"      ... 还有 {len(dates)-10} 个日期")
        
        # 4. 处理数据并检查处理后的结果
        print(f"\n4. 处理数据并检查处理后的结果...")
        df = processor.process_daily_data(raw_data, days_limit=None)
        print(f"   处理后数据条数: {len(df)}")
        
        # 检查处理后的数据
        df_date_strings = df.index.strftime('%Y-%m-%d')
        
        if target_date in df_date_strings.values:
            processed_row = df[df_date_strings == target_date].iloc[0]
            print(f"   ✅ 在处理后数据中找到 {target_date}:")
            print(f"      开盘价: ${processed_row['open']:.3f}")
            print(f"      最高价: ${processed_row['high']:.3f}")
            print(f"      最低价: ${processed_row['low']:.3f}")
            print(f"      收盘价: ${processed_row['close']:.3f}")
            print(f"      成交量: {processed_row['volume']:,.0f}")
            
            # 检查处理过程中是否有数据丢失或变化
            if target_date in time_series:
                print(f"\n   对比原始API数据和处理后数据:")
                raw_data_target = time_series[target_date]
                
                api_vs_processed = {
                    'open': (float(raw_data_target['open']), processed_row['open']),
                    'high': (float(raw_data_target['high']), processed_row['high']),
                    'low': (float(raw_data_target['low']), processed_row['low']),
                    'close': (float(raw_data_target['close']), processed_row['close']),
                    'volume': (float(raw_data_target['volume']), processed_row['volume'])
                }
                
                for field, (api_val, processed_val) in api_vs_processed.items():
                    diff = abs(api_val - processed_val)
                    status = '✅' if diff < 0.001 else '❌'
                    print(f"      {field}: API={api_val:.3f}, 处理后={processed_val:.3f}, 差异={diff:.6f} {status}")
        else:
            print(f"   ❌ 在处理后数据中未找到 {target_date}")
        
        # 5. 检查数据源和时区问题
        print(f"\n5. 检查数据源和时区信息...")
        metadata = raw_data.get('metadata', {})
        print(f"   元数据信息:")
        for key, value in metadata.items():
            print(f"      {key}: {value}")
        
        # 6. 检查最近几个交易日的数据
        print(f"\n6. 检查最近几个交易日的数据...")
        recent_dates = ['2025-01-10', '2025-01-09', '2025-01-08', '2025-01-07', '2025-01-06']
        
        for date_str in recent_dates:
            if date_str in time_series:
                data = time_series[date_str]
                open_price = float(data['open'])
                high_price = float(data['high'])
                low_price = float(data['low'])
                close_price = float(data['close'])
                print(f"      {date_str}: O={open_price:.3f}, H={high_price:.3f}, L={low_price:.3f}, C={close_price:.3f}")
        
        # 7. 总结分析
        print(f"\n7. 问题分析总结:")
        if target_date in time_series:
            raw_target = time_series[target_date]
            api_data = {
                'open': float(raw_target['open']),
                'high': float(raw_target['high']),
                'low': float(raw_target['low']),
                'close': float(raw_target['close'])
            }
            
            all_match = True
            for field in ['open', 'high', 'low', 'close']:
                if abs(api_data[field] - expected_data[field]) > 0.01:
                    all_match = False
                    break
            
            if all_match:
                print(f"   ✅ Alpha Vantage API数据与期望数据匹配，问题可能在UI显示层")
            else:
                print(f"   ❌ Alpha Vantage API数据与期望数据不匹配，可能是数据源差异")
                print(f"   可能原因:")
                print(f"      1. 不同数据源的价格可能略有差异")
                print(f"      2. 时区差异导致的交易日期不同")
                print(f"      3. 数据更新时间不同")
                print(f"      4. 调整后价格 vs 未调整价格")
        else:
            print(f"   ❌ Alpha Vantage API中没有 {target_date} 的数据")
            print(f"   可能原因:")
            print(f"      1. {target_date} 不是交易日（周末或节假日）")
            print(f"      2. 数据更新延迟")
            print(f"      3. API数据范围限制")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_jd_data()