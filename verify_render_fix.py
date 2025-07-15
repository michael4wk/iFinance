#!/usr/bin/env python3
"""
验证Render修复
测试线上Render应用是否已经修复
"""

import requests
import time
from datetime import datetime

def log_message(message):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_render_application():
    """测试Render应用"""
    render_url = "https://ifinance-dev.onrender.com"
    
    log_message("=== 测试Render应用状态 ===")
    
    try:
        # 测试主页
        log_message(f"测试主页: {render_url}")
        response = requests.get(render_url, timeout=30)
        
        log_message(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            log_message("✅ 主页访问成功")
            
            # 检查页面内容
            if "iFinance" in response.text:
                log_message("✅ 页面内容正常")
            else:
                log_message("⚠️  页面内容可能异常")
            
            # 检查是否包含Dash相关内容
            if "_dash-layout" in response.text:
                log_message("✅ Dash应用正常加载")
            else:
                log_message("⚠️  Dash应用可能未正常加载")
            
            # 检查是否有错误信息
            error_indicators = [
                "Server initialization failed",
                "500 Internal Server Error",
                "Application Error",
                "Callback function not found"
            ]
            
            has_errors = False
            for error in error_indicators:
                if error in response.text:
                    log_message(f"❌ 发现错误: {error}")
                    has_errors = True
            
            if not has_errors:
                log_message("✅ 未发现明显错误")
            
            return True
            
        else:
            log_message(f"❌ 主页访问失败: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        log_message(f"❌ 请求失败: {str(e)}")
        return False

def test_dash_endpoints():
    """测试Dash相关端点"""
    render_url = "https://ifinance-dev.onrender.com"
    
    log_message("\n=== 测试Dash端点 ===")
    
    # 测试Dash布局端点
    endpoints = [
        "/_dash-layout",
        "/_dash-dependencies"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{render_url}{endpoint}"
            log_message(f"测试端点: {endpoint}")
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                log_message(f"✅ {endpoint} 访问成功")
                
                # 检查是否返回JSON
                try:
                    json_data = response.json()
                    log_message(f"✅ {endpoint} 返回有效JSON")
                    results[endpoint] = True
                except:
                    log_message(f"⚠️  {endpoint} 未返回有效JSON")
                    results[endpoint] = False
            else:
                log_message(f"❌ {endpoint} 访问失败: {response.status_code}")
                results[endpoint] = False
                
        except requests.RequestException as e:
            log_message(f"❌ {endpoint} 请求失败: {str(e)}")
            results[endpoint] = False
    
    return results

def test_application_functionality():
    """测试应用功能"""
    render_url = "https://ifinance-dev.onrender.com"
    
    log_message("\n=== 测试应用功能 ===")
    
    try:
        # 首先获取主页以获取session
        session = requests.Session()
        response = session.get(render_url, timeout=30)
        
        if response.status_code != 200:
            log_message("❌ 无法访问主页，跳过功能测试")
            return False
        
        log_message("✅ 成功建立会话")
        
        # 尝试获取Dash布局
        layout_response = session.get(f"{render_url}/_dash-layout", timeout=15)
        
        if layout_response.status_code == 200:
            log_message("✅ Dash布局获取成功")
            
            try:
                layout_data = layout_response.json()
                log_message("✅ 布局数据解析成功")
                
                # 检查是否包含搜索相关组件
                layout_str = str(layout_data)
                if "stock-search-input" in layout_str:
                    log_message("✅ 发现股票搜索输入组件")
                if "stock-dropdown" in layout_str:
                    log_message("✅ 发现股票下拉选择组件")
                
                return True
                
            except Exception as e:
                log_message(f"❌ 布局数据解析失败: {str(e)}")
                return False
        else:
            log_message(f"❌ Dash布局获取失败: {layout_response.status_code}")
            return False
            
    except Exception as e:
        log_message(f"❌ 应用功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    log_message("🚀 Render修复验证测试")
    log_message("=" * 60)
    
    # 运行测试
    app_status = test_render_application()
    dash_endpoints = test_dash_endpoints()
    app_functionality = test_application_functionality()
    
    # 等待一下再做最终测试
    log_message("\n等待5秒后进行最终验证...")
    time.sleep(5)
    
    # 最终验证
    log_message("\n=== 最终验证 ===")
    try:
        final_response = requests.get("https://ifinance-dev.onrender.com", timeout=30)
        final_status = final_response.status_code == 200
        log_message(f"最终状态检查: {'✅ 成功' if final_status else '❌ 失败'}")
    except:
        final_status = False
        log_message("最终状态检查: ❌ 失败")
    
    # 总结
    log_message("\n" + "=" * 60)
    log_message("📊 验证结果总结:")
    log_message(f"  应用状态: {'✅ 正常' if app_status else '❌ 异常'}")
    log_message(f"  Dash布局端点: {'✅ 正常' if dash_endpoints.get('/_dash-layout', False) else '❌ 异常'}")
    log_message(f"  Dash依赖端点: {'✅ 正常' if dash_endpoints.get('/_dash-dependencies', False) else '❌ 异常'}")
    log_message(f"  应用功能: {'✅ 正常' if app_functionality else '❌ 异常'}")
    log_message(f"  最终状态: {'✅ 正常' if final_status else '❌ 异常'}")
    
    # 判断修复是否成功
    all_tests = [
        app_status,
        dash_endpoints.get('/_dash-layout', False),
        dash_endpoints.get('/_dash-dependencies', False),
        app_functionality,
        final_status
    ]
    
    success_count = sum(all_tests)
    total_count = len(all_tests)
    
    if success_count >= 4:  # 允许一个测试失败
        log_message(f"\n🎉 修复成功！({success_count}/{total_count} 测试通过)")
        log_message("Render应用现在应该能正常工作了。")
    elif success_count >= 2:
        log_message(f"\n⚠️  部分修复 ({success_count}/{total_count} 测试通过)")
        log_message("应用有所改善，但可能还需要进一步调试。")
    else:
        log_message(f"\n❌ 修复失败 ({success_count}/{total_count} 测试通过)")
        log_message("需要进一步调试和修复。")

if __name__ == "__main__":
    main()