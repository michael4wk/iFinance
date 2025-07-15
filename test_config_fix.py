#!/usr/bin/env python3
"""
测试配置修复效果
验证修复后的配置系统是否能正确处理Render环境中的API密钥
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def log_message(message: str):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_local_environment():
    """测试本地环境配置"""
    log_message("=== 测试本地环境配置 ===")
    
    try:
        from src.utils.config import config
        
        # 检查是否检测为Render环境
        is_render = config.is_render_environment
        log_message(f"检测为Render环境: {is_render}")
        
        # 获取API密钥
        api_key = config.get('ALPHA_VANTAGE_API_KEY')
        log_message(f"获取的API密钥: {api_key[:8] if api_key else 'None'}...")
        
        # 预期在本地环境中应该从.env文件读取
        expected_local_key = "J7DTPEUD0VHYYAFR"
        if api_key == expected_local_key:
            log_message("✅ 本地环境配置正常")
            return True
        else:
            log_message(f"❌ 本地环境配置异常，期望: {expected_local_key[:8]}..., 实际: {api_key[:8] if api_key else 'None'}...")
            return False
            
    except Exception as e:
        log_message(f"❌ 本地环境测试失败: {e}")
        return False

def test_simulated_render_environment():
    """测试模拟的Render环境配置"""
    log_message("\n=== 测试模拟Render环境配置 ===")
    
    # 设置Render环境变量
    original_env = {}
    render_env_vars = {
        'RENDER': 'true',
        'RENDER_SERVICE_ID': 'srv-test123',
        'ENVIRONMENT': 'production',
        'ALPHA_VANTAGE_API_KEY': 'SDMG58OJI9FOIUWW'
    }
    
    # 备份原始环境变量
    for key in render_env_vars:
        original_env[key] = os.getenv(key)
        os.environ[key] = render_env_vars[key]
    
    try:
        # 重新导入配置模块以应用新的环境变量
        import importlib
        if 'src.utils.config' in sys.modules:
            importlib.reload(sys.modules['src.utils.config'])
        
        from src.utils.config import Config
        
        # 创建新的配置实例
        test_config = Config()
        
        # 检查是否检测为Render环境
        is_render = test_config.is_render_environment
        log_message(f"检测为Render环境: {is_render}")
        
        # 获取API密钥
        api_key = test_config.get('ALPHA_VANTAGE_API_KEY')
        log_message(f"获取的API密钥: {api_key[:8] if api_key else 'None'}...")
        
        # 在Render环境中应该使用环境变量而不是.env文件
        expected_render_key = "SDMG58OJI9FOIUWW"
        if is_render and api_key == expected_render_key:
            log_message("✅ Render环境配置正常")
            success = True
        else:
            log_message(f"❌ Render环境配置异常")
            log_message(f"  期望检测为Render环境: True, 实际: {is_render}")
            log_message(f"  期望API密钥: {expected_render_key[:8]}..., 实际: {api_key[:8] if api_key else 'None'}...")
            success = False
            
    except Exception as e:
        log_message(f"❌ Render环境测试失败: {e}")
        import traceback
        log_message(f"错误详情: {traceback.format_exc()}")
        success = False
    
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    
    return success

def test_api_functionality():
    """测试API功能"""
    log_message("\n=== 测试API功能 ===")
    
    try:
        from src.api.alpha_vantage import AlphaVantageClient
        
        # 创建API客户端
        client = AlphaVantageClient()
        
        # 测试搜索功能
        log_message("测试股票搜索功能...")
        results = client.search_symbols('TSLA')
        
        if results and len(results) > 0:
            log_message(f"✅ API搜索成功，找到 {len(results)} 个结果")
            log_message(f"第一个结果: {results[0].get('1. symbol', 'N/A')} - {results[0].get('2. name', 'N/A')}")
            return True
        else:
            log_message("❌ API搜索失败，未找到结果")
            return False
            
    except Exception as e:
        log_message(f"❌ API功能测试失败: {e}")
        return False

def test_dash_callback_simulation():
    """测试Dash回调模拟"""
    log_message("\n=== 测试Dash回调模拟 ===")
    
    try:
        from src.api.alpha_vantage import AlphaVantageClient
        
        # 模拟Dash回调中的股票搜索
        client = AlphaVantageClient()
        search_term = 'AAPL'
        
        log_message(f"模拟搜索: {search_term}")
        results = client.search_symbols(search_term)
        
        if results:
            # 模拟生成下拉选项
            options = []
            for result in results[:5]:  # 限制前5个结果
                symbol = result.get('1. symbol', '')
                name = result.get('2. name', '')
                if symbol:
                    options.append({
                        'label': f"{symbol} - {name}",
                        'value': symbol
                    })
            
            log_message(f"✅ 生成了 {len(options)} 个下拉选项")
            for option in options:
                log_message(f"  - {option['label']}")
            return True
        else:
            log_message("❌ 回调模拟失败，未找到搜索结果")
            return False
            
    except Exception as e:
        log_message(f"❌ Dash回调模拟失败: {e}")
        return False

def main():
    """主函数"""
    log_message("开始测试配置修复效果")
    log_message("="*60)
    
    # 运行所有测试
    tests = [
        ("本地环境配置", test_local_environment),
        ("模拟Render环境配置", test_simulated_render_environment),
        ("API功能", test_api_functionality),
        ("Dash回调模拟", test_dash_callback_simulation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            log_message(f"❌ 测试 '{test_name}' 执行异常: {e}")
            results[test_name] = False
    
    # 总结测试结果
    log_message("\n" + "="*60)
    log_message("=== 测试结果总结 ===")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        log_message(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    log_message("\n" + "="*60)
    if all_passed:
        log_message("🎉 所有测试通过！配置修复成功")
        log_message("\n📋 下一步操作:")
        log_message("1. 提交代码更改到Git")
        log_message("2. 重新部署到Render")
        log_message("3. 验证Render环境中的股票搜索功能")
    else:
        log_message("⚠️  部分测试失败，需要进一步调试")
        log_message("\n🔍 建议检查:")
        log_message("1. 配置文件是否正确加载")
        log_message("2. API密钥是否有效")
        log_message("3. 网络连接是否正常")

if __name__ == "__main__":
    main()