#!/usr/bin/env python3
"""
Render线上环境实时测试脚本
用于诊断Render部署环境中的Dash应用问题
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Render应用URL
RENDER_APP_URL = "https://ifinance-dev.onrender.com"

def log_message(message: str):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_render_app_health():
    """测试Render应用的基本健康状态"""
    log_message("=== 测试Render应用健康状态 ===")
    
    try:
        response = requests.get(f"{RENDER_APP_URL}/", timeout=30)
        log_message(f"应用首页状态码: {response.status_code}")
        
        if response.status_code == 200:
            log_message("✅ Render应用正常运行")
            
            # 检查响应内容是否包含Dash应用的关键元素
            content = response.text
            if "iFinance" in content and "dash" in content.lower():
                log_message("✅ Dash应用内容正常加载")
                return True
            else:
                log_message("⚠️ 应用内容可能异常")
                return False
        else:
            log_message(f"❌ Render应用响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_message(f"❌ 无法连接到Render应用: {e}")
        return False

def test_dash_layout():
    """测试Dash应用的布局加载"""
    log_message("=== 测试Dash布局加载 ===")
    
    try:
        # 测试Dash布局端点
        layout_url = f"{RENDER_APP_URL}/_dash-layout"
        response = requests.get(layout_url, timeout=30)
        
        log_message(f"布局端点状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                layout_data = response.json()
                log_message("✅ Dash布局加载成功")
                log_message(f"布局数据类型: {type(layout_data)}")
                return True
            except json.JSONDecodeError:
                log_message("❌ 布局数据JSON解析失败")
                return False
        else:
            log_message(f"❌ 布局加载失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_message(f"❌ 布局请求失败: {e}")
        return False

def test_dash_dependencies():
    """测试Dash依赖关系"""
    log_message("=== 测试Dash依赖关系 ===")
    
    try:
        # 测试Dash依赖端点
        deps_url = f"{RENDER_APP_URL}/_dash-dependencies"
        response = requests.get(deps_url, timeout=30)
        
        log_message(f"依赖端点状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                deps_data = response.json()
                log_message("✅ Dash依赖关系加载成功")
                log_message(f"依赖数量: {len(deps_data) if isinstance(deps_data, list) else 'N/A'}")
                return True
            except json.JSONDecodeError:
                log_message("❌ 依赖数据JSON解析失败")
                return False
        else:
            log_message(f"❌ 依赖加载失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_message(f"❌ 依赖请求失败: {e}")
        return False

def simulate_stock_search(search_term: str = "TSLA"):
    """模拟股票搜索操作"""
    log_message(f"=== 模拟股票搜索: {search_term} ===")
    
    try:
        # 模拟Dash回调请求
        callback_url = f"{RENDER_APP_URL}/_dash-update-component"
        
        # 构造回调请求数据（模拟搜索按钮点击）
        callback_data = {
            "output": "stock-dropdown.options",
            "outputs": [
                {"id": "stock-dropdown", "property": "options"},
                {"id": "stock-dropdown", "property": "value"},
                {"id": "selected-stock-info", "property": "data"},
                {"id": "error-container", "property": "children"}
            ],
            "inputs": [
                {"id": "search-button", "property": "n_clicks", "value": 1}
            ],
            "state": [
                {"id": "stock-search-input", "property": "value", "value": search_term}
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        log_message(f"发送回调请求: {search_term}")
        response = requests.post(
            callback_url, 
            json=callback_data, 
            headers=headers, 
            timeout=30
        )
        
        log_message(f"回调响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                log_message("✅ 股票搜索回调成功")
                
                # 分析回调结果
                if isinstance(result, dict) and "response" in result:
                    response_data = result["response"]
                    if isinstance(response_data, dict):
                        # 检查搜索结果
                        options = response_data.get("stock-dropdown", {}).get("options", [])
                        if options:
                            log_message(f"✅ 找到 {len(options)} 个搜索结果")
                            for i, option in enumerate(options[:3]):
                                log_message(f"  结果{i+1}: {option.get('label', 'N/A')}")
                            return True
                        else:
                            log_message("❌ 搜索返回空结果")
                            
                            # 检查错误信息
                            error_info = response_data.get("error-container", {})
                            if error_info:
                                log_message(f"错误信息: {error_info}")
                            return False
                    else:
                        log_message(f"❌ 回调响应格式异常: {type(response_data)}")
                        return False
                else:
                    log_message(f"❌ 回调结果格式异常: {result}")
                    return False
                    
            except json.JSONDecodeError as e:
                log_message(f"❌ 回调结果JSON解析失败: {e}")
                log_message(f"原始响应: {response.text[:500]}")
                return False
        else:
            log_message(f"❌ 回调请求失败: {response.status_code}")
            log_message(f"错误响应: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_message(f"❌ 回调请求异常: {e}")
        return False

def test_render_logs():
    """检查可能的错误信息"""
    log_message("=== 检查应用错误信息 ===")
    
    # 尝试访问一些可能暴露错误信息的端点
    test_endpoints = [
        "/health",
        "/status",
        "/_dash-config",
        "/favicon.ico"
    ]
    
    for endpoint in test_endpoints:
        try:
            url = f"{RENDER_APP_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            log_message(f"端点 {endpoint}: {response.status_code}")
            
            if response.status_code == 500:
                log_message(f"  ⚠️ 服务器错误: {response.text[:200]}")
                
        except requests.exceptions.RequestException:
            log_message(f"端点 {endpoint}: 无法访问")
        
        time.sleep(0.5)

def analyze_render_environment():
    """分析Render环境的详细信息"""
    log_message("=== 分析Render环境 ===")
    
    # 测试不同的搜索关键词
    test_keywords = ["TSLA", "AAPL", "MSFT"]
    
    successful_searches = 0
    total_searches = len(test_keywords)
    
    for keyword in test_keywords:
        log_message(f"\n--- 测试搜索: {keyword} ---")
        if simulate_stock_search(keyword):
            successful_searches += 1
        time.sleep(3)  # 避免请求过快
    
    success_rate = (successful_searches / total_searches) * 100
    log_message(f"\n搜索成功率: {success_rate:.1f}% ({successful_searches}/{total_searches})")
    
    return success_rate

def main():
    """主测试函数"""
    log_message("开始Render线上环境诊断测试")
    log_message(f"目标应用: {RENDER_APP_URL}")
    log_message("="*60)
    
    # 1. 测试应用健康状态
    if not test_render_app_health():
        log_message("❌ 应用健康检查失败，终止测试")
        return
    
    time.sleep(2)
    
    # 2. 测试Dash组件
    dash_layout_ok = test_dash_layout()
    time.sleep(1)
    dash_deps_ok = test_dash_dependencies()
    time.sleep(1)
    
    if not dash_layout_ok or not dash_deps_ok:
        log_message("⚠️ Dash组件加载异常，但继续测试搜索功能")
    
    # 3. 检查错误信息
    test_render_logs()
    time.sleep(2)
    
    # 4. 分析搜索功能
    success_rate = analyze_render_environment()
    
    # 5. 总结
    log_message("\n" + "="*60)
    log_message("=== 诊断总结 ===")
    
    if success_rate == 0:
        log_message("❌ 严重问题: 所有股票搜索均失败")
        log_message("可能原因:")
        log_message("  1. Render环境中的API密钥配置问题")
        log_message("  2. Alpha Vantage API调用失败")
        log_message("  3. Dash回调函数执行异常")
        log_message("  4. 应用依赖或环境问题")
    elif success_rate < 50:
        log_message(f"⚠️ 部分问题: 搜索成功率仅 {success_rate:.1f}%")
        log_message("建议检查API限制和网络连接")
    else:
        log_message(f"✅ 搜索功能基本正常: 成功率 {success_rate:.1f}%")
    
    log_message("\n诊断完成!")
    log_message("\n建议下一步:")
    log_message("1. 检查Render环境变量配置")
    log_message("2. 查看Render部署日志")
    log_message("3. 验证API密钥在Render环境中的可用性")

if __name__ == "__main__":
    main()