#!/usr/bin/env python3
"""
检查Render环境中的API密钥
验证API密钥是否为demo密钥
"""

import requests
import json
from datetime import datetime

def check_render_api_key():
    """
    检查Render环境中的API密钥状态
    """
    print(f"=== Render API密钥检查 ===")
    print(f"时间: {datetime.now()}")
    
    # Render应用URL
    render_url = "https://ifinance-dev.onrender.com"
    
    # 测试环境变量端点
    env_endpoint = f"{render_url}/api/test-env"
    
    print(f"\n--- 检查Render环境变量 ---")
    print(f"请求URL: {env_endpoint}")
    
    try:
        response = requests.get(env_endpoint, timeout=30)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"环境变量响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查API密钥
            api_key = data.get('ALPHA_VANTAGE_API_KEY', '')
            if api_key:
                # 检查是否为demo密钥
                if api_key == 'demo':
                    print("❌ 检测到demo API密钥！")
                    print("   这是Alpha Vantage的演示密钥，只能返回演示信息，无法获取真实数据。")
                    print("   需要在Render控制台设置真实的API密钥。")
                elif len(api_key) > 8:
                    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
                    print(f"✅ 检测到自定义API密钥: {masked_key}")
                    
                    # 测试这个API密钥
                    print("\n--- 测试API密钥有效性 ---")
                    test_api_key_validity(api_key)
                else:
                    print(f"⚠️ API密钥长度异常: {len(api_key)} 字符")
            else:
                print("❌ 未检测到API密钥")
        else:
            print(f"❌ 无法获取环境变量: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 直接测试搜索功能
    print(f"\n--- 直接测试Render应用搜索功能 ---")
    search_endpoint = f"{render_url}/_dash-update-component"
    
    # 模拟Dash回调请求
    search_data = {
        "output": "stock-dropdown.options",
        "outputs": [{"id": "stock-dropdown", "property": "options"}],
        "inputs": [{"id": "search-input", "property": "value", "value": "AAPL"}],
        "changedPropIds": ["search-input.value"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(search_endpoint, json=search_data, headers=headers, timeout=30)
        print(f"搜索测试 - HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"搜索响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"搜索失败: {response.status_code}")
            print(f"错误内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 搜索测试异常: {e}")

def test_api_key_validity(api_key):
    """
    测试API密钥的有效性
    """
    base_url = "https://www.alphavantage.co/query"
    
    # 测试SYMBOL_SEARCH
    print("测试 SYMBOL_SEARCH...")
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": "AAPL",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            if "Information" in data and "demo" in data["Information"]:
                print("❌ API密钥仍然是demo密钥")
                return False
            elif "bestMatches" in data:
                matches = data["bestMatches"]
                print(f"✅ SYMBOL_SEARCH成功，找到 {len(matches)} 个匹配项")
                if matches:
                    print(f"   第一个匹配: {matches[0].get('1. symbol', 'N/A')} - {matches[0].get('2. name', 'N/A')}")
                return True
            elif "Error Message" in data:
                print(f"❌ API错误: {data['Error Message']}")
                return False
            elif "Note" in data:
                print(f"⚠️ API限制: {data['Note']}")
                return False
            else:
                print(f"⚠️ 未知响应格式: {data}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    check_render_api_key()