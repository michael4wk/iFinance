#!/usr/bin/env python3
"""
测试工作中的Render应用
使用正确的URL: https://ifinance-dev.onrender.com
"""

import requests
import json
from datetime import datetime

# 正确的Render URL
RENDER_URL = "https://ifinance-dev.onrender.com"

def log_with_time(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_main_page():
    log_with_time("=== 测试主页 ===")
    try:
        response = requests.get(RENDER_URL, timeout=10)
        log_with_time(f"主页状态码: {response.status_code}")
        if response.status_code == 200:
            log_with_time("✅ 主页加载成功")
            # 检查是否包含iFinance内容
            if "iFinance" in response.text:
                log_with_time("✅ 检测到iFinance应用")
            if "_dash" in response.text:
                log_with_time("✅ 检测到Dash框架")
            return True
        else:
            log_with_time(f"❌ 主页加载失败: {response.text[:100]}")
            return False
    except Exception as e:
        log_with_time(f"❌ 主页测试异常: {e}")
        return False

def test_dash_layout():
    log_with_time("\n=== 测试Dash布局 ===")
    try:
        response = requests.get(f"{RENDER_URL}/_dash-layout", timeout=10)
        log_with_time(f"布局端点状态码: {response.status_code}")
        if response.status_code == 200:
            log_with_time("✅ Dash布局加载成功")
            return True
        else:
            log_with_time(f"❌ Dash布局失败: {response.text[:100]}")
            return False
    except Exception as e:
        log_with_time(f"❌ Dash布局测试异常: {e}")
        return False

def test_stock_search_callback():
    log_with_time("\n=== 测试股票搜索回调 ===")
    
    callback_url = f"{RENDER_URL}/_dash-update-component"
    
    # 构造回调请求数据
    callback_data = {
        "output": "stock-dropdown.options",
        "outputs": [{"id": "stock-dropdown", "property": "options"}],
        "inputs": [{"id": "stock-search", "property": "value", "value": "AAPL"}],
        "changedPropIds": ["stock-search.value"],
        "state": []
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        log_with_time("发送AAPL搜索请求...")
        response = requests.post(
            callback_url,
            json=callback_data,
            headers=headers,
            timeout=15
        )
        
        log_with_time(f"回调响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                log_with_time("✅ 回调请求成功")
                
                # 检查响应结构
                if "response" in result:
                    options = result["response"].get("stock-dropdown", {}).get("options", [])
                    log_with_time(f"返回选项数量: {len(options)}")
                    
                    if len(options) > 0:
                        log_with_time("✅ 股票搜索功能正常")
                        for i, option in enumerate(options[:3]):
                            label = option.get('label', 'N/A')
                            value = option.get('value', 'N/A')
                            log_with_time(f"  选项{i+1}: {label} ({value})")
                        return True
                    else:
                        log_with_time("⚠️  搜索结果为空")
                        return False
                else:
                    log_with_time(f"❌ 响应格式异常: {result}")
                    return False
                    
            except json.JSONDecodeError:
                log_with_time("❌ 响应不是有效的JSON")
                log_with_time(f"响应内容: {response.text[:200]}...")
                return False
        else:
            log_with_time(f"❌ 回调请求失败: {response.status_code}")
            log_with_time(f"错误响应: {response.text[:200]}...")
            return False
            
    except Exception as e:
        log_with_time(f"❌ 回调测试异常: {e}")
        return False

def test_multiple_stocks():
    log_with_time("\n=== 测试多个股票搜索 ===")
    
    test_stocks = ["MSFT", "TSLA", "GOOGL"]
    callback_url = f"{RENDER_URL}/_dash-update-component"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    success_count = 0
    
    for stock in test_stocks:
        try:
            callback_data = {
                "output": "stock-dropdown.options",
                "outputs": [{"id": "stock-dropdown", "property": "options"}],
                "inputs": [{"id": "stock-search", "property": "value", "value": stock}],
                "changedPropIds": ["stock-search.value"],
                "state": []
            }
            
            log_with_time(f"测试股票: {stock}")
            response = requests.post(
                callback_url,
                json=callback_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "response" in result:
                    options = result["response"].get("stock-dropdown", {}).get("options", [])
                    log_with_time(f"  ✅ {stock}: 找到 {len(options)} 个选项")
                    success_count += 1
                else:
                    log_with_time(f"  ❌ {stock}: 响应格式错误")
            else:
                log_with_time(f"  ❌ {stock}: HTTP {response.status_code}")
                
        except Exception as e:
            log_with_time(f"  ❌ {stock}: 异常 - {e}")
    
    log_with_time(f"\n多股票测试结果: {success_count}/{len(test_stocks)} 成功")
    return success_count == len(test_stocks)

def main():
    log_with_time("开始测试工作中的Render应用")
    log_with_time(f"URL: {RENDER_URL}")
    log_with_time("="*60)
    
    # 运行所有测试
    tests = [
        ("主页加载", test_main_page),
        ("Dash布局", test_dash_layout),
        ("股票搜索回调", test_stock_search_callback),
        ("多股票搜索", test_multiple_stocks)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            log_with_time(f"❌ 测试 '{test_name}' 执行异常: {e}")
            results[test_name] = False
    
    # 总结结果
    log_with_time("\n" + "="*60)
    log_with_time("=== 测试总结 ===")
    
    passed_tests = 0
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        log_with_time(f"{test_name}: {status}")
        if passed:
            passed_tests += 1
    
    log_with_time(f"\n总体结果: {passed_tests}/{len(tests)} 测试通过")
    
    if passed_tests == len(tests):
        log_with_time("🎉 所有测试通过！应用运行正常")
    else:
        log_with_time("⚠️  部分测试失败，需要进一步调试")

if __name__ == "__main__":
    main()