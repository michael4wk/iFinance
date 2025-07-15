#!/usr/bin/env python3
"""
Render环境调试脚本
用于诊断Render部署环境中的问题
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目配置系统
from src.utils.config import config

def check_environment_variables():
    """
    检查关键环境变量的配置
    """
    print("\n" + "="*60)
    print("🔍 检查环境变量配置")
    print("="*60)
    
    required_vars = {
        'ALPHA_VANTAGE_API_KEY': '必需 - Alpha Vantage API密钥',
        'ENVIRONMENT': '推荐 - 运行环境标识',
        'DEBUG': '推荐 - 调试模式开关',
        'TZ': '推荐 - 时区设置'
    }
    
    missing_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            if var_name == 'ALPHA_VANTAGE_API_KEY':
                # 隐藏API密钥的大部分内容
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "[已设置]"
            else:
                display_value = value
            print(f"✅ {var_name:25} = {display_value}")
        else:
            print(f"❌ {var_name:25} = [未设置] - {description}")
            missing_vars.append(var_name)
    
    return missing_vars

def test_api_key_directly(api_key: str):
    """
    直接测试API密钥的有效性
    
    Args:
        api_key: API密钥
    """
    print("\n" + "="*60)
    print("🔑 测试API密钥有效性")
    print("="*60)
    
    if not api_key:
        print("❌ API密钥为空，无法测试")
        return False
    
    print(f"🔍 测试API密钥: {api_key[:8]}...{api_key[-4:]}")
    
    # 使用简单的查询测试API Key
    test_url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': 'AAPL',
        'apikey': api_key
    }
    
    try:
        print("📡 发送测试请求...")
        query_string = urllib.parse.urlencode(params)
        full_url = f"{test_url}?{query_string}"
        
        with urllib.request.urlopen(full_url, timeout=10) as response:
            response_text = response.read().decode('utf-8')
            data = json.loads(response_text)
        
        # 检查响应内容
        if 'Error Message' in data:
            print(f"❌ API错误: {data['Error Message']}")
            return False
        elif 'Note' in data:
            print(f"⚠️  API限制: {data['Note']}")
            print("API密钥有效，但可能已达到调用限制")
            return True
        elif 'Global Quote' in data:
            quote = data['Global Quote']
            symbol = quote.get('01. symbol', 'N/A')
            price = quote.get('05. price', 'N/A')
            print(f"✅ API密钥有效！")
            print(f"📈 测试数据: {symbol} = ${price}")
            return True
        elif 'Information' in data:
            info_msg = data['Information']
            if 'demo' in info_msg.lower():
                print(f"⚠️  检测到演示API密钥: {info_msg}")
                print("🔧 当前使用的是演示密钥，功能受限")
                print("📝 这可能是问题的根源！")
                return False
            else:
                print(f"ℹ️  API信息: {info_msg}")
                return True
        else:
            print(f"⚠️  收到意外响应格式: {list(data.keys())}")
            print(f"📄 响应内容: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_symbol_search(api_key: str):
    """
    测试股票搜索功能
    
    Args:
        api_key: API密钥
    """
    print("\n" + "="*60)
    print("🔍 测试股票搜索功能")
    print("="*60)
    
    if not api_key:
        print("❌ API密钥为空，无法测试")
        return False
    
    test_symbols = ['TSLA', 'AAPL', 'META']
    
    for symbol in test_symbols:
        print(f"\n🔍 搜索: {symbol}")
        
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': symbol,
            'apikey': api_key
        }
        
        try:
            query_string = urllib.parse.urlencode(params)
            full_url = f"https://www.alphavantage.co/query?{query_string}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                response_text = response.read().decode('utf-8')
                data = json.loads(response_text)
            
            if 'bestMatches' in data:
                matches = data['bestMatches']
                print(f"✅ 找到 {len(matches)} 个匹配结果")
                if matches:
                    first_match = matches[0]
                    print(f"   首个结果: {first_match.get('1. symbol')} - {first_match.get('2. name')}")
            elif 'Information' in data:
                info_msg = data['Information']
                if 'demo' in info_msg.lower():
                    print(f"❌ 演示API密钥限制: {info_msg}")
                    return False
                else:
                    print(f"ℹ️  API信息: {info_msg}")
            else:
                print(f"⚠️  意外响应: {list(data.keys())}")
                print(f"📄 内容: {data}")
                
        except Exception as e:
            print(f"❌ 搜索失败: {str(e)}")
    
    return True

def generate_diagnosis_report(missing_vars: list, api_valid: bool, search_works: bool):
    """
    生成诊断报告
    
    Args:
        missing_vars: 缺失的环境变量列表
        api_valid: API密钥是否有效
        search_works: 搜索功能是否正常
    """
    print("\n" + "="*80)
    print("📋 诊断报告")
    print("="*80)
    
    print("\n🔍 问题分析:")
    
    if missing_vars:
        print(f"❌ 缺失环境变量: {', '.join(missing_vars)}")
    else:
        print("✅ 所有必需环境变量都已设置")
    
    if not api_valid:
        print("❌ API密钥无效或为演示密钥")
    else:
        print("✅ API密钥有效")
    
    if not search_works:
        print("❌ 股票搜索功能异常")
    else:
        print("✅ 股票搜索功能正常")
    
    print("\n💡 解决建议:")
    
    if 'ALPHA_VANTAGE_API_KEY' in missing_vars:
        print("\n🔧 API密钥未设置:")
        print("   1. 登录Render Dashboard")
        print("   2. 进入你的iFinance服务")
        print("   3. 点击'Environment'标签")
        print("   4. 添加环境变量:")
        print("      Key: ALPHA_VANTAGE_API_KEY")
        print("      Value: SDMG58OJI9FOIUWW")
        print("   5. 保存后等待自动重新部署")
    
    elif not api_valid:
        print("\n🔧 API密钥问题:")
        print("   1. 当前API密钥可能是演示密钥或无效")
        print("   2. 确认Render环境变量中的API密钥值")
        print("   3. 如果是演示密钥，请更换为有效的API密钥")
        print("   4. 推荐使用: SDMG58OJI9FOIUWW")
    
    elif not search_works:
        print("\n🔧 搜索功能问题:")
        print("   1. API密钥有效但搜索异常")
        print("   2. 可能是API调用频率限制")
        print("   3. 检查应用日志中的详细错误信息")
        print("   4. 稍后重试或联系技术支持")
    
    else:
        print("\n🎉 所有检查都通过了！")
        print("   如果Web应用仍有问题，可能是:")
        print("   1. 应用代码逻辑问题")
        print("   2. 前端显示问题")
        print("   3. 缓存问题")
        print("   4. 建议重新部署应用")
    
    print("\n📞 需要帮助?")
    print("   1. 查看Render应用日志")
    print("   2. 检查浏览器开发者工具")
    print("   3. 尝试重新部署应用")

def main():
    """
    主函数
    """
    print("🚀 Render环境诊断工具")
    print("🎯 帮助诊断部署环境中的配置问题")
    
    # 步骤1: 检查环境变量
    missing_vars = check_environment_variables()
    
    # 步骤2: 测试API密钥
    api_key = config.get('ALPHA_VANTAGE_API_KEY')
    api_valid = test_api_key_directly(api_key) if api_key else False
    
    # 步骤3: 测试搜索功能
    search_works = test_symbol_search(api_key) if api_key and api_valid else False
    
    # 步骤4: 生成诊断报告
    generate_diagnosis_report(missing_vars, api_valid, search_works)

if __name__ == "__main__":
    main()