#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试计算逻辑的简化验证
"""

import pandas as pd
from datetime import datetime, timedelta

def test_calculation_logic():
    """
    测试数据计算逻辑
    """
    print("=" * 60)
    print("数据计算逻辑测试")
    print("=" * 60)
    
    # 创建测试数据（模拟真实的股价数据）
    dates = [
        '2025-02-07',  # 最新
        '2025-02-06', 
        '2025-02-05',  # 目标日期
        '2025-02-04',  # 前一交易日
        '2025-02-03'
    ]
    
    closes = [710.0, 708.0, 704.87, 704.19, 700.0]  # 对应的收盘价
    
    # 创建DataFrame（按降序排列，最新在前）
    df = pd.DataFrame({
        'close': closes
    }, index=pd.to_datetime(dates))
    
    print("原始数据（按降序排列，最新在前）:")
    for i, (date, row) in enumerate(df.iterrows()):
        print(f"  {date.strftime('%Y-%m-%d')}: Close = {row['close']:.2f}")
    
    print("\n当前的计算逻辑（有问题的）:")
    # 当前的计算逻辑
    df['change_current'] = df['close'] - df['close'].shift(1)
    df['change_percent_current'] = (df['change_current'] / df['close'].shift(1) * 100).round(2)
    
    for i, (date, row) in enumerate(df.iterrows()):
        change = row['change_current']
        change_pct = row['change_percent_current']
        change_str = f"{change:.2f}" if pd.notna(change) else "N/A"
        change_pct_str = f"{change_pct:.2f}" if pd.notna(change_pct) else "N/A"
        print(f"  {date.strftime('%Y-%m-%d')}: Change = {change_str}, Change% = {change_pct_str}%")
    
    print("\n正确的计算逻辑:")
    # 正确的计算逻辑：对于降序数据，应该用当前值减去下一行的值
    # 但这样会导致逻辑混乱，更好的方法是先排序为升序，计算后再排回降序
    
    # 方法1：临时排序为升序进行计算
    df_asc = df.sort_index(ascending=True)  # 升序排列
    df_asc['change_correct'] = df_asc['close'].diff()  # diff()等同于当前值减去前一个值
    df_asc['change_percent_correct'] = (df_asc['change_correct'] / df_asc['close'].shift(1) * 100).round(2)
    
    # 排回降序
    df_corrected = df_asc.sort_index(ascending=False)
    
    for i, (date, row) in enumerate(df_corrected.iterrows()):
        change = row['change_correct']
        change_pct = row['change_percent_correct']
        change_str = f"{change:.2f}" if pd.notna(change) else "N/A"
        change_pct_str = f"{change_pct:.2f}" if pd.notna(change_pct) else "N/A"
        print(f"  {date.strftime('%Y-%m-%d')}: Change = {change_str}, Change% = {change_pct_str}%")
    
    print("\n重点验证2025-02-05的数据:")
    target_date = '2025-02-05'
    target_row_current = df.loc[target_date]
    target_row_correct = df_corrected.loc[target_date]
    
    print(f"当前错误计算: Change = {target_row_current['change_current']:.2f}, Change% = {target_row_current['change_percent_current']:.2f}%")
    print(f"正确计算结果: Change = {target_row_correct['change_correct']:.2f}, Change% = {target_row_correct['change_percent_correct']:.2f}%")
    
    # 手动验证
    current_close = 704.87  # 2025-02-05
    previous_close = 704.19  # 2025-02-04
    manual_change = current_close - previous_close
    manual_change_pct = (manual_change / previous_close * 100)
    
    print(f"手动验证计算: Change = {manual_change:.2f}, Change% = {manual_change_pct:.2f}%")
    
    print("\n结论:")
    if abs(target_row_correct['change_correct'] - manual_change) < 0.01:
        print("✅ 正确的计算逻辑与手动验证一致")
    else:
        print("❌ 正确的计算逻辑与手动验证不一致")
        
    if abs(target_row_current['change_current'] - manual_change) < 0.01:
        print("✅ 当前的计算逻辑与手动验证一致")
    else:
        print("❌ 当前的计算逻辑与手动验证不一致")
        print("   这说明当前的计算逻辑确实有问题！")

if __name__ == "__main__":
    test_calculation_logic()