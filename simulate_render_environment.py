#!/usr/bin/env python3
"""
模拟Render环境测试脚本
用于在本地模拟Render环境的配置，诊断可能的问题
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

def log_message(message: str):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def backup_current_env():
    """备份当前环境变量"""
    return {
        'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT'),
        'DEBUG': os.getenv('DEBUG'),
        'RENDER': os.getenv('RENDER')
    }

def restore_env(backup):
    """恢复环境变量"""
    for key, value in backup.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value

def simulate_render_env():
    """模拟Render环境变量"""
    log_message("=== 模拟Render环境配置 ===")
    
    # 设置Render环境变量
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'SDMG58OJI9FOIUWW'
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DEBUG'] = 'false'
    os.environ['RENDER'] = 'true'
    os.environ['TZ'] = 'Asia/Shanghai'
    
    log_message("✅ Render环境变量已设置")
    log_message(f"API密钥: {os.getenv('ALPHA_VANTAGE_API_KEY')[:8]}...")
    log_message(f"环境: {os.getenv('ENVIRONMENT')}")
    log_message(f"调试模式: {os.getenv('DEBUG')}")

def test_api_with_render_key():
    """使用Render API密钥测试"""
    log_message("=== 测试Render API密钥 ===")
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    log_message(f"使用API密钥: {api_key[:8]}...")
    
    try:
        # 直接API调用
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': 'TSLA',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=30)
        log_message(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                log_message(f"响应数据类型: {type(data)}")
                
                if isinstance(data, dict):
                    if 'bestMatches' in data:
                        matches = data['bestMatches']
                        log_message(f"✅ 找到 {len(matches)} 个匹配结果")
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
                        
            except json.JSONDecodeError as e:
                log_message(f"❌ JSON解析失败: {e}")
                return False
        else:
            log_message(f"❌ HTTP请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        log_message(f"❌ API调用异常: {e}")
        return False

def test_config_system_in_render_env():
    """测试配置系统在Render环境中的行为"""
    log_message("=== 测试配置系统 ===")
    
    try:
        # 重新导入配置系统以获取新的环境变量
        import importlib
        if 'src.utils.config' in sys.modules:
            importlib.reload(sys.modules['src.utils.config'])
        
        from src.utils.config import config
        
        api_key = config.get('ALPHA_VANTAGE_API_KEY')
        log_message(f"配置系统获取的API密钥: {api_key[:8] if api_key else 'None'}...")
        
        if api_key == 'SDMG58OJI9FOIUWW':
            log_message("✅ 配置系统正确获取Render API密钥")
            return True
        else:
            log_message(f"❌ 配置系统获取的API密钥不正确: {api_key}")
            return False
            
    except Exception as e:
        log_message(f"❌ 配置系统测试失败: {e}")
        return False

def test_alpha_vantage_client_in_render_env():
    """测试AlphaVantageClient在Render环境中的行为"""
    log_message("=== 测试AlphaVantageClient ===")
    
    try:
        # 重新导入AlphaVantageClient
        import importlib
        if 'src.api.alpha_vantage' in sys.modules:
            importlib.reload(sys.modules['src.api.alpha_vantage'])
        
        from src.api.alpha_vantage import AlphaVantageClient
        
        client = AlphaVantageClient()
        log_message("✅ AlphaVantageClient实例创建成功")
        
        # 测试搜索功能
        results = client.search_symbols('TSLA')
        log_message(f"搜索结果数量: {len(results) if isinstance(results, list) else 'N/A'}")
        
        if isinstance(results, list) and len(results) > 0:
            log_message("✅ 搜索成功")
            return True
        else:
            log_message("❌ 搜索返回空结果")
            return False
            
    except Exception as e:
        log_message(f"❌ AlphaVantageClient测试失败: {e}")
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}")
        return False

def test_dash_callback_simulation():
    """模拟Dash回调在Render环境中的执行"""
    log_message("=== 模拟Dash回调执行 ===")
    
    try:
        # 模拟app.py中的回调函数逻辑
        from src.api.alpha_vantage import AlphaVantageClient
        
        # 模拟回调函数参数
        n_clicks = 1
        search_value = "TSLA"
        
        log_message(f"模拟搜索: {search_value}")
        
        if n_clicks and search_value:
            api_client = AlphaVantageClient()
            results = api_client.search_symbols(search_value)
            
            if results:
                # 构造下拉选项
                options = []
                for result in results:
                    if isinstance(result, dict):
                        symbol = result.get('symbol', '')
                        name = result.get('name', '')
                        options.append({
                            'label': f"{symbol} - {name}",
                            'value': symbol
                        })
                
                log_message(f"✅ 生成 {len(options)} 个下拉选项")
                
                # 模拟返回值
                return_value = (
                    options,  # stock-dropdown.options
                    None,     # stock-dropdown.value
                    {},       # selected-stock-info.data
                    []        # error-container.children
                )
                
                log_message("✅ 回调函数执行成功")
                return True
            else:
                log_message("❌ 搜索结果为空")
                return False
        else:
            log_message("❌ 回调参数无效")
            return False
            
    except Exception as e:
        log_message(f"❌ 回调模拟失败: {e}")
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}")
        return False

def compare_api_keys():
    """比较不同API密钥的响应"""
    log_message("=== 比较API密钥响应 ===")
    
    api_keys = {
        'Local': 'J7DTPEUD0VHYYAFR',
        'Render': 'SDMG58OJI9FOIUWW'
    }
    
    results = {}
    
    for env_name, api_key in api_keys.items():
        log_message(f"\n--- 测试 {env_name} API密钥 ---")
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': 'TSLA',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'bestMatches' in data:
                    count = len(data['bestMatches'])
                    log_message(f"✅ {env_name}: 找到 {count} 个结果")
                    results[env_name] = True
                else:
                    log_message(f"❌ {env_name}: {data}")
                    results[env_name] = False
            else:
                log_message(f"❌ {env_name}: HTTP {response.status_code}")
                results[env_name] = False
                
        except Exception as e:
            log_message(f"❌ {env_name}: 异常 {e}")
            results[env_name] = False
    
    return results

def main():
    """主测试函数"""
    log_message("开始Render环境模拟测试")
    log_message("="*60)
    
    # 备份当前环境
    env_backup = backup_current_env()
    log_message(f"当前环境备份完成")
    
    try:
        # 1. 比较API密钥
        api_comparison = compare_api_keys()
        print()
        
        # 2. 模拟Render环境
        simulate_render_env()
        print()
        
        # 3. 测试API调用
        api_ok = test_api_with_render_key()
        print()
        
        # 4. 测试配置系统
        config_ok = test_config_system_in_render_env()
        print()
        
        # 5. 测试AlphaVantageClient
        client_ok = test_alpha_vantage_client_in_render_env()
        print()
        
        # 6. 模拟Dash回调
        callback_ok = test_dash_callback_simulation()
        print()
        
        # 总结
        log_message("="*60)
        log_message("=== 模拟测试总结 ===")
        log_message(f"Local API密钥: {'✅ 正常' if api_comparison.get('Local') else '❌ 异常'}")
        log_message(f"Render API密钥: {'✅ 正常' if api_comparison.get('Render') else '❌ 异常'}")
        log_message(f"Render环境API调用: {'✅ 正常' if api_ok else '❌ 异常'}")
        log_message(f"Render环境配置系统: {'✅ 正常' if config_ok else '❌ 异常'}")
        log_message(f"Render环境客户端: {'✅ 正常' if client_ok else '❌ 异常'}")
        log_message(f"Render环境回调: {'✅ 正常' if callback_ok else '❌ 异常'}")
        
        if all([api_ok, config_ok, client_ok, callback_ok]):
            log_message("\n🎉 所有Render环境模拟测试通过！")
            log_message("问题可能在于:")
            log_message("1. Render Dashboard中的环境变量配置不正确")
            log_message("2. Render部署过程中的环境变量加载问题")
            log_message("3. Render运行时的其他环境因素")
        else:
            log_message("\n❌ 发现问题，需要进一步调查")
            
    finally:
        # 恢复环境
        restore_env(env_backup)
        log_message("\n环境变量已恢复")

if __name__ == "__main__":
    main()