#!/usr/bin/env python3
"""
Render详细调试工具
深入分析Render环境中的500错误原因
"""

import requests
import json
import time
from datetime import datetime
import os

def log_message(message):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_render_main_page():
    """测试Render主页是否正常加载"""
    log_message("=== 测试Render主页加载 ===")
    
    base_url = "https://ifinance-ggqe.onrender.com"
    
    try:
        response = requests.get(base_url, timeout=15)
        log_message(f"主页状态码: {response.status_code}")
        
        if response.status_code == 200:
            log_message("✅ 主页加载成功")
            
            # 检查页面内容
            content = response.text
            if 'dash' in content.lower():
                log_message("✅ 检测到Dash应用内容")
            if 'ifinance' in content.lower():
                log_message("✅ 检测到iFinance应用标识")
            if 'error' in content.lower():
                log_message("⚠️  页面包含错误信息")
                
            # 检查关键元素
            if 'stock-search-input' in content:
                log_message("✅ 找到股票搜索输入框")
            if 'search-button' in content:
                log_message("✅ 找到搜索按钮")
                
            return True
        else:
            log_message(f"❌ 主页加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        log_message(f"❌ 主页访问异常: {str(e)}")
        return False

def test_dash_layout():
    """测试Dash布局端点"""
    log_message("\n=== 测试Dash布局端点 ===")
    
    base_url = "https://ifinance-ggqe.onrender.com"
    
    try:
        response = requests.get(f"{base_url}/_dash-layout", timeout=10)
        log_message(f"布局端点状态码: {response.status_code}")
        
        if response.status_code == 200:
            log_message("✅ Dash布局加载成功")
            try:
                layout_data = response.json()
                log_message(f"✅ 布局数据解析成功，包含 {len(str(layout_data))} 字符")
                return True
            except:
                log_message("⚠️  布局数据解析失败")
                return False
        else:
            log_message(f"❌ Dash布局加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        log_message(f"❌ 布局端点访问异常: {str(e)}")
        return False

def test_api_key_directly():
    """直接测试API密钥是否有效"""
    log_message("\n=== 直接测试API密钥 ===")
    
    # 使用Render环境中应该存在的API密钥
    api_key = "SDMG58OJ6IXQTJHZ"  # 这是Render环境中设置的密钥
    
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': 'TSLA',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        log_message(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'bestMatches' in data:
                matches = data['bestMatches']
                log_message(f"✅ API调用成功，找到 {len(matches)} 个匹配")
                if matches:
                    first_match = matches[0]
                    symbol = first_match.get('1. symbol', 'N/A')
                    name = first_match.get('2. name', 'N/A')
                    log_message(f"  第一个匹配: {symbol} - {name}")
                return True
            else:
                log_message(f"❌ API响应格式异常: {data}")
                return False
        else:
            log_message(f"❌ API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        log_message(f"❌ API调用异常: {str(e)}")
        return False

def test_callback_with_debug():
    """测试回调函数并尝试获取详细错误信息"""
    log_message("\n=== 测试回调函数（详细调试） ===")
    
    base_url = "https://ifinance-ggqe.onrender.com"
    
    # 构造回调请求
    callback_data = {
        "output": "search-results.children",
        "outputs": [{"id": "search-results", "property": "children"}],
        "inputs": [{"id": "search-button", "property": "n_clicks", "value": 1}],
        "state": [{"id": "stock-search-input", "property": "value", "value": "TSLA"}],
        "changedPropIds": ["search-button.n_clicks"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/_dash-update-component",
            json=callback_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        log_message(f"回调响应状态码: {response.status_code}")
        log_message(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                log_message(f"✅ 回调成功，响应数据: {str(result)[:200]}...")
                return True
            except:
                log_message(f"⚠️  回调响应解析失败: {response.text[:500]}")
                return False
        elif response.status_code == 500:
            log_message("❌ 回调函数内部错误 (500)")
            error_content = response.text
            log_message(f"错误内容: {error_content[:1000]}")
            
            # 尝试从错误页面提取有用信息
            if 'Traceback' in error_content:
                log_message("⚠️  检测到Python异常信息")
            if 'ImportError' in error_content:
                log_message("⚠️  可能是导入错误")
            if 'KeyError' in error_content:
                log_message("⚠️  可能是配置或数据访问错误")
            if 'ConnectionError' in error_content:
                log_message("⚠️  可能是网络连接错误")
                
            return False
        else:
            log_message(f"❌ 回调请求失败: {response.status_code}")
            log_message(f"响应内容: {response.text[:500]}")
            return False
            
    except Exception as e:
        log_message(f"❌ 回调请求异常: {str(e)}")
        return False

def test_simple_callback():
    """测试简化的回调请求"""
    log_message("\n=== 测试简化回调请求 ===")
    
    base_url = "https://ifinance-ggqe.onrender.com"
    
    # 更简单的回调数据
    simple_callback = {
        "inputs": [{"id": "search-button", "property": "n_clicks", "value": 1}],
        "state": [{"id": "stock-search-input", "property": "value", "value": "AAPL"}]
    }
    
    try:
        response = requests.post(
            f"{base_url}/_dash-update-component",
            json=simple_callback,
            headers={'Content-Type': 'application/json'},
            timeout=20
        )
        
        log_message(f"简化回调状态码: {response.status_code}")
        
        if response.status_code == 200:
            log_message("✅ 简化回调成功")
            return True
        else:
            log_message(f"❌ 简化回调失败: {response.status_code}")
            log_message(f"错误响应: {response.text[:300]}")
            return False
            
    except Exception as e:
        log_message(f"❌ 简化回调异常: {str(e)}")
        return False

def check_render_environment_info():
    """检查Render环境信息"""
    log_message("\n=== 检查Render环境信息 ===")
    
    # 检查本地环境变量（模拟）
    log_message("本地环境变量:")
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '未设置')
    if api_key != '未设置':
        masked_key = api_key[:8] + '...' if len(api_key) > 8 else '***'
        log_message(f"  ALPHA_VANTAGE_API_KEY: {masked_key}")
    else:
        log_message(f"  ALPHA_VANTAGE_API_KEY: {api_key}")
    
    render_env = os.environ.get('RENDER', '未设置')
    log_message(f"  RENDER: {render_env}")
    
    port = os.environ.get('PORT', '未设置')
    log_message(f"  PORT: {port}")

def main():
    """主函数"""
    log_message("开始Render详细调试")
    log_message("=" * 60)
    
    # 检查环境信息
    check_render_environment_info()
    
    # 测试主页
    main_page_ok = test_render_main_page()
    
    # 测试Dash布局
    layout_ok = test_dash_layout()
    
    # 直接测试API密钥
    api_ok = test_api_key_directly()
    
    # 测试回调函数
    callback_ok = test_callback_with_debug()
    
    # 测试简化回调
    simple_callback_ok = test_simple_callback()
    
    # 总结
    log_message("\n" + "=" * 60)
    log_message("=== 调试总结 ===")
    log_message(f"主页加载: {'✅ 正常' if main_page_ok else '❌ 异常'}")
    log_message(f"Dash布局: {'✅ 正常' if layout_ok else '❌ 异常'}")
    log_message(f"API密钥: {'✅ 有效' if api_ok else '❌ 无效'}")
    log_message(f"回调函数: {'✅ 正常' if callback_ok else '❌ 异常'}")
    log_message(f"简化回调: {'✅ 正常' if simple_callback_ok else '❌ 异常'}")
    
    if not callback_ok:
        log_message("\n=== 问题分析 ===")
        if main_page_ok and layout_ok and api_ok:
            log_message("应用基础功能正常，问题可能在于:")
            log_message("1. 回调函数内部逻辑错误")
            log_message("2. 数据处理或格式化问题")
            log_message("3. 异常处理不当")
        elif not api_ok:
            log_message("API密钥问题，需要检查Render环境变量配置")
        else:
            log_message("应用基础功能异常，需要检查部署配置")
    else:
        log_message("\n✅ 所有测试通过，应用运行正常！")

if __name__ == "__main__":
    main()