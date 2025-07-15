#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试推送修复后的 Render 应用功能
验证部署是否成功以及应用是否正常工作
"""

import requests
import json
import time
from typing import Dict, Any

# Render 应用 URL
RENDER_URL = "https://ifinance-dev.onrender.com"

def test_main_page() -> bool:
    """
    测试主页是否可以访问
    """
    try:
        print("\n=== 测试主页访问 ===")
        response = requests.get(RENDER_URL, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 主页访问成功 (状态码: {response.status_code})")
            
            # 检查关键组件
            content = response.text
            if 'stock-search-input' in content and 'stock-dropdown' in content:
                print("✅ 关键 UI 组件存在")
                return True
            else:
                print("❌ 关键 UI 组件缺失")
                return False
        else:
            print(f"❌ 主页访问失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 主页访问异常: {e}")
        return False

def test_dash_endpoints() -> bool:
    """
    测试 Dash 关键端点
    """
    try:
        print("\n=== 测试 Dash 端点 ===")
        
        # 测试布局端点
        layout_response = requests.get(f"{RENDER_URL}/_dash-layout", timeout=30)
        if layout_response.status_code == 200:
            print("✅ /_dash-layout 端点正常")
        else:
            print(f"❌ /_dash-layout 端点失败 (状态码: {layout_response.status_code})")
            return False
            
        # 测试依赖端点
        deps_response = requests.get(f"{RENDER_URL}/_dash-dependencies", timeout=30)
        if deps_response.status_code == 200:
            print("✅ /_dash-dependencies 端点正常")
            return True
        else:
            print(f"❌ /_dash-dependencies 端点失败 (状态码: {deps_response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Dash 端点测试异常: {e}")
        return False

def test_stock_search_functionality() -> bool:
    """
    测试股票搜索功能
    """
    try:
        print("\n=== 测试股票搜索功能 ===")
        
        # 模拟搜索请求
        search_data = {
            "output": "stock-dropdown.options",
            "outputs": [{"id": "stock-dropdown", "property": "options"}],
            "inputs": [{"id": "stock-search-input", "property": "value", "value": "AAPL"}],
            "changedPropIds": ["stock-search-input.value"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        response = requests.post(
            f"{RENDER_URL}/_dash-update-component",
            json=search_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'response' in result and 'stock-dropdown' in result['response']:
                    options = result['response']['stock-dropdown']['options']
                    print(f"✅ 搜索功能正常，找到 {len(options)} 个结果")
                    
                    # 显示前几个结果
                    if options:
                        print("   前几个搜索结果:")
                        for i, option in enumerate(options[:3]):
                            print(f"   - {option.get('label', 'N/A')} ({option.get('value', 'N/A')})")
                    
                    return True
                else:
                    print("❌ 搜索响应格式异常")
                    print(f"   响应内容: {result}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ 搜索响应不是有效的 JSON")
                print(f"   响应内容: {response.text[:200]}...")
                return False
        else:
            print(f"❌ 搜索请求失败 (状态码: {response.status_code})")
            print(f"   响应内容: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 股票搜索功能测试异常: {e}")
        return False

def test_callback_registration() -> bool:
    """
    测试回调函数是否正确注册
    """
    try:
        print("\n=== 测试回调函数注册 ===")
        
        # 获取依赖信息
        response = requests.get(f"{RENDER_URL}/_dash-dependencies", timeout=30)
        
        if response.status_code == 200:
            deps = response.json()
            
            # 检查是否有回调函数注册
            if deps and len(deps) > 0:
                print(f"✅ 发现 {len(deps)} 个已注册的回调函数")
                
                # 检查关键回调
                stock_search_callback = False
                for dep in deps:
                    if 'output' in dep and 'stock-dropdown' in str(dep['output']):
                        stock_search_callback = True
                        break
                
                if stock_search_callback:
                    print("✅ 股票搜索回调函数已正确注册")
                    return True
                else:
                    print("❌ 股票搜索回调函数未找到")
                    return False
            else:
                print("❌ 未发现任何已注册的回调函数")
                return False
        else:
            print(f"❌ 获取依赖信息失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 回调函数注册测试异常: {e}")
        return False

def main():
    """
    主测试函数
    """
    print("🚀 开始测试推送修复后的 Render 应用...")
    print(f"📍 测试 URL: {RENDER_URL}")
    
    # 执行所有测试
    tests = [
        ("主页访问", test_main_page),
        ("Dash 端点", test_dash_endpoints),
        ("回调函数注册", test_callback_registration),
        ("股票搜索功能", test_stock_search_functionality)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 正在测试: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试 {test_name} 时发生异常: {e}")
            results[test_name] = False
        
        # 测试间隔
        time.sleep(1)
    
    # 汇总结果
    print("\n" + "="*50)
    print("📊 测试结果汇总")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Render 应用修复成功！")
        print("\n✨ 应用现在可以正常使用了")
        print(f"🌐 访问地址: {RENDER_URL}")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，需要进一步检查")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)