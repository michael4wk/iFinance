#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试特定日期数据准确性
专门用于验证META 2025-02-05数据的问题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from datetime import datetime, timedelta
from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor

def debug_specific_date():
    """
    调试特定日期的数据问题
    """
    print("=" * 80)
    print("META 2025-02-05 数据准确性调试")
    print("=" * 80)
    
    # 初始化客户端
    api_client = AlphaVantageClient()
    processor = DataProcessor()
    
    target_date = '2025-02-05'
    print(f"\n目标日期: {target_date}")
    
    try:
        # 1. 获取完整历史数据
        print("\n1. 获取META完整历史数据...")
        daily_data = api_client.get_daily_data('META', 'full')
        print(f"   API返回数据条数: {len(daily_data['time_series'])}")
        
        # 2. 检查原始API数据中是否包含目标日期
        print("\n2. 检查原始API数据...")
        time_series = daily_data['time_series']
        
        if target_date in time_series:
            raw_data = time_series[target_date]
            print(f"   ✅ 原始API数据中找到 {target_date}:")
            print(f"      Open: {raw_data['open']}")
            print(f"      High: {raw_data['high']}")
            print(f"      Low: {raw_data['low']}")
            print(f"      Close: {raw_data['close']}")
            print(f"      Volume: {raw_data['volume']}")
        else:
            print(f"   ❌ 原始API数据中未找到 {target_date}")
            # 查找最接近的日期
            available_dates = sorted(time_series.keys())
            target_dt = datetime.strptime(target_date, '%Y-%m-%d')
            
            closest_dates = []
            for date_str in available_dates:
                date_dt = datetime.strptime(date_str, '%Y-%m-%d')
                diff = abs((date_dt - target_dt).days)
                closest_dates.append((date_str, diff))
            
            closest_dates.sort(key=lambda x: x[1])
            print(f"   最接近的5个日期:")
            for date_str, diff in closest_dates[:5]:
                print(f"      {date_str} (相差{diff}天)")
        
        # 3. 处理数据并检查
        print("\n3. 处理数据...")
        df = processor.process_daily_data(daily_data, days_limit=None)
        print(f"   处理后数据条数: {len(df)}")
        print(f"   数据日期范围: {df.index.min().strftime('%Y-%m-%d')} 到 {df.index.max().strftime('%Y-%m-%d')}")
        
        # 4. 检查处理后的数据中是否包含目标日期
        print("\n4. 检查处理后的数据...")
        df_date_strings = df.index.strftime('%Y-%m-%d')
        
        if target_date in df_date_strings.values:
            target_row = df[df_date_strings == target_date].iloc[0]
            print(f"   ✅ 处理后数据中找到 {target_date}:")
            print(f"      Open: {target_row['open']:.2f}")
            print(f"      High: {target_row['high']:.2f}")
            print(f"      Low: {target_row['low']:.2f}")
            print(f"      Close: {target_row['close']:.2f}")
            print(f"      Volume: {target_row['volume']:,}")
            change_val = target_row.get('change', None)
            change_pct_val = target_row.get('change_percent', None)
            
            if pd.notna(change_val):
                print(f"      Change: {change_val:.2f}")
            else:
                print(f"      Change: N/A")
                
            if pd.notna(change_pct_val):
                print(f"      Change%: {change_pct_val:.2f}%")
            else:
                print(f"      Change%: N/A")
            
            # 验证计算字段的准确性
            print("\n   验证计算字段:")
            target_idx = df.index.get_loc(df[df_date_strings == target_date].index[0])
            
            if target_idx < len(df) - 1:
                current_close = target_row['close']
                previous_row = df.iloc[target_idx + 1]
                previous_close = previous_row['close']
                previous_date = df.index[target_idx + 1].strftime('%Y-%m-%d')
                
                manual_change = current_close - previous_close
                manual_change_percent = (manual_change / previous_close * 100)
                
                print(f"      当前日期 {target_date}: Close = {current_close:.2f}")
                print(f"      前一交易日 {previous_date}: Close = {previous_close:.2f}")
                print(f"      手动计算变化: {manual_change:.2f}")
                print(f"      手动计算变化%: {manual_change_percent:.2f}%")
                stored_change = target_row.get('change', None)
                stored_change_pct = target_row.get('change_percent', None)
                
                if pd.notna(stored_change):
                    print(f"      存储的变化: {stored_change:.2f}")
                else:
                    print(f"      存储的变化: N/A")
                    
                if pd.notna(stored_change_pct):
                    print(f"      存储的变化%: {stored_change_pct:.2f}%")
                else:
                    print(f"      存储的变化%: N/A")
                
                # 检查是否匹配
                change_match = abs(manual_change - (target_row.get('change', 0) if pd.notna(target_row.get('change')) else 0)) < 0.01
                percent_match = abs(manual_change_percent - (target_row.get('change_percent', 0) if pd.notna(target_row.get('change_percent')) else 0)) < 0.01
                
                print(f"      计算匹配: {'✅' if change_match else '❌'}")
                print(f"      百分比匹配: {'✅' if percent_match else '❌'}")
            else:
                print(f"      {target_date} 是最早的数据，无法计算变化")
                
        else:
            print(f"   ❌ 处理后数据中未找到 {target_date}")
            
            # 查找最接近的日期
            target_dt = pd.to_datetime(target_date)
            df_dates = df.index
            closest_date = min(df_dates, key=lambda x: abs((x - target_dt).days))
            closest_date_str = closest_date.strftime('%Y-%m-%d')
            diff_days = abs((closest_date - target_dt).days)
            
            print(f"   最接近的日期: {closest_date_str} (相差{diff_days}天)")
            
            closest_row = df.loc[closest_date]
            print(f"   该日期数据:")
            print(f"      Open: {closest_row['open']:.2f}")
            print(f"      High: {closest_row['high']:.2f}")
            print(f"      Low: {closest_row['low']:.2f}")
            print(f"      Close: {closest_row['close']:.2f}")
            print(f"      Volume: {closest_row['volume']:,}")
        
        # 5. 检查2025年2月前后的数据
        print("\n5. 检查2025年2月前后的数据...")
        feb_2025_data = df[(df.index >= '2025-02-01') & (df.index <= '2025-02-28')]
        
        if len(feb_2025_data) > 0:
            print(f"   2025年2月数据条数: {len(feb_2025_data)}")
            print(f"   2025年2月数据范围: {feb_2025_data.index.min().strftime('%Y-%m-%d')} 到 {feb_2025_data.index.max().strftime('%Y-%m-%d')}")
            
            print(f"   2025年2月前5个交易日:")
            for i in range(min(5, len(feb_2025_data))):
                row = feb_2025_data.iloc[i]
                date_str = feb_2025_data.index[i].strftime('%Y-%m-%d')
                print(f"      {date_str}: Close={row['close']:.2f}, Volume={row['volume']:,}")
        else:
            print(f"   ❌ 未找到2025年2月的数据")
            
            # 查找最接近2025年2月的数据
            feb_start = pd.to_datetime('2025-02-01')
            closest_to_feb = min(df.index, key=lambda x: abs((x - feb_start).days))
            print(f"   最接近2025年2月的数据: {closest_to_feb.strftime('%Y-%m-%d')}")
        
        # 6. 检查数据的时间范围问题
        print("\n6. 数据时间范围分析...")
        latest_date = df.index.max()
        earliest_date = df.index.min()
        today = datetime.now().date()
        
        print(f"   最新数据日期: {latest_date.strftime('%Y-%m-%d')}")
        print(f"   最早数据日期: {earliest_date.strftime('%Y-%m-%d')}")
        print(f"   今天日期: {today}")
        print(f"   最新数据距今: {(today - latest_date.date()).days} 天")
        
        if latest_date.date() < datetime.strptime(target_date, '%Y-%m-%d').date():
            print(f"   ⚠️  问题发现: 最新数据日期 {latest_date.strftime('%Y-%m-%d')} 早于目标日期 {target_date}")
            print(f"   这说明API返回的数据不包含未来日期，这是正常的")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_date()