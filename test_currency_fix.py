#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试货币显示修复效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor
from src.utils.config import config


def test_currency_display():
    """
    测试修复后的货币显示
    """
    print("\n" + "="*80)
    print("测试修复后的货币显示效果")
    print("="*80)
    
    try:
        api_client = AlphaVantageClient()
        data_processor = DataProcessor()
        
        # 测试不同货币的股票
        test_cases = [
            {
                "search": "HSBA",
                "description": "英国汇丰银行 (应显示便士符号 p)"
            },
            {
                "search": "TYT.LON", 
                "description": "伦敦丰田ADR (应显示日元符号 ¥)"
            },
            {
                "search": "AAPL",
                "description": "美国苹果 (应显示美元符号 $)"
            },
            {
                "search": "AZN",
                "description": "阿斯利康 (美国版本应显示$，英国版本应显示p)"
            }
        ]
        
        for test_case in test_cases:
            search_term = test_case["search"]
            description = test_case["description"]
            
            print(f"\n{'='*60}")
            print(f"测试: {search_term}")
            print(f"说明: {description}")
            print(f"{'='*60}")
            
            try:
                # 搜索股票
                search_results = api_client.search_symbols(search_term)
                
                if not search_results:
                    print(f"❌ 未找到股票: {search_term}")
                    continue
                
                # 处理搜索结果
                processed_results = data_processor.process_symbol_search_results(search_results)
                
                print(f"\n🔧 修复后的货币显示:")
                for i, result in enumerate(processed_results[:3]):
                    symbol = result.get('symbol', 'N/A')
                    name = result.get('name', 'N/A')
                    region = result.get('region', 'N/A')
                    currency = result.get('currency', 'N/A')
                    currency_symbol = result.get('currency_symbol', 'N/A')
                    
                    print(f"\n  结果 {i+1}: {symbol} - {name}")
                    print(f"    地区: {region}")
                    print(f"    货币代码: {currency}")
                    print(f"    货币符号: {currency_symbol}")
                    print(f"    显示格式: {currency_symbol} {currency}")
                    
                    # 验证货币符号是否正确
                    expected_symbols = {
                        'USD': '$',
                        'GBP': '£', 
                        'GBX': 'p',
                        'JPY': '¥',
                        'EUR': '€'
                    }
                    
                    expected = expected_symbols.get(currency)
                    if expected and currency_symbol == expected:
                        print(f"    ✅ 货币符号正确")
                    elif expected:
                        print(f"    ❌ 货币符号错误，期望: {expected}，实际: {currency_symbol}")
                    else:
                        print(f"    ⚠️  未知货币类型: {currency}")
                        
            except Exception as e:
                print(f"❌ 处理股票 {search_term} 时出错: {str(e)}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        
    print(f"\n{'='*80}")
    print("货币显示测试完成")
    print(f"{'='*80}")


def explain_findings():
    """
    解释发现的问题和解决方案
    """
    print("\n" + "="*80)
    print("问题分析和解决方案")
    print("="*80)
    
    print("\n📋 发现的问题:")
    print("1. TYT.LON 显示日元符号是正确的")
    print("   - 这是丰田汽车在伦敦交易所的ADR (美国存托凭证)")
    print("   - 虽然在伦敦交易，但以日元计价")
    print("   - Alpha Vantage API 返回 JPY 是准确的")
    
    print("\n2. 英国本土股票使用 GBX (便士) 而不是 GBP (英镑)")
    print("   - 英国股票通常以便士计价 (1英镑 = 100便士)")
    print("   - 例如: HSBA.LON, AZN.LON, ULVR.LON 等")
    print("   - 已添加 GBX -> 'p' 的货币符号映射")
    
    print("\n3. Alpha Vantage 对日本股市的支持有限")
    print("   - 不支持东京交易所的原生格式 (如 7203.T)")
    print("   - 主要返回在美国交易的日本公司ADR")
    print("   - 或者在其他国际交易所交易的日本公司股票")
    
    print("\n✅ 解决方案:")
    print("1. 添加了 GBX 货币符号支持")
    print("2. 扩展了地区映射配置")
    print("3. 改进了UI货币显示格式")
    
    print("\n💡 建议:")
    print("1. 如需查询日本本土股票，可考虑其他数据源")
    print("2. 用户搜索时可提示不同交易所的版本")
    print("3. 在UI中显示股票的交易所信息")


if __name__ == "__main__":
    # 检查环境配置
    if not config.get("ALPHA_VANTAGE_API_KEY"):
        print("❌ 错误: 未找到 ALPHA_VANTAGE_API_KEY 环境变量")
        sys.exit(1)
    
    test_currency_display()
    explain_findings()