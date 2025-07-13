#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render部署环境的API连接
用于诊断生产环境中的API调用问题
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.api.alpha_vantage import AlphaVantageClient
    from src.utils.config import config
    from src.utils.logger import get_logger
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)

def test_environment_variables():
    """测试环境变量配置"""
    print("=== 环境变量检查 ===")
    
    # 检查API密钥
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if api_key:
        print(f"✅ ALPHA_VANTAGE_API_KEY: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
    else:
        print("❌ ALPHA_VANTAGE_API_KEY: 未设置")
    
    # 检查其他环境变量
    other_vars = ['DEBUG', 'LOG_LEVEL', 'HOST', 'PORT']
    for var in other_vars:
        value = os.getenv(var)
        print(f"{'✅' if value else '❌'} {var}: {value or '未设置'}")
    
    return bool(api_key)

def test_config_loading():
    """测试配置加载"""
    print("\n=== 配置加载检查 ===")
    
    try:
        api_key = config.get('ALPHA_VANTAGE_API_KEY')
        if api_key:
            print(f"✅ 配置加载成功: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
            return True
        else:
            print("❌ 配置中未找到API密钥")
            return False
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_api_client():
    """测试API客户端初始化"""
    print("\n=== API客户端检查 ===")
    
    try:
        client = AlphaVantageClient()
        print("✅ API客户端初始化成功")
        return client
    except Exception as e:
        print(f"❌ API客户端初始化失败: {e}")
        return None

def test_api_call(client):
    """测试API调用"""
    print("\n=== API调用测试 ===")
    
    if not client:
        print("❌ 无法测试API调用，客户端未初始化")
        return False
    
    try:
        # 测试搜索功能
        print("测试股票搜索...")
        results = client.search_symbols("AAPL")
        if results:
            print(f"✅ 搜索成功，找到 {len(results)} 个结果")
            print(f"第一个结果: {results[0].get('symbol', 'N/A')} - {results[0].get('name', 'N/A')}")
        else:
            print("⚠️ 搜索成功但无结果")
        
        # 测试数据获取
        print("\n测试数据获取...")
        data = client.get_daily_data("AAPL", "compact")
        if data and "time_series" in data and "meta_data" in data:
            time_series = data["time_series"]
            meta_data = data["meta_data"]
            if time_series:
                latest_date = list(time_series.keys())[0]
                latest_data = time_series[latest_date]
                print(f"✅ 数据获取成功")
                print(f"   股票代码: {meta_data.get('symbol', 'N/A')}")
                print(f"   最新日期: {latest_date}")
                print(f"   收盘价: ${latest_data.get('close', 'N/A')}")
                return True
            else:
                print("❌ 时间序列数据为空")
                return False
        else:
            print("❌ 数据获取失败或格式错误")
            print(f"   返回数据键: {list(data.keys()) if data else 'None'}")
            return False
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 Render部署环境API连接诊断")
    print("=" * 50)
    
    # 测试环境变量
    env_ok = test_environment_variables()
    
    # 测试配置加载
    config_ok = test_config_loading()
    
    # 测试API客户端
    client = test_api_client()
    
    # 测试API调用
    api_ok = test_api_call(client)
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 诊断结果总结:")
    print(f"环境变量: {'✅ 正常' if env_ok else '❌ 异常'}")
    print(f"配置加载: {'✅ 正常' if config_ok else '❌ 异常'}")
    print(f"API客户端: {'✅ 正常' if client else '❌ 异常'}")
    print(f"API调用: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    if not all([env_ok, config_ok, client, api_ok]):
        print("\n🚨 发现问题，请检查:")
        if not env_ok:
            print("- 在Render Dashboard中设置ALPHA_VANTAGE_API_KEY环境变量")
        if not config_ok:
            print("- 检查配置文件加载逻辑")
        if not client:
            print("- 检查API客户端初始化代码")
        if not api_ok:
            print("- 检查网络连接和API密钥有效性")
    else:
        print("\n🎉 所有测试通过！")

if __name__ == "__main__":
    main()