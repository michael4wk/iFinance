#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha Vantage API Key 验证脚本

用于在部署前验证 API Key 的有效性
"""

import os
import sys
import urllib.request
import urllib.parse
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目配置系统
from src.utils.config import config

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv 未安装，将直接读取环境变量")


def verify_api_key(api_key: str = None) -> bool:
    """
    验证 Alpha Vantage API Key 的有效性
    
    Args:
        api_key: API密钥，如果为None则从环境变量读取
        
    Returns:
        bool: API Key是否有效
    """
    if not api_key:
        api_key = config.get('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print("❌ 未找到 ALPHA_VANTAGE_API_KEY 环境变量")
        print("请确保已设置环境变量或创建 .env 文件")
        return False
    
    print(f"🔍 验证 API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # 使用简单的查询测试API Key
    test_url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': 'AAPL',
        'apikey': api_key
    }
    
    try:
        print("📡 发送测试请求...")
        # 构建完整的URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{test_url}?{query_string}"
        
        # 发送请求
        with urllib.request.urlopen(full_url, timeout=10) as response:
            response_text = response.read().decode('utf-8')
            data = json.loads(response_text)
        
        # 检查响应内容
        if 'Error Message' in data:
            print(f"❌ API 错误: {data['Error Message']}")
            return False
        elif 'Note' in data:
            print(f"⚠️  API 限制: {data['Note']}")
            print("API Key 有效，但可能已达到调用限制")
            return True
        elif 'Global Quote' in data:
            quote = data['Global Quote']
            symbol = quote.get('01. symbol', 'N/A')
            price = quote.get('05. price', 'N/A')
            print(f"✅ API Key 有效！")
            print(f"📈 测试数据: {symbol} = ${price}")
            return True
        elif 'Information' in data:
            info_msg = data['Information']
            if 'demo' in info_msg.lower():
                print(f"⚠️  检测到演示 API Key: {info_msg}")
                print("🔧 当前使用的是演示密钥，功能受限")
                print("📝 建议申请正式的 API Key 以获得完整功能")
                return True
            else:
                print(f"ℹ️  API 信息: {info_msg}")
                return True
        else:
            print(f"⚠️  收到意外响应格式: {list(data.keys())}")
            print(f"📄 响应内容: {data}")
            return False
            
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print(f"❌ 网络请求失败: {e.reason}")
        else:
            print(f"❌ 网络请求失败: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ 响应解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False


def main():
    """
    主函数
    """
    print("=" * 50)
    print("🔑 Alpha Vantage API Key 验证工具")
    print("=" * 50)
    
    # 检查是否有命令行参数提供的API Key
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print(f"📝 使用命令行提供的 API Key")
    
    # 验证API Key
    is_valid = verify_api_key(api_key)
    
    print("\n" + "=" * 50)
    if is_valid:
        print("🎉 验证成功！API Key 可以正常使用")
        print("✅ 可以继续进行 Railway 部署")
        sys.exit(0)
    else:
        print("💥 验证失败！请检查 API Key 配置")
        print("\n📋 解决方案:")
        print("1. 确认 API Key 正确无误")
        print("2. 检查网络连接")
        print("3. 确认 API Key 未过期")
        print("4. 访问 https://www.alphavantage.co/support/#api-key 获取新的 API Key")
        sys.exit(1)


if __name__ == "__main__":
    main()