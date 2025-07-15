#!/usr/bin/env python3
"""
测试简单Flask服务器在Render上的运行状态
"""

import requests
import json
from datetime import datetime

RENDER_URL = "https://ifinance-latest.onrender.com"

def log_with_time(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_simple_server():
    log_with_time("=== 测试简单Flask服务器 ===")
    
    # 测试主页
    try:
        response = requests.get(f"{RENDER_URL}/", timeout=10)
        log_with_time(f"主页状态码: {response.status_code}")
        if response.status_code == 200:
            log_with_time(f"✅ 主页响应: {response.text}")
        else:
            log_with_time(f"❌ 主页失败: {response.text}")
    except Exception as e:
        log_with_time(f"❌ 主页请求异常: {e}")
    
    # 测试健康检查
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        log_with_time(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            log_with_time(f"✅ 健康检查: {response.json()}")
        else:
            log_with_time(f"❌ 健康检查失败: {response.text}")
    except Exception as e:
        log_with_time(f"❌ 健康检查异常: {e}")
    
    # 测试环境信息
    try:
        response = requests.get(f"{RENDER_URL}/env", timeout=10)
        log_with_time(f"环境信息状态码: {response.status_code}")
        if response.status_code == 200:
            env_data = response.json()
            log_with_time(f"✅ 环境信息:")
            for key, value in env_data.items():
                log_with_time(f"  {key}: {value}")
        else:
            log_with_time(f"❌ 环境信息失败: {response.text}")
    except Exception as e:
        log_with_time(f"❌ 环境信息异常: {e}")

if __name__ == "__main__":
    test_simple_server()