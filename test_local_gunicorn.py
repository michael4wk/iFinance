#!/usr/bin/env python3
"""
本地Gunicorn测试
模拟Render环境，测试gunicorn启动是否正常
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime

def log_message(message):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def setup_render_environment():
    """设置模拟Render环境变量"""
    log_message("=== 设置模拟Render环境 ===")
    
    # 设置Render环境变量
    os.environ['RENDER'] = 'true'
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'SDMG58OJ6IXQTJHZ'
    os.environ['PORT'] = '8050'
    os.environ['HOST'] = '0.0.0.0'
    os.environ['ENVIRONMENT'] = 'production'
    
    log_message("✅ 环境变量设置完成")
    log_message(f"  RENDER: {os.environ.get('RENDER')}")
    log_message(f"  API_KEY: {os.environ.get('ALPHA_VANTAGE_API_KEY')[:8]}...")
    log_message(f"  PORT: {os.environ.get('PORT')}")

def test_module_import():
    """测试模块导入"""
    log_message("\n=== 测试模块导入 ===")
    
    try:
        # 添加项目路径
        project_root = os.getcwd()
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        log_message("尝试导入src.main模块...")
        import src.main as main_module
        log_message("✅ 成功导入src.main")
        
        # 测试server属性
        if hasattr(main_module, 'server'):
            log_message("✅ 找到server属性")
            server = main_module.server
            
            if server is not None:
                log_message(f"✅ server对象类型: {type(server)}")
                
                # 测试server的基本属性
                if hasattr(server, 'run'):
                    log_message("✅ server具有run方法")
                if hasattr(server, 'wsgi_app'):
                    log_message("✅ server具有wsgi_app属性")
                    
                return True
            else:
                log_message("❌ server对象为None")
                return False
        else:
            log_message("❌ 未找到server属性")
            return False
            
    except Exception as e:
        log_message(f"❌ 模块导入失败: {str(e)}")
        import traceback
        log_message(f"详细错误: {traceback.format_exc()}")
        return False

def test_gunicorn_command():
    """测试gunicorn命令"""
    log_message("\n=== 测试Gunicorn命令 ===")
    
    # 构造gunicorn命令
    cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:8050',
        '--workers', '1',
        '--timeout', '120',
        '--check-config',  # 只检查配置，不启动
        'src.main:server'
    ]
    
    try:
        log_message(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        log_message(f"命令退出码: {result.returncode}")
        
        if result.returncode == 0:
            log_message("✅ Gunicorn配置检查通过")
            if result.stdout:
                log_message(f"输出: {result.stdout}")
            return True
        else:
            log_message("❌ Gunicorn配置检查失败")
            if result.stderr:
                log_message(f"错误: {result.stderr}")
            if result.stdout:
                log_message(f"输出: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("❌ Gunicorn命令超时")
        return False
    except FileNotFoundError:
        log_message("❌ 未找到gunicorn命令，请确保已安装")
        return False
    except Exception as e:
        log_message(f"❌ Gunicorn测试异常: {str(e)}")
        return False

def start_test_server():
    """启动测试服务器"""
    log_message("\n=== 启动测试服务器 ===")
    
    # 构造gunicorn启动命令
    cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:8050',
        '--workers', '1',
        '--timeout', '120',
        '--daemon',  # 后台运行
        '--pid', '/tmp/gunicorn_test.pid',
        'src.main:server'
    ]
    
    try:
        log_message(f"启动命令: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            log_message("✅ 服务器启动成功")
            time.sleep(3)  # 等待服务器完全启动
            return True
        else:
            log_message("❌ 服务器启动失败")
            if result.stderr:
                log_message(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"❌ 服务器启动异常: {str(e)}")
        return False

def test_local_server():
    """测试本地服务器"""
    log_message("\n=== 测试本地服务器 ===")
    
    base_url = "http://localhost:8050"
    
    try:
        # 测试主页
        response = requests.get(base_url, timeout=10)
        log_message(f"主页状态码: {response.status_code}")
        
        if response.status_code == 200:
            log_message("✅ 主页访问成功")
            
            # 测试Dash布局
            layout_response = requests.get(f"{base_url}/_dash-layout", timeout=10)
            log_message(f"布局端点状态码: {layout_response.status_code}")
            
            if layout_response.status_code == 200:
                log_message("✅ Dash布局正常")
                return True
            else:
                log_message("❌ Dash布局异常")
                return False
        else:
            log_message(f"❌ 主页访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        log_message(f"❌ 服务器测试异常: {str(e)}")
        return False

def stop_test_server():
    """停止测试服务器"""
    log_message("\n=== 停止测试服务器 ===")
    
    try:
        # 读取PID文件
        with open('/tmp/gunicorn_test.pid', 'r') as f:
            pid = int(f.read().strip())
        
        # 终止进程
        os.kill(pid, 15)  # SIGTERM
        time.sleep(2)
        
        # 清理PID文件
        os.remove('/tmp/gunicorn_test.pid')
        
        log_message("✅ 测试服务器已停止")
        
    except FileNotFoundError:
        log_message("⚠️  PID文件不存在，服务器可能未启动")
    except ProcessLookupError:
        log_message("⚠️  进程不存在，服务器可能已停止")
    except Exception as e:
        log_message(f"❌ 停止服务器异常: {str(e)}")

def main():
    """主函数"""
    log_message("开始本地Gunicorn测试")
    log_message("=" * 60)
    
    # 设置环境
    setup_render_environment()
    
    # 测试模块导入
    import_ok = test_module_import()
    
    if not import_ok:
        log_message("\n❌ 模块导入失败，无法继续测试")
        return
    
    # 测试gunicorn配置
    config_ok = test_gunicorn_command()
    
    if not config_ok:
        log_message("\n❌ Gunicorn配置检查失败")
        return
    
    # 启动测试服务器
    server_ok = start_test_server()
    
    if server_ok:
        # 测试服务器功能
        test_ok = test_local_server()
        
        # 停止服务器
        stop_test_server()
        
        # 总结
        log_message("\n" + "=" * 60)
        log_message("=== 测试总结 ===")
        log_message(f"模块导入: {'✅ 正常' if import_ok else '❌ 异常'}")
        log_message(f"Gunicorn配置: {'✅ 正常' if config_ok else '❌ 异常'}")
        log_message(f"服务器启动: {'✅ 正常' if server_ok else '❌ 异常'}")
        log_message(f"功能测试: {'✅ 正常' if test_ok else '❌ 异常'}")
        
        if import_ok and config_ok and server_ok and test_ok:
            log_message("\n✅ 所有测试通过！本地Gunicorn运行正常")
            log_message("问题可能在于Render环境配置或部署过程")
        else:
            log_message("\n❌ 存在问题，需要进一步调试")
    else:
        log_message("\n❌ 服务器启动失败，无法进行功能测试")

if __name__ == "__main__":
    main()