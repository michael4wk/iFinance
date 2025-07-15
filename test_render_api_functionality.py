#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render环境的API功能
直接调用Render应用的搜索功能
"""

import requests
import json
from typing import Dict, Any

def test_render_search_functionality():
    """
    测试Render环境的股票搜索功能
    """
    render_url = "https://ifinance-dev.onrender.com"
    
    # 测试不同的搜索关键词
    test_keywords = ['AAPL', 'MSFT', 'NVDA', 'JD', 'META']
    
    print(f"测试Render应用: {render_url}")
    print(f"{'='*60}")
    
    # 首先测试应用是否正常运行
    try:
        response = requests.get(render_url, timeout=30)
        print(f"应用状态检查: {response.status_code}")
        if response.status_code != 200:
            print(f"应用无法访问，状态码: {response.status_code}")
            return
    except Exception as e:
        print(f"无法连接到Render应用: {e}")
        return
    
    # 测试搜索功能
    for keyword in test_keywords:
        print(f"\n{'='*40}")
        print(f"测试搜索: {keyword}")
        print(f"{'='*40}")
        
        # 构建Dash回调请求
        callback_url = f"{render_url}/_dash-update-component"
        
        # Dash回调请求的payload
        payload = {
            "output": "stock-dropdown.options",
            "outputs": [{"id": "stock-dropdown", "property": "options"}],
            "inputs": [{"id": "search-input", "property": "value", "value": keyword}],
            "changedPropIds": ["search-input.value"],
            "state": []
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            print(f"发送搜索请求: {keyword}")
            response = requests.post(
                callback_url, 
                json=payload, 
                headers=headers, 
                timeout=30
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"搜索响应:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # 检查响应结构
                    if 'response' in data:
                        options = data['response'].get('stock-dropdown', {}).get('options', [])
                        print(f"\n找到 {len(options)} 个搜索结果")
                        if options:
                            print(f"第一个结果: {options[0]}")
                        else:
                            print("没有找到搜索结果")
                    else:
                        print("响应格式异常")
                        
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"原始响应: {response.text[:500]}...")
            else:
                print(f"搜索请求失败: {response.status_code}")
                print(f"错误响应: {response.text[:500]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
        except Exception as e:
            print(f"未知错误: {e}")
    
    print(f"\n{'='*60}")
    print("测试完成")

if __name__ == "__main__":
    test_render_search_functionality()