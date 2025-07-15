#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Alpha Vantage搜索功能
直接测试API调用，查看实际响应
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_alpha_vantage_search(keywords: str, api_key: str) -> Dict[str, Any]:
    """
    直接测试Alpha Vantage搜索API
    
    Args:
        keywords: 搜索关键词
        api_key: API密钥
        
    Returns:
        Dict[str, Any]: API响应
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keywords,
        "apikey": api_key
    }
    
    # 构建完整URL
    query_string = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{query_string}"
    
    print(f"\n🔍 搜索关键词: {keywords}")
    print(f"📡 请求URL: {full_url}")
    
    try:
        # 创建请求
        req = urllib.request.Request(full_url)
        req.add_header('User-Agent', 'iFinance/1.0.0')
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            headers = dict(response.headers)
            content = response.read().decode('utf-8')
            
            print(f"\n📊 HTTP状态码: {status_code}")
            print(f"📄 响应头: {headers}")
            
            if status_code == 200:
                data = json.loads(content)
                print(f"\n✅ 响应数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # 分析响应
                if "bestMatches" in data:
                    matches = data["bestMatches"]
                    print(f"\n📈 找到 {len(matches)} 个匹配结果")
                    for i, match in enumerate(matches, 1):
                        symbol = match.get("1. symbol", "N/A")
                        name = match.get("2. name", "N/A")
                        print(f"  {i}. {symbol} - {name}")
                else:
                    print("\n❌ 响应中没有 'bestMatches' 字段")
                    
                # 检查错误信息
                if "Error Message" in data:
                    print(f"\n❌ API错误: {data['Error Message']}")
                if "Note" in data:
                    print(f"\n⚠️  API提示: {data['Note']}")
                    
                return data
            else:
                print(f"\n❌ HTTP错误: {status_code}")
                print(f"响应内容: {content}")
                return {"error": f"HTTP {status_code}", "content": content}
                
    except Exception as e:
        print(f"\n💥 请求异常: {str(e)}")
        return {"error": str(e)}

def main():
    """
    主函数：测试多个搜索关键词
    """
    print("🚀 Alpha Vantage搜索功能调试工具")
    print("=" * 50)
    
    # 使用Render上的API密钥进行测试
    api_key = 'SDMG58OJI9FOIUWW'
    if not api_key:
        print("❌ 错误: 未找到ALPHA_VANTAGE_API_KEY环境变量")
        print("请设置环境变量: export ALPHA_VANTAGE_API_KEY=your_api_key")
        return
    
    print(f"🔑 使用API密钥: {api_key[:10]}..." if len(api_key) > 10 else f"🔑 使用API密钥: {api_key}")
    
    # 测试关键词列表
    test_keywords = [
        "TSLA",      # Tesla - 应该能找到
        "tsla",      # 小写测试
        "AAPL",      # Apple - 应该能找到
        "META",      # Meta - 应该能找到
        "AMZN",      # Amazon - 应该能找到
        "BABA",      # Alibaba - 应该能找到
        "didi",      # 滴滴 - 根据日志应该能找到
        "tesla",     # 公司名称搜索
        "apple",     # 公司名称搜索
        "microsoft", # 公司名称搜索
    ]
    
    results = {}
    
    for keyword in test_keywords:
        try:
            result = test_alpha_vantage_search(keyword, api_key)
            results[keyword] = result
            print("\n" + "="*50)
        except KeyboardInterrupt:
            print("\n\n⏹️  用户中断测试")
            break
        except Exception as e:
            print(f"\n💥 测试 '{keyword}' 时发生异常: {str(e)}")
            results[keyword] = {"error": str(e)}
    
    # 总结结果
    print("\n\n📊 测试结果总结:")
    print("=" * 50)
    
    for keyword, result in results.items():
        if "error" in result:
            print(f"❌ {keyword}: 错误 - {result['error']}")
        elif "bestMatches" in result:
            count = len(result["bestMatches"])
            print(f"✅ {keyword}: 找到 {count} 个结果")
        else:
            print(f"⚠️  {keyword}: 未知响应格式")
    
    # 保存详细结果到文件
    output_file = "alpha_vantage_debug_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 详细结果已保存到: {output_file}")
    except Exception as e:
        print(f"\n❌ 保存结果文件失败: {str(e)}")

if __name__ == "__main__":
    main()