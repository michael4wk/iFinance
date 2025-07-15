#!/usr/bin/env python3
"""
Render环境API调试脚本
专门用于诊断Render环境中的API密钥和Alpha Vantage API调用问题
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目模块
from src.utils.config import config
from src.api.alpha_vantage import AlphaVantageClient

def log_message(message: str):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_environment_variables():
    """检查环境变量配置"""
    log_message("=== 检查环境变量配置 ===")
    
    # 检查直接的环境变量
    api_key_env = os.getenv('ALPHA_VANTAGE_API_KEY')
    log_message(f"直接环境变量 ALPHA_VANTAGE_API_KEY: {'已设置' if api_key_env else '未设置'}")
    if api_key_env:
        log_message(f"API密钥长度: {len(api_key_env)}")
        log_message(f"API密钥前缀: {api_key_env[:8]}...")
    
    # 检查通过配置系统获取的API密钥
    try:
        config_api_key = config.get('ALPHA_VANTAGE_API_KEY')
        log_message(f"配置系统 API密钥: {'已获取' if config_api_key else '未获取'}")
        if config_api_key:
            log_message(f"配置API密钥长度: {len(config_api_key)}")
            log_message(f"配置API密钥前缀: {config_api_key[:8]}...")
            
            # 检查是否是demo密钥
            if config_api_key == "demo":
                log_message("⚠️ 检测到demo API密钥")
                return False
            elif len(config_api_key) < 10:
                log_message("⚠️ API密钥长度异常")
                return False
            else:
                log_message("✅ API密钥格式正常")
                return True
    except Exception as e:
        log_message(f"❌ 配置系统错误: {e}")
        return False
    
    return False

def test_direct_api_call():
    """直接测试Alpha Vantage API调用"""
    log_message("=== 直接API调用测试 ===")
    
    try:
        api_key = config.get('ALPHA_VANTAGE_API_KEY')
        if not api_key:
            log_message("❌ 无法获取API密钥")
            return False
        
        # 构造API请求
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': 'TSLA',
            'apikey': api_key
        }
        
        log_message(f"请求URL: {url}")
        log_message(f"请求参数: {dict(params, apikey='***')}")
        
        # 发送请求
        response = requests.get(url, params=params, timeout=30)
        log_message(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                log_message(f"响应数据类型: {type(data)}")
                log_message(f"响应键: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                
                # 检查响应内容
                if isinstance(data, dict):
                    if 'bestMatches' in data:
                        matches = data['bestMatches']
                        log_message(f"✅ 找到 {len(matches)} 个匹配结果")
                        for i, match in enumerate(matches[:3]):
                            symbol = match.get('1. symbol', 'N/A')
                            name = match.get('2. name', 'N/A')
                            log_message(f"  结果{i+1}: {symbol} - {name}")
                        return True
                    elif 'Error Message' in data:
                        log_message(f"❌ API错误: {data['Error Message']}")
                        return False
                    elif 'Note' in data:
                        log_message(f"⚠️ API限制: {data['Note']}")
                        return False
                    else:
                        log_message(f"❌ 未知响应格式: {data}")
                        return False
                else:
                    log_message(f"❌ 响应不是字典格式: {data}")
                    return False
                    
            except json.JSONDecodeError as e:
                log_message(f"❌ JSON解析失败: {e}")
                log_message(f"原始响应: {response.text[:500]}")
                return False
        else:
            log_message(f"❌ HTTP请求失败: {response.status_code}")
            log_message(f"错误响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        log_message(f"❌ API调用异常: {e}")
        return False

def test_alpha_vantage_client():
    """测试AlphaVantageClient类"""
    log_message("=== AlphaVantageClient测试 ===")
    
    try:
        # 创建客户端实例
        client = AlphaVantageClient()
        log_message("✅ AlphaVantageClient实例创建成功")
        
        # 测试搜索功能
        log_message("测试搜索功能: TSLA")
        results = client.search_symbols('TSLA')
        
        log_message(f"搜索结果类型: {type(results)}")
        log_message(f"搜索结果数量: {len(results) if isinstance(results, list) else 'N/A'}")
        
        if isinstance(results, list) and len(results) > 0:
            log_message("✅ 搜索成功")
            for i, result in enumerate(results[:3]):
                log_message(f"  结果{i+1}: {result}")
            return True
        else:
            log_message("❌ 搜索返回空结果")
            return False
            
    except Exception as e:
        log_message(f"❌ AlphaVantageClient测试失败: {e}")
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}")
        return False

def test_render_specific_issues():
    """测试Render环境特有的问题"""
    log_message("=== Render环境特有问题检查 ===")
    
    # 检查是否在Render环境中
    render_env = os.getenv('RENDER')
    log_message(f"RENDER环境变量: {render_env}")
    
    # 检查其他可能相关的环境变量
    env_vars = [
        'ENVIRONMENT',
        'DEBUG',
        'TZ',
        'PYTHON_VERSION',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        log_message(f"{var}: {value if value else '未设置'}")
    
    # 检查网络连接
    log_message("\n--- 网络连接测试 ---")
    try:
        response = requests.get('https://www.alphavantage.co', timeout=10)
        log_message(f"Alpha Vantage网站连接: {response.status_code}")
    except Exception as e:
        log_message(f"❌ 网络连接失败: {e}")
    
    # 检查DNS解析
    try:
        import socket
        ip = socket.gethostbyname('www.alphavantage.co')
        log_message(f"DNS解析成功: www.alphavantage.co -> {ip}")
    except Exception as e:
        log_message(f"❌ DNS解析失败: {e}")

def simulate_dash_callback_error():
    """模拟Dash回调中可能出现的错误"""
    log_message("=== 模拟Dash回调错误 ===")
    
    try:
        # 模拟Dash回调函数的执行过程
        log_message("模拟回调函数执行...")
        
        # 1. 获取API客户端
        from src.api.alpha_vantage import AlphaVantageClient
        api_client = AlphaVantageClient()
        log_message("✅ API客户端创建成功")
        
        # 2. 执行搜索
        search_term = "TSLA"
        log_message(f"执行搜索: {search_term}")
        
        results = api_client.search_symbols(search_term)
        log_message(f"搜索结果: {results}")
        
        # 3. 处理结果
        if results:
            options = []
            for result in results:
                if isinstance(result, dict):
                    symbol = result.get('symbol', '')
                    name = result.get('name', '')
                    options.append({
                        'label': f"{symbol} - {name}",
                        'value': symbol
                    })
            
            log_message(f"✅ 处理完成，生成 {len(options)} 个选项")
            return True
        else:
            log_message("❌ 搜索结果为空")
            return False
            
    except Exception as e:
        log_message(f"❌ 回调模拟失败: {e}")
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主诊断函数"""
    log_message("开始Render环境API调试")
    log_message("="*60)
    
    # 1. 检查环境变量
    env_ok = check_environment_variables()
    print()
    
    # 2. 测试Render特有问题
    test_render_specific_issues()
    print()
    
    # 3. 直接API调用测试
    if env_ok:
        api_ok = test_direct_api_call()
        print()
        
        # 4. 测试AlphaVantageClient
        if api_ok:
            client_ok = test_alpha_vantage_client()
            print()
            
            # 5. 模拟Dash回调
            if client_ok:
                callback_ok = simulate_dash_callback_error()
                print()
            else:
                callback_ok = False
        else:
            client_ok = False
            callback_ok = False
    else:
        api_ok = False
        client_ok = False
        callback_ok = False
    
    # 总结
    log_message("="*60)
    log_message("=== 诊断总结 ===")
    log_message(f"环境变量配置: {'✅ 正常' if env_ok else '❌ 异常'}")
    log_message(f"直接API调用: {'✅ 正常' if api_ok else '❌ 异常'}")
    log_message(f"AlphaVantage客户端: {'✅ 正常' if client_ok else '❌ 异常'}")
    log_message(f"Dash回调模拟: {'✅ 正常' if callback_ok else '❌ 异常'}")
    
    if not env_ok:
        log_message("\n🔧 建议解决方案:")
        log_message("1. 检查Render Dashboard中的环境变量配置")
        log_message("2. 确认ALPHA_VANTAGE_API_KEY设置为: SDMG58OJI9FOIUWW")
        log_message("3. 重新部署应用以应用环境变量更改")
    elif not api_ok:
        log_message("\n🔧 建议解决方案:")
        log_message("1. 检查API密钥是否有效")
        log_message("2. 验证网络连接和DNS解析")
        log_message("3. 检查Alpha Vantage API服务状态")
    elif not client_ok:
        log_message("\n🔧 建议解决方案:")
        log_message("1. 检查AlphaVantageClient类的实现")
        log_message("2. 验证错误处理逻辑")
        log_message("3. 检查依赖包版本")
    elif not callback_ok:
        log_message("\n🔧 建议解决方案:")
        log_message("1. 检查Dash回调函数的错误处理")
        log_message("2. 添加更详细的日志记录")
        log_message("3. 验证数据处理逻辑")
    else:
        log_message("\n🎉 所有测试通过！问题可能在其他地方")
        log_message("建议检查:")
        log_message("1. Render部署日志")
        log_message("2. 应用运行时错误")
        log_message("3. Dash应用的具体配置")

if __name__ == "__main__":
    main()