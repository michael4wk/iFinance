#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试货币显示问题
检查Alpha Vantage API返回的实际货币数据
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor
from src.utils.config import config


def debug_currency_data():
    """
    调试货币数据问题
    """
    print("\n" + "="*80)
    print("调试货币显示问题")
    print("="*80)
    
    try:
        # 初始化客户端
        api_client = AlphaVantageClient()
        data_processor = DataProcessor()
        
        # 测试不同市场的股票
        test_symbols = [
            "toyota",  # 日本股票
            "TYT.LON", # 英国股票 (伦敦交易所)
            "AAPL",    # 美国股票
            "7203.T",  # 日本股票 (东京交易所)
        ]
        
        for symbol in test_symbols:
            print(f"\n{'='*60}")
            print(f"测试股票: {symbol}")
            print(f"{'='*60}")
            
            try:
                # 搜索股票
                search_results = api_client.search_symbols(symbol)
                
                if not search_results:
                    print(f"❌ 未找到股票: {symbol}")
                    continue
                
                print(f"\n📊 原始API返回数据:")
                for i, result in enumerate(search_results[:3]):  # 只显示前3个结果
                    print(f"\n结果 {i+1}:")
                    print(f"  Symbol: {result.get('symbol', 'N/A')}")
                    print(f"  Name: {result.get('name', 'N/A')}")
                    print(f"  Type: {result.get('type', 'N/A')}")
                    print(f"  Region: {result.get('region', 'N/A')}")
                    print(f"  Currency: {result.get('currency', 'N/A')}")
                    print(f"  Market Open: {result.get('market_open', 'N/A')}")
                    print(f"  Market Close: {result.get('market_close', 'N/A')}")
                    print(f"  Timezone: {result.get('timezone', 'N/A')}")
                    print(f"  Match Score: {result.get('match_score', 'N/A')}")
                
                # 处理搜索结果
                processed_results = data_processor.process_symbol_search_results(search_results)
                
                print(f"\n🔧 处理后的数据:")
                for i, result in enumerate(processed_results[:3]):
                    print(f"\n处理结果 {i+1}:")
                    print(f"  Symbol: {result.get('symbol', 'N/A')}")
                    print(f"  Name: {result.get('name', 'N/A')}")
                    print(f"  Region: {result.get('region', 'N/A')}")
                    print(f"  Currency: {result.get('currency', 'N/A')}")
                    print(f"  Currency Symbol: {result.get('currency_symbol', 'N/A')}")
                    
                    # 市场状态信息
                    market_status = result.get('market_status', {})
                    print(f"  Market Status: {market_status.get('status', 'N/A')}")
                    print(f"  Status Text: {market_status.get('status_text', 'N/A')}")
                    
            except Exception as e:
                print(f"❌ 处理股票 {symbol} 时出错: {str(e)}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return
    
    print(f"\n{'='*80}")
    print("调试完成")
    print(f"{'='*80}")


def check_alpha_vantage_support():
    """
    检查Alpha Vantage对日本股市的支持情况
    """
    print("\n" + "="*80)
    print("检查Alpha Vantage对日本股市的支持")
    print("="*80)
    
    try:
        api_client = AlphaVantageClient()
        
        # 测试日本股票代码的不同格式
        japanese_symbols = [
            "7203.T",      # 丰田汽车 (东京交易所格式)
            "7203",        # 丰田汽车 (简化格式)
            "TOYOTA",      # 公司名称搜索
            "Toyota Motor", # 完整公司名称
            "6758.T",      # 索尼 (东京交易所格式)
            "SONY",        # 索尼公司名称
            "9984.T",      # 软银集团
            "SoftBank",    # 软银公司名称
        ]
        
        for symbol in japanese_symbols:
            print(f"\n测试日本股票: {symbol}")
            print("-" * 40)
            
            try:
                results = api_client.search_symbols(symbol)
                
                if results:
                    print(f"✅ 找到 {len(results)} 个结果:")
                    for i, result in enumerate(results[:2]):  # 显示前2个结果
                        print(f"  {i+1}. {result.get('symbol', 'N/A')} - {result.get('name', 'N/A')}")
                        print(f"     地区: {result.get('region', 'N/A')}")
                        print(f"     货币: {result.get('currency', 'N/A')}")
                        print(f"     匹配度: {result.get('match_score', 'N/A')}")
                else:
                    print(f"❌ 未找到结果")
                    
            except Exception as e:
                print(f"❌ 搜索失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        
    print(f"\n{'='*80}")
    print("日本股市支持检查完成")
    print(f"{'='*80}")


if __name__ == "__main__":
    # 检查环境配置
    if not config.get("ALPHA_VANTAGE_API_KEY"):
        print("❌ 错误: 未找到 ALPHA_VANTAGE_API_KEY 环境变量")
        print("请确保在 .env 文件中设置了正确的API密钥")
        sys.exit(1)
    
    # 运行调试
    debug_currency_data()
    check_alpha_vantage_support()