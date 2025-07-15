#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web应用中的股票搜索逻辑
模拟完整的搜索流程，定位问题所在
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor
from src.data.validator import DataValidator
from src.utils.exceptions import APIRateLimitError

def test_search_workflow(search_term: str):
    """
    测试完整的搜索工作流程
    
    Args:
        search_term: 搜索关键词
    """
    print(f"\n{'='*60}")
    print(f"🔍 测试搜索关键词: '{search_term}'")
    print(f"{'='*60}")
    
    try:
        # 步骤1: 初始化组件
        print("\n📋 步骤1: 初始化组件...")
        api_client = AlphaVantageClient()
        data_processor = DataProcessor()
        data_validator = DataValidator()
        print("✅ 组件初始化成功")
        
        # 步骤2: 验证搜索关键词
        print("\n📋 步骤2: 验证搜索关键词...")
        validated_keywords = data_validator.validate_search_keywords(search_term)
        print(f"✅ 验证后的关键词: '{validated_keywords}'")
        
        # 步骤3: 调用API搜索
        print("\n📋 步骤3: 调用Alpha Vantage API搜索...")
        search_results = api_client.search_symbols(validated_keywords)
        print(f"✅ API返回 {len(search_results)} 个原始结果")
        
        if search_results:
            print("\n📄 原始搜索结果示例:")
            for i, result in enumerate(search_results[:3]):
                print(f"  {i+1}. {result}")
        else:
            print("⚠️  API返回空结果")
            return
        
        # 步骤4: 处理搜索结果
        print("\n📋 步骤4: 处理搜索结果...")
        processed_results = data_processor.process_symbol_search_results(search_results)
        print(f"✅ 处理后得到 {len(processed_results)} 个结果")
        
        if processed_results:
            print("\n📄 处理后的结果示例:")
            for i, result in enumerate(processed_results[:3]):
                print(f"  {i+1}. {result['symbol']} - {result['name']} (匹配度: {result['match_score']})")
        else:
            print("⚠️  处理后结果为空")
            return
        
        # 步骤5: 生成下拉选项（模拟Web应用逻辑）
        print("\n📋 步骤5: 生成下拉选项...")
        options = []
        stock_info_map = {}
        
        for result in processed_results[:10]:  # 限制显示前10个结果
            options.append({
                "label": result["display_label"], 
                "value": result["symbol"]
            })
            stock_info_map[result["symbol"]] = result
        
        print(f"✅ 生成 {len(options)} 个下拉选项")
        
        if options:
            print("\n📄 下拉选项:")
            for i, option in enumerate(options[:5]):
                print(f"  {i+1}. {option['label']} (值: {option['value']})")
            
            # 自动选择第一个结果
            default_value = options[0]["value"] if options else None
            print(f"\n🎯 默认选择: {default_value}")
            
            return len(options), default_value, stock_info_map
        else:
            print("⚠️  没有生成任何下拉选项")
            return 0, None, {}
            
    except APIRateLimitError as e:
        print(f"❌ API频率限制: {str(e)}")
        return 0, None, {}
    except Exception as e:
        print(f"❌ 搜索失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0, None, {}

def main():
    """
    主函数：测试多个搜索关键词
    """
    print("🚀 Web应用股票搜索逻辑测试工具")
    print("🎯 模拟完整的搜索工作流程")
    
    # 测试关键词列表
    test_keywords = [
        "TSLA",
        "tsla", 
        "AAPL",
        "META",
        "AMZN",
        "BABA",
        "didi",
        "tesla",
        "apple",
        "microsoft"
    ]
    
    results_summary = []
    
    for keyword in test_keywords:
        try:
            option_count, default_value, stock_info = test_search_workflow(keyword)
            results_summary.append({
                "keyword": keyword,
                "option_count": option_count,
                "default_value": default_value,
                "success": option_count > 0
            })
        except Exception as e:
            print(f"❌ 测试 '{keyword}' 时出错: {str(e)}")
            results_summary.append({
                "keyword": keyword,
                "option_count": 0,
                "default_value": None,
                "success": False,
                "error": str(e)
            })
    
    # 打印总结
    print(f"\n\n{'='*80}")
    print("📊 测试结果总结")
    print(f"{'='*80}")
    
    success_count = 0
    for result in results_summary:
        status = "✅" if result["success"] else "❌"
        keyword = result["keyword"]
        option_count = result["option_count"]
        default_value = result.get("default_value", "None")
        
        print(f"{status} {keyword:12} -> {option_count:2d} 个选项, 默认: {default_value}")
        
        if result["success"]:
            success_count += 1
        elif "error" in result:
            print(f"    错误: {result['error']}")
    
    print(f"\n🎯 成功率: {success_count}/{len(test_keywords)} ({success_count/len(test_keywords)*100:.1f}%)")
    
    if success_count == 0:
        print("\n💡 所有搜索都失败了，这可能表明:")
        print("   1. API密钥配置问题")
        print("   2. 网络连接问题")
        print("   3. API响应格式变化")
        print("   4. 代码逻辑错误")
    elif success_count < len(test_keywords):
        print("\n💡 部分搜索失败，建议检查:")
        print("   1. 特定关键词的处理逻辑")
        print("   2. 数据验证和处理流程")
    else:
        print("\n🎉 所有搜索都成功！问题可能在其他地方。")

if __name__ == "__main__":
    main()