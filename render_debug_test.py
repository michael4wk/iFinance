#!/usr/bin/env python3
"""
Render环境API调试测试脚本
用于在Render部署环境中测试Alpha Vantage API响应
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目配置系统
from src.utils.config import config

def log_message(message):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def test_api_key():
    """测试API密钥配置"""
    log_message("=== API密钥配置测试 ===")
    
    api_key = config.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        log_message("❌ ALPHA_VANTAGE_API_KEY环境变量未设置")
        return False
    
    log_message(f"✅ API密钥已配置: {api_key[:8]}...{api_key[-4:]}")
    log_message(f"API密钥长度: {len(api_key)}")
    return True

def test_basic_api_call(api_key):
    """测试基础API调用"""
    log_message("=== 基础API调用测试 ===")
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "AAPL",
        "apikey": api_key
    }
    
    try:
        log_message(f"发送请求到: {url}")
        log_message(f"请求参数: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        log_message(f"响应状态码: {response.status_code}")
        log_message(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            log_message(f"响应数据: {json.dumps(data, indent=2)}")
            
            if "Global Quote" in data:
                log_message("✅ 基础API调用成功")
                return True
            else:
                log_message(f"❌ 响应格式异常，缺少'Global Quote'字段")
                return False
        else:
            log_message(f"❌ API调用失败，状态码: {response.status_code}")
            log_message(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        log_message(f"❌ API调用异常: {str(e)}")
        return False

def test_symbol_search(api_key, keywords):
    """测试股票搜索功能"""
    log_message(f"=== 股票搜索测试: {keywords} ===")
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keywords,
        "apikey": api_key
    }
    
    try:
        log_message(f"发送搜索请求: {keywords}")
        log_message(f"请求参数: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        log_message(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_message(f"原始响应数据: {json.dumps(data, indent=2)}")
            log_message(f"响应数据类型: {type(data)}")
            log_message(f"响应数据键: {list(data.keys()) if isinstance(data, dict) else '不是字典类型'}")
            
            best_matches = data.get("bestMatches", [])
            log_message(f"bestMatches内容: {best_matches}")
            log_message(f"bestMatches类型: {type(best_matches)}")
            log_message(f"bestMatches长度: {len(best_matches) if isinstance(best_matches, list) else '不是列表类型'}")
            
            if best_matches:
                log_message(f"✅ 搜索成功，找到 {len(best_matches)} 个结果")
                for i, match in enumerate(best_matches[:3]):  # 只显示前3个结果
                    symbol = match.get("1. symbol", "N/A")
                    name = match.get("2. name", "N/A")
                    log_message(f"  结果 {i+1}: {symbol} - {name}")
                return True
            else:
                log_message(f"❌ 搜索返回空结果")
                return False
        else:
            log_message(f"❌ 搜索请求失败，状态码: {response.status_code}")
            log_message(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        log_message(f"❌ 搜索请求异常: {str(e)}")
        return False

def test_environment_info():
    """测试环境信息"""
    log_message("=== 环境信息 ===")
    
    # Python版本
    log_message(f"Python版本: {sys.version}")
    
    # 环境变量
    env_vars = ['ENVIRONMENT', 'DEBUG', 'TZ', 'ALPHA_VANTAGE_API_KEY']
    for var in env_vars:
        value = os.getenv(var, 'Not Set')
        if var == 'ALPHA_VANTAGE_API_KEY' and value != 'Not Set':
            value = f"{value[:8]}...{value[-4:]}"
        log_message(f"{var}: {value}")
    
    # 网络测试
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            log_message(f"外部IP: {ip_info.get('origin', 'Unknown')}")
        else:
            log_message("无法获取外部IP信息")
    except Exception as e:
        log_message(f"网络测试失败: {str(e)}")

def main():
    """主函数"""
    log_message("开始Render环境API调试测试")
    log_message("=" * 50)
    
    # 测试环境信息
    test_environment_info()
    
    # 测试API密钥
    if not test_api_key():
        log_message("API密钥测试失败，退出")
        return
    
    api_key = config.get('ALPHA_VANTAGE_API_KEY')
    
    # 测试基础API调用
    if not test_basic_api_call(api_key):
        log_message("基础API调用失败")
    
    # 测试多个搜索关键词
    test_keywords = ['TSLA', 'AAPL', 'META', 'microsoft', 'tesla', 'apple']
    
    success_count = 0
    for keyword in test_keywords:
        if test_symbol_search(api_key, keyword):
            success_count += 1
    
    log_message("=" * 50)
    log_message(f"测试完成: {success_count}/{len(test_keywords)} 个搜索测试成功")
    
    if success_count == 0:
        log_message("❌ 所有搜索测试都失败了")
    elif success_count == len(test_keywords):
        log_message("✅ 所有搜索测试都成功了")
    else:
        log_message(f"⚠️ 部分搜索测试成功 ({success_count}/{len(test_keywords)})")

if __name__ == "__main__":
    main()