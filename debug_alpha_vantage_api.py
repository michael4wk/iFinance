#!/usr/bin/env python3
"""
调试Alpha Vantage API响应
直接测试API调用，查看详细的响应内容
"""

import os
import requests
import json
from datetime import datetime

def test_alpha_vantage_api():
    """
    直接测试Alpha Vantage API调用
    """
    # 从环境变量获取API密钥
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    print(f"=== Alpha Vantage API 调试测试 ===")
    print(f"时间: {datetime.now()}")
    print(f"API Key: {'已设置' if api_key else '未设置'}")
    
    if not api_key:
        print("❌ 错误: ALPHA_VANTAGE_API_KEY 环境变量未设置")
        return
    
    # 显示API密钥的前几位和后几位（用于验证）
    if len(api_key) > 8:
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        print(f"API Key (masked): {masked_key}")
    
    # 测试用例
    test_cases = [
        "NVDA",
        "JD", 
        "META",
        "FUTU",
        "AAPL",
        "TSLA",
        "MSFT"
    ]
    
    base_url = "https://www.alphavantage.co/query"
    
    for keyword in test_cases:
        print(f"\n--- 测试搜索: {keyword} ---")
        
        # 构建请求参数
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keyword,
            "apikey": api_key
        }
        
        print(f"请求URL: {base_url}")
        print(f"请求参数: {dict(params, apikey='***')}")
        
        try:
            # 发送请求
            response = requests.get(base_url, params=params, timeout=30)
            
            print(f"HTTP状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"响应数据类型: {type(data)}")
                    print(f"响应键: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # 检查特定字段
                    if "bestMatches" in data:
                        best_matches = data["bestMatches"]
                        print(f"bestMatches 类型: {type(best_matches)}")
                        print(f"bestMatches 长度: {len(best_matches) if isinstance(best_matches, list) else 'Not a list'}")
                        
                        if isinstance(best_matches, list) and len(best_matches) > 0:
                            print(f"第一个匹配项: {json.dumps(best_matches[0], indent=2, ensure_ascii=False)}")
                        else:
                            print("❌ bestMatches 为空或不是列表")
                    else:
                        print("❌ 响应中没有 bestMatches 字段")
                    
                    # 检查错误信息
                    if "Error Message" in data:
                        print(f"❌ API错误: {data['Error Message']}")
                    
                    if "Note" in data:
                        print(f"⚠️ API提示: {data['Note']}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析错误: {e}")
                    print(f"原始响应内容: {response.text[:500]}...")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"错误内容: {response.text[:500]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 50)
    
    # 测试API密钥有效性
    print(f"\n--- 测试API密钥有效性 ---")
    test_params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "AAPL",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=test_params, timeout=30)
        print(f"GLOBAL_QUOTE测试 - HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"GLOBAL_QUOTE响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if "Global Quote" in data:
                print("✅ API密钥有效，可以获取股票报价")
            elif "Error Message" in data:
                print(f"❌ API错误: {data['Error Message']}")
            elif "Note" in data:
                print(f"⚠️ API限制: {data['Note']}")
        else:
            print(f"❌ GLOBAL_QUOTE测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ GLOBAL_QUOTE测试异常: {e}")

if __name__ == "__main__":
    test_alpha_vantage_api()