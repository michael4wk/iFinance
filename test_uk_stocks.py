#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试英国本土股票的货币显示
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.alpha_vantage import AlphaVantageClient
from src.utils.config import config


def test_uk_stocks():
    """
    测试英国本土股票
    """
    print("\n" + "="*80)
    print("测试英国本土股票的货币显示")
    print("="*80)
    
    try:
        api_client = AlphaVantageClient()
        
        # 测试真正的英国本土股票
        uk_stocks = [
            "BP",       # 英国石油
            "SHEL",     # 壳牌
            "VODAFONE", # 沃达丰
            "LLOY",     # 劳埃德银行
            "BARC",     # 巴克莱银行
            "HSBA",     # 汇丰银行
            "AZN",      # 阿斯利康
            "ULVR",     # 联合利华
        ]
        
        for symbol in uk_stocks:
            print(f"\n测试英国股票: {symbol}")
            print("-" * 50)
            
            try:
                results = api_client.search_symbols(symbol)
                
                if results:
                    print(f"✅ 找到 {len(results)} 个结果:")
                    for i, result in enumerate(results[:3]):  # 显示前3个结果
                        region = result.get('region', 'N/A')
                        currency = result.get('currency', 'N/A')
                        symbol_code = result.get('symbol', 'N/A')
                        name = result.get('name', 'N/A')
                        
                        print(f"  {i+1}. {symbol_code} - {name}")
                        print(f"     地区: {region}")
                        print(f"     货币: {currency}")
                        print(f"     匹配度: {result.get('match_score', 'N/A')}")
                        
                        # 特别关注英国地区的结果
                        if 'United Kingdom' in region or 'London' in region:
                            print(f"     ⭐ 这是英国本土股票！")
                else:
                    print(f"❌ 未找到结果")
                    
            except Exception as e:
                print(f"❌ 搜索失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        
    print(f"\n{'='*80}")
    print("英国股票测试完成")
    print(f"{'='*80}")


if __name__ == "__main__":
    # 检查环境配置
    if not config.get("ALPHA_VANTAGE_API_KEY"):
        print("❌ 错误: 未找到 ALPHA_VANTAGE_API_KEY 环境变量")
        sys.exit(1)
    
    test_uk_stocks()