#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据处理逻辑
用于验证日期匹配和数据计算的准确性
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from datetime import datetime, timedelta
from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor

def debug_data_processing():
    """
    调试数据处理流程
    """
    print("=" * 60)
    print("数据处理逻辑调试")
    print("=" * 60)
    
    # 初始化客户端
    api_client = AlphaVantageClient()
    processor = DataProcessor()
    
    # 获取META的完整历史数据
    print("\n1. 获取META完整历史数据...")
    try:
        daily_data = api_client.get_daily_data('META', 'full')
        print(f"   API返回数据条数: {len(daily_data['time_series'])}")
        
        # 查看原始数据的前几条
        print("\n2. 原始API数据示例（前5条）:")
        time_series = daily_data['time_series']
        sorted_dates = sorted(time_series.keys(), reverse=True)  # 按日期降序
        for i, date in enumerate(sorted_dates[:5]):
            data = time_series[date]
            print(f"   {date}: Open={data['open']}, Close={data['close']}, Volume={data['volume']}")
        
        # 处理数据
        print("\n3. 处理数据...")
        df = processor.process_daily_data(daily_data, days_limit=None)
        print(f"   处理后数据条数: {len(df)}")
        print(f"   数据日期范围: {df.index.min().strftime('%Y-%m-%d')} 到 {df.index.max().strftime('%Y-%m-%d')}")
        
        # 检查数据排序
        print("\n4. 数据排序检查（前5条）:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            date_str = df.index[i].strftime('%Y-%m-%d')
            print(f"   {date_str}: Open={row['open']:.2f}, Close={row['close']:.2f}, Change={row.get('change', 'N/A'):.2f if pd.notna(row.get('change')) else 'N/A'}")
        
        # 测试特定日期查找
        test_dates = ['2024-01-15', '2023-06-15', '2022-08-17']
        print("\n5. 测试特定日期查找:")
        
        for test_date in test_dates:
            print(f"\n   测试日期: {test_date}")
            
            # 检查日期是否存在于数据中
            date_exists = test_date in df.index.strftime('%Y-%m-%d')
            print(f"   日期存在: {date_exists}")
            
            if date_exists:
                # 获取该日期的数据
                day_data = df[df.index.strftime('%Y-%m-%d') == test_date].iloc[0]
                print(f"   数据: Open={day_data['open']:.2f}, High={day_data['high']:.2f}, Low={day_data['low']:.2f}, Close={day_data['close']:.2f}, Volume={day_data['volume']:,}")
                
                # 检查计算字段
                change = day_data.get('change')
                change_percent = day_data.get('change_percent')
                print(f"   计算字段: Change={change:.2f if pd.notna(change) else 'N/A'}, Change%={change_percent:.2f if pd.notna(change_percent) else 'N/A'}%")
            else:
                # 查找最接近的日期
                target_dt = pd.to_datetime(test_date)
                df_dates = df.index
                closest_date = min(df_dates, key=lambda x: abs((x - target_dt).days))
                print(f"   最接近的日期: {closest_date.strftime('%Y-%m-%d')}")
                
                # 显示该日期前后的数据
                closest_idx = df.index.get_loc(closest_date)
                print(f"   前后数据:")
                for i in range(max(0, closest_idx-2), min(len(df), closest_idx+3)):
                    row = df.iloc[i]
                    date_str = df.index[i].strftime('%Y-%m-%d')
                    print(f"     {date_str}: Close={row['close']:.2f}")
        
        # 检查变化计算逻辑
        print("\n6. 变化计算逻辑验证:")
        print("   数据按降序排列（最新在前）")
        print("   Change = Close[i] - Close[i+1] (当前日 - 前一交易日)")
        
        # 手动验证前几天的计算
        for i in range(min(3, len(df)-1)):
            current_close = df.iloc[i]['close']
            previous_close = df.iloc[i+1]['close']
            calculated_change = current_close - previous_close
            stored_change = df.iloc[i]['change']
            
            current_date = df.index[i].strftime('%Y-%m-%d')
            previous_date = df.index[i+1].strftime('%Y-%m-%d')
            
            print(f"   {current_date}: Close={current_close:.2f}")
            print(f"   {previous_date}: Close={previous_close:.2f}")
            print(f"   手动计算变化: {calculated_change:.2f}")
            print(f"   存储的变化: {stored_change:.2f if pd.notna(stored_change) else 'N/A'}")
            print(f"   匹配: {'✓' if abs(calculated_change - (stored_change if pd.notna(stored_change) else 0)) < 0.01 else '✗'}")
            print()
            
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_processing()