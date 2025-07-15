#!/usr/bin/env python3
"""
Render部署日志检查工具
检查Render应用的部署状态和可能的错误
"""

import requests
import json
import time
from datetime import datetime

def log_message(message):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_render_endpoints():
    """测试Render应用的各种端点"""
    base_url = "https://ifinance-ggqe.onrender.com"
    
    endpoints = [
        "/",
        "/_dash-layout", 
        "/_dash-dependencies",
        "/_dash-component-suites/dash/dcc/async-graph.js",
        "/_dash-component-suites/dash/dash_table/async-table.js",
        "/assets/style.css"
    ]
    
    log_message("开始测试Render端点")
    log_message("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            log_message(f"测试端点: {endpoint}")
            response = requests.get(url, timeout=10)
            log_message(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                log_message(f"  ✅ 成功 - Content-Type: {content_type}, 大小: {content_length} bytes")
                
                # 如果是HTML，检查是否包含Dash相关内容
                if 'text/html' in content_type:
                    content = response.text.lower()
                    if 'dash' in content:
                        log_message(f"  📱 检测到Dash内容")
                    if 'error' in content or 'exception' in content:
                        log_message(f"  ⚠️  检测到错误内容")
                        
            elif response.status_code == 404:
                log_message(f"  ❌ 404 - 端点不存在")
            elif response.status_code == 500:
                log_message(f"  💥 500 - 服务器内部错误")
                try:
                    error_content = response.text[:500]
                    log_message(f"  错误内容: {error_content}")
                except:
                    pass
            else:
                log_message(f"  ⚠️  状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            log_message(f"  ⏰ 超时")
        except requests.exceptions.ConnectionError:
            log_message(f"  🔌 连接错误")
        except Exception as e:
            log_message(f"  ❌ 异常: {str(e)}")
        
        time.sleep(0.5)  # 避免请求过快
    
    log_message("\n" + "=" * 50)

def test_gunicorn_compatibility():
    """测试gunicorn兼容性"""
    log_message("\n=== 测试Gunicorn兼容性 ===")
    
    try:
        # 尝试导入main模块
        import sys
        import os
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        log_message("尝试导入src.main模块...")
        import src.main as main_module
        
        log_message("✅ 成功导入src.main")
        
        # 检查server属性
        if hasattr(main_module, 'server'):
            log_message("✅ 找到server属性")
            server = main_module.server
            if server is not None:
                log_message(f"✅ server对象类型: {type(server)}")
            else:
                log_message("❌ server对象为None")
        else:
            log_message("❌ 未找到server属性")
            
        # 检查get_server函数
        if hasattr(main_module, 'get_server'):
            log_message("✅ 找到get_server函数")
            try:
                server = main_module.get_server()
                log_message(f"✅ get_server()返回: {type(server)}")
            except Exception as e:
                log_message(f"❌ get_server()调用失败: {str(e)}")
        else:
            log_message("❌ 未找到get_server函数")
            
    except ImportError as e:
        log_message(f"❌ 导入失败: {str(e)}")
    except Exception as e:
        log_message(f"❌ 其他错误: {str(e)}")

def check_environment_variables():
    """检查环境变量设置"""
    log_message("\n=== 检查环境变量 ===")
    
    import os
    
    # 检查关键环境变量
    env_vars = [
        'ALPHA_VANTAGE_API_KEY',
        'PORT',
        'RENDER',
        'PYTHON_VERSION'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'API_KEY' in var:
                # 隐藏API密钥的大部分内容
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                log_message(f"  {var}: {masked_value}")
            else:
                log_message(f"  {var}: {value}")
        else:
            log_message(f"  {var}: 未设置")

def main():
    """主函数"""
    log_message("开始Render部署诊断")
    log_message("=" * 60)
    
    # 检查环境变量
    check_environment_variables()
    
    # 测试gunicorn兼容性
    test_gunicorn_compatibility()
    
    # 测试Render端点
    test_render_endpoints()
    
    log_message("\n=== 诊断总结 ===")
    log_message("1. 检查上述输出中的错误信息")
    log_message("2. 如果所有端点都返回404，可能是应用启动失败")
    log_message("3. 如果导入失败，可能是依赖问题")
    log_message("4. 建议检查Render控制台的部署日志")

if __name__ == "__main__":
    main()