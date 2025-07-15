#!/usr/bin/env python3
"""
测试Render部署修复
验证修复后的main.py是否能正确处理gunicorn启动
"""

import sys
import subprocess
import time
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_server_import():
    """测试server对象导入"""
    print("=== 测试server对象导入 ===")
    try:
        from src.main import server
        print(f"✅ server对象导入成功: {type(server)}")
        print(f"✅ server是Flask应用: {hasattr(server, 'url_map')}")
        
        # 检查路由
        routes = list(server.url_map.iter_rules())
        print(f"✅ 注册的路由数量: {len(routes)}")
        
        # 显示前几个路由
        print("前5个路由:")
        for i, rule in enumerate(routes[:5], 1):
            print(f"  {i}. {rule.rule} -> {rule.endpoint}")
        
        return True
    except Exception as e:
        print(f"❌ server对象导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_gunicorn_startup():
    """测试gunicorn启动"""
    print("\n=== 测试gunicorn启动 ===")
    
    # 启动gunicorn服务器
    port = 8052
    cmd = [
        "gunicorn",
        "--bind", f"127.0.0.1:{port}",
        "--workers", "1",
        "--timeout", "30",
        "--preload",  # 预加载应用
        "src.main:server"
    ]
    
    print(f"启动命令: {' '.join(cmd)}")
    
    try:
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root)
        )
        
        # 等待启动
        print("等待服务器启动...")
        time.sleep(5)
        
        # 检查进程状态
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ gunicorn启动失败")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False
        
        # 测试HTTP请求
        try:
            response = requests.get(f"http://127.0.0.1:{port}", timeout=10)
            print(f"✅ HTTP请求成功: {response.status_code}")
            
            # 检查响应内容
            if "iFinance" in response.text:
                print("✅ 应用页面加载正常")
            else:
                print("⚠️  应用页面内容异常")
            
            success = True
        except requests.RequestException as e:
            print(f"❌ HTTP请求失败: {str(e)}")
            success = False
        
        # 停止进程
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        return success
        
    except Exception as e:
        print(f"❌ gunicorn测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_simulation():
    """模拟Render环境"""
    print("\n=== 模拟Render环境测试 ===")
    
    import os
    
    # 保存原始环境变量
    original_env = {
        'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
        'RENDER': os.environ.get('RENDER'),
        'PORT': os.environ.get('PORT')
    }
    
    try:
        # 设置Render环境变量
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['RENDER'] = 'true'
        os.environ['PORT'] = '8053'
        
        print("设置Render环境变量:")
        print(f"  ENVIRONMENT: {os.environ.get('ENVIRONMENT')}")
        print(f"  RENDER: {os.environ.get('RENDER')}")
        print(f"  PORT: {os.environ.get('PORT')}")
        
        # 重新导入server对象
        import importlib
        import src.main
        importlib.reload(src.main)
        
        from src.main import server
        print(f"✅ Render环境下server对象创建成功: {type(server)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Render环境模拟失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

def test_callback_registration():
    """测试回调函数注册"""
    print("\n=== 测试回调函数注册 ===")
    
    try:
        from src.main import server
        
        # 获取Dash应用实例
        # 在Flask应用中查找Dash应用
        dash_app = None
        for rule in server.url_map.iter_rules():
            if rule.endpoint.startswith('_dash'):
                # 找到Dash相关的路由，说明Dash应用已注册
                dash_app = True
                break
        
        if dash_app:
            print("✅ Dash应用已正确注册到Flask服务器")
            
            # 检查是否有回调相关的路由
            callback_routes = [rule for rule in server.url_map.iter_rules() 
                             if '_dash-dependencies' in rule.rule or '_dash-layout' in rule.rule]
            print(f"✅ 发现 {len(callback_routes)} 个Dash回调相关路由")
            
            return True
        else:
            print("❌ 未找到Dash应用注册")
            return False
            
    except Exception as e:
        print(f"❌ 回调函数注册测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 Render部署修复测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("server对象导入", test_server_import),
        ("回调函数注册", test_callback_registration),
        ("Render环境模拟", test_environment_simulation),
        ("gunicorn启动", test_gunicorn_startup),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    for test_name, result in results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 所有测试通过 ({success_count}/{total_count})！")
        print("修复应该能解决Render部署问题。")
    else:
        print(f"\n⚠️  部分测试失败 ({success_count}/{total_count})")
        print("需要进一步调试。")

if __name__ == "__main__":
    main()