#!/usr/bin/env python3
"""
Render部署最终诊断脚本
全面检查Render部署状态和可能的问题
"""

import requests
import json
import time
from datetime import datetime

RENDER_URL = "https://ifinance-latest.onrender.com"
ALTERNATE_URLS = [
    "https://ifinance-latest.onrender.com",
    "https://ifinance.onrender.com",
    "https://ifinance-dev.onrender.com"
]

def log_with_time(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_url_variations():
    log_with_time("=== 测试不同URL变体 ===")
    
    for url in ALTERNATE_URLS:
        try:
            log_with_time(f"测试URL: {url}")
            response = requests.get(url, timeout=10)
            log_with_time(f"  状态码: {response.status_code}")
            log_with_time(f"  响应头: {dict(response.headers)}")
            if response.status_code == 200:
                log_with_time(f"  ✅ 成功响应: {response.text[:200]}...")
                return url
            else:
                log_with_time(f"  ❌ 失败响应: {response.text[:100]}")
        except Exception as e:
            log_with_time(f"  ❌ 请求异常: {e}")
        log_with_time("")
    
    return None

def test_render_service_status():
    log_with_time("=== 检查Render服务状态 ===")
    
    # 测试基本连接
    try:
        response = requests.get(RENDER_URL, timeout=30)
        log_with_time(f"基本连接状态码: {response.status_code}")
        log_with_time(f"响应时间: {response.elapsed.total_seconds():.2f}秒")
        
        headers = dict(response.headers)
        log_with_time("重要响应头:")
        important_headers = ['server', 'x-render-routing', 'cf-ray', 'content-type']
        for header in important_headers:
            if header in headers:
                log_with_time(f"  {header}: {headers[header]}")
        
        # 检查是否是Cloudflare错误页面
        if 'cloudflare' in headers.get('server', '').lower():
            log_with_time("⚠️  检测到Cloudflare，可能是代理层问题")
        
        # 检查x-render-routing
        routing = headers.get('x-render-routing', '')
        if routing == 'no-server':
            log_with_time("❌ Render报告：没有检测到运行的服务器")
        elif routing:
            log_with_time(f"ℹ️  Render路由状态: {routing}")
        
    except requests.exceptions.Timeout:
        log_with_time("❌ 请求超时 - 服务器可能未响应")
    except requests.exceptions.ConnectionError:
        log_with_time("❌ 连接错误 - 服务器可能未运行")
    except Exception as e:
        log_with_time(f"❌ 其他错误: {e}")

def test_health_endpoints():
    log_with_time("=== 测试常见健康检查端点 ===")
    
    health_endpoints = [
        "/",
        "/health",
        "/ping",
        "/_dash-layout",
        "/status"
    ]
    
    for endpoint in health_endpoints:
        try:
            url = f"{RENDER_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            log_with_time(f"{endpoint}: {response.status_code}")
            if response.status_code != 404:
                log_with_time(f"  响应: {response.text[:100]}")
        except Exception as e:
            log_with_time(f"{endpoint}: 异常 - {e}")

def check_deployment_timing():
    log_with_time("=== 检查部署时间 ===")
    
    # 多次请求检查一致性
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.get(RENDER_URL, timeout=15)
            end_time = time.time()
            
            log_with_time(f"请求 {i+1}: 状态码 {response.status_code}, 响应时间 {end_time-start_time:.2f}秒")
            
            # 检查是否有部署相关的头信息
            headers = dict(response.headers)
            deploy_headers = ['x-render-deploy-id', 'x-render-service-id', 'date']
            for header in deploy_headers:
                if header in headers:
                    log_with_time(f"  {header}: {headers[header]}")
            
            time.sleep(2)
        except Exception as e:
            log_with_time(f"请求 {i+1}: 异常 - {e}")

def main():
    log_with_time("开始Render部署最终诊断")
    log_with_time("="*60)
    
    # 测试URL变体
    working_url = test_url_variations()
    
    log_with_time("")
    # 测试服务状态
    test_render_service_status()
    
    log_with_time("")
    # 测试健康检查端点
    test_health_endpoints()
    
    log_with_time("")
    # 检查部署时间
    check_deployment_timing()
    
    log_with_time("")
    log_with_time("=== 诊断总结 ===")
    if working_url:
        log_with_time(f"✅ 找到工作的URL: {working_url}")
    else:
        log_with_time("❌ 所有测试的URL都无法正常工作")
        log_with_time("")
        log_with_time("可能的问题:")
        log_with_time("1. Render服务未正确启动")
        log_with_time("2. Procfile配置错误")
        log_with_time("3. 应用代码存在启动错误")
        log_with_time("4. 依赖安装失败")
        log_with_time("5. 环境变量配置问题")
        log_with_time("")
        log_with_time("建议检查Render控制台的部署日志")

if __name__ == "__main__":
    main()