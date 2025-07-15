#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实API密钥的Alpha Vantage响应
直接调用API查看详细响应内容
"""

import os
import requests
import json
from typing import Dict, Any

def test_alpha_vantage_api():
    """
    测试Alpha Vantage API的真实响应
    """
    # 获取API密钥
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    print(f"使用API密钥: {api_key[:10]}...{api_key[-4:] if api_key and len(api_key) > 14 else api_key}")
    
    if not api_key:
        print("错误: 未找到ALPHA_VANTAGE_API_KEY环境变量")
        return
    
    # 测试不同的搜索关键词
    test_keywords = ['AAPL', 'MSFT', 'NVDA', 'JD', 'META', 'FUTU']
    
    base_url = "https://www.alphavantage.co/query"
    
    for keyword in test_keywords:
        print(f"\n{'='*50}")
        print(f"测试搜索关键词: {keyword}")
        print(f"{'='*50}")
        
        # 构建请求参数
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keyword,
            'apikey': api_key
        }
        
        try:
            # 发送请求
            print(f"发送请求到: {base_url}")
            print(f"请求参数: {params}")
            
            response = requests.get(base_url, params=params, timeout=30)
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            # 检查响应内容
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"\n原始JSON响应:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # 检查特定字段
                    if 'bestMatches' in data:
                        best_matches = data['bestMatches']
                        print(f"\nbestMatches字段:")
                        print(f"类型: {type(best_matches)}")
                        print(f"长度: {len(best_matches) if isinstance(best_matches, list) else 'N/A'}")
                        print(f"内容: {best_matches}")
                    else:
                        print(f"\n警告: 响应中没有找到'bestMatches'字段")
                        print(f"可用字段: {list(data.keys())}")
                    
                    # 检查错误信息
                    if 'Error Message' in data:
                        print(f"\n错误信息: {data['Error Message']}")
                    
                    if 'Note' in data:
                        print(f"\n注意事项: {data['Note']}")
                    
                    if 'Information' in data:
                        print(f"\n信息: {data['Information']}")
                        
                except json.JSONDecodeError as e:
                    print(f"\nJSON解析错误: {e}")
                    print(f"原始响应文本: {response.text[:500]}...")
            else:
                print(f"\n请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text[:500]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"\n请求异常: {e}")
        except Exception as e:
            print(f"\n未知错误: {e}")
    
    # 测试API密钥有效性
    print(f"\n{'='*50}")
    print("测试API密钥有效性 - 获取AAPL报价")
    print(f"{'='*50}")
    
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': 'AAPL',
        'apikey': api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n报价API响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"\nJSON解析错误: {e}")
                print(f"原始响应文本: {response.text[:500]}...")
        else:
            print(f"\n请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            
    except Exception as e:
        print(f"\n测试报价API时出错: {e}")

if __name__ == "__main__":
    test_alpha_vantage_api()