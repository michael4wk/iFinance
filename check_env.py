#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的环境变量检查脚本
用于在Render部署后快速验证环境配置
"""

import os
import sys

def check_environment():
    """检查关键环境变量"""
    print("🔍 Render环境变量检查")
    print("=" * 40)
    
    # 关键环境变量列表
    required_vars = {
        'ALPHA_VANTAGE_API_KEY': '必需 - Alpha Vantage API密钥',
        'HOST': '建议设置为 0.0.0.0',
        'PORT': '建议设置为 10000',
    }
    
    optional_vars = {
        'DEBUG': '生产环境建议设为 False',
        'LOG_LEVEL': '建议设置为 INFO',
        'ALPHA_VANTAGE_BASE_URL': 'API基础URL',
        'REQUEST_TIMEOUT': 'API请求超时时间',
        'MAX_RETRIES': '最大重试次数',
        'RETRY_DELAY': '重试延迟时间'
    }
    
    all_good = True
    
    print("📋 必需环境变量:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # 对于API密钥，只显示部分内容
            if 'API_KEY' in var and len(value) > 8:
                display_value = f"{value[:4]}...{value[-4:]}"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未设置 ({desc})")
            all_good = False
    
    print("\n📋 可选环境变量:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "⚠️"
        print(f"{status} {var}: {value or '未设置'} ({desc})")
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 所有必需环境变量已正确配置！")
        print("\n📝 下一步:")
        print("1. 确保Render服务已重新部署")
        print("2. 访问您的应用: https://ifinance-durp.onrender.com")
        print("3. 测试股票查询功能")
    else:
        print("🚨 发现配置问题！")
        print("\n🔧 解决方案:")
        print("1. 登录 Render Dashboard")
        print("2. 进入您的服务 > Environment")
        print("3. 添加缺失的环境变量")
        print("4. 保存更改并等待重新部署")
        print("\n📖 详细指南: 查看 RENDER_DEPLOYMENT_GUIDE.md")
    
    return all_good

if __name__ == "__main__":
    try:
        check_environment()
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {e}")
        sys.exit(1)