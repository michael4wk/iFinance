#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Render API测试脚本
专门用于在Render环境中快速验证API配置
"""

import os
import sys
import urllib.request
import urllib.parse
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目配置系统
from src.utils.config import config

def test_render_api():
    """
    在Render环境中测试API配置
    """
    print("=" * 50)
    print("🔍 Render API配置测试")
    print("=" * 50)
    
    # 获取环境变量
    api_key = config.get('ALPHA_VANTAGE_API_KEY')
    environment = os.getenv('ENVIRONMENT', 'unknown')
    
    print(f"🌍 运行环境: {environment}")
    
    if not api_key:
        print("❌ 错误: ALPHA_VANTAGE_API_KEY 环境变量未设置")
        print("\n🔧 解决方案:")
        print("1. 登录 Render Dashboard")
        print("2. 进入你的服务设置")
        print("3. 添加环境变量: ALPHA_VANTAGE_API_KEY = SDMG58OJI9FOIUWW")
        return False
    
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # 测试1: 基础API调用
    print("\n📡 测试1: 基础API调用 (GLOBAL_QUOTE)")
    if not test_basic_api(api_key):
        return False
    
    # 测试2: 股票搜索
    print("\n🔍 测试2: 股票搜索功能 (SYMBOL_SEARCH)")
    if not test_symbol_search(api_key):
        return False
    
    print("\n✅ 所有测试通过！API配置正常")
    return True

def test_basic_api(api_key):
    """
    测试基础API调用
    """
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': 'AAPL',
        'apikey': api_key
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        
        with urllib.request.urlopen(full_url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'Error Message' in data:
            print(f"❌ API错误: {data['Error Message']}")
            return False
        elif 'Note' in data:
            print(f"⚠️  频率限制: {data['Note']}")
            print("API有效但已达到调用限制")
            return True
        elif 'Global Quote' in data:
            quote = data['Global Quote']
            symbol = quote.get('01. symbol', 'N/A')
            price = quote.get('05. price', 'N/A')
            print(f"✅ 成功获取数据: {symbol} = ${price}")
            return True
        elif 'Information' in data and 'demo' in data['Information'].lower():
            print(f"❌ 演示API密钥: {data['Information']}")
            print("🔧 需要使用有效的API密钥替换演示密钥")
            return False
        else:
            print(f"⚠️  意外响应: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_symbol_search(api_key):
    """
    测试股票搜索功能
    """
    test_keywords = ['TSLA', 'AAPL']
    
    for keyword in test_keywords:
        print(f"\n  🔍 搜索: {keyword}")
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keyword,
            'apikey': api_key
        }
        
        try:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            with urllib.request.urlopen(full_url, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'bestMatches' in data:
                matches = data['bestMatches']
                print(f"  ✅ 找到 {len(matches)} 个结果")
                if matches:
                    first = matches[0]
                    print(f"     首个: {first.get('1. symbol')} - {first.get('2. name', '')[:50]}")
            elif 'Information' in data:
                if 'demo' in data['Information'].lower():
                    print(f"  ❌ 演示API限制: {data['Information']}")
                    return False
                else:
                    print(f"  ℹ️  信息: {data['Information']}")
            else:
                print(f"  ⚠️  意外响应: {list(data.keys())}")
                
        except Exception as e:
            print(f"  ❌ 搜索失败: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 启动Render环境API测试...")
    success = test_render_api()
    
    if success:
        print("\n🎉 测试完成 - API配置正常")
        print("如果Web应用仍有问题，可能需要检查应用代码或重新部署")
    else:
        print("\n❌ 测试失败 - 需要修复API配置")
        print("请按照上述建议修复环境变量配置")
    
    exit(0 if success else 1)