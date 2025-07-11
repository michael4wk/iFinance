#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的计算逻辑
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from datetime import datetime
from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor

def verify_calculation_fix():
    """
    验证修复后的计算逻辑
    """
    print("=" * 80)
    print("验证修复后的计算逻辑")
    print("=" * 80)
    
    # 初始化客户端
    api_client = AlphaVantageClient()
    processor = DataProcessor()
    
    target_date = '2025-02-05'
    print(f"\n目标验证日期: {target_date}")
    
    try:
        # 获取META的完整历史数据
        print("\n1. 获取META完整历史数据...")
        daily_data = api_client.get_daily_data('META', 'full')
        print(f"   API返回数据条数: {len(daily_data['time_series'])}")
        
        # 处理数据
        print("\n2. 处理数据（应用修复后的计算逻辑）...")
        df = processor.process_daily_data(daily_data, days_limit=None)
        print(f"   处理后数据条数: {len(df)}")
        
        # 检查目标日期的数据
        print(f"\n3. 检查 {target_date} 的计算结果...")
        df_date_strings = df.index.strftime('%Y-%m-%d')
        
        if target_date in df_date_strings.values:
            target_row = df[df_date_strings == target_date].iloc[0]
            
            print(f"   ✅ 找到 {target_date} 的数据:")
            print(f"      收盘价: {target_row['close']:.2f}")
            
            change_val = target_row.get('change', None)
            change_pct_val = target_row.get('change_percent', None)
            
            if pd.notna(change_val):
                print(f"      日变化: {change_val:.2f}")
            else:
                print(f"      日变化: N/A")
                
            if pd.notna(change_pct_val):
                print(f"      日变化%: {change_pct_val:.2f}%")
            else:
                print(f"      日变化%: N/A")
            
            # 手动验证计算
            print(f"\n4. 手动验证计算...")
            target_idx = df.index.get_loc(df[df_date_strings == target_date].index[0])
            
            if target_idx < len(df) - 1:
                current_close = target_row['close']
                previous_row = df.iloc[target_idx + 1]  # 在降序数据中，下一行是前一个交易日
                previous_close = previous_row['close']
                previous_date = df.index[target_idx + 1].strftime('%Y-%m-%d')
                
                manual_change = current_close - previous_close
                manual_change_percent = (manual_change / previous_close * 100)
                
                print(f"      当前日期 {target_date}: Close = {current_close:.2f}")
                print(f"      前一交易日 {previous_date}: Close = {previous_close:.2f}")
                print(f"      手动计算变化: {manual_change:.2f}")
                print(f"      手动计算变化%: {manual_change_percent:.2f}%")
                
                # 检查是否匹配
                change_match = abs(manual_change - (change_val if pd.notna(change_val) else 0)) < 0.01
                percent_match = abs(manual_change_percent - (change_pct_val if pd.notna(change_pct_val) else 0)) < 0.01
                
                print(f"\n5. 验证结果:")
                if change_match:
                    print(f"      ✅ 日变化计算正确: 系统计算 {change_val:.2f} = 手动验证 {manual_change:.2f}")
                else:
                    print(f"      ❌ 日变化计算错误: 系统计算 {change_val:.2f} ≠ 手动验证 {manual_change:.2f}")
                    
                if percent_match:
                    print(f"      ✅ 日变化%计算正确: 系统计算 {change_pct_val:.2f}% = 手动验证 {manual_change_percent:.2f}%")
                else:
                    print(f"      ❌ 日变化%计算错误: 系统计算 {change_pct_val:.2f}% ≠ 手动验证 {manual_change_percent:.2f}%")
                
                if change_match and percent_match:
                    print(f"\n🎉 修复成功！计算逻辑现在是正确的！")
                else:
                    print(f"\n⚠️  修复可能不完整，仍有计算错误。")
            else:
                print(f"      {target_date} 是最早的数据，无法计算变化")
                
        else:
            print(f"   ❌ 未找到 {target_date} 的数据")
        
        # 额外测试：检查几个连续日期的计算
        print(f"\n6. 额外验证：检查2025年2月前几个交易日的计算...")
        feb_dates = ['2025-02-07', '2025-02-06', '2025-02-05', '2025-02-04', '2025-02-03']
        
        for date_str in feb_dates:
            if date_str in df_date_strings.values:
                row = df[df_date_strings == date_str].iloc[0]
                change = row.get('change', None)
                change_pct = row.get('change_percent', None)
                
                change_str = f"{change:.2f}" if pd.notna(change) else "N/A"
                change_pct_str = f"{change_pct:.2f}%" if pd.notna(change_pct) else "N/A"
                
                print(f"      {date_str}: Close={row['close']:.2f}, Change={change_str}, Change%={change_pct_str}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_calculation_fix()