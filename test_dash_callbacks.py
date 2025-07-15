#!/usr/bin/env python3
"""
测试Dash应用回调函数
验证股票搜索等核心功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.app import create_app
from src.api.alpha_vantage import AlphaVantageClient
from src.data.processor import DataProcessor

def test_app_creation():
    """测试应用创建"""
    print("=== 测试应用创建 ===")
    try:
        app = create_app()
        print(f"✅ 应用创建成功: {type(app)}")
        print(f"✅ 应用标题: {app.title}")
        print(f"✅ 回调函数数量: {len(app.callback_map)}")
        
        # 列出所有回调函数
        print("\n注册的回调函数:")
        for i, (callback_id, callback) in enumerate(app.callback_map.items(), 1):
            print(f"  {i}. {callback_id}")
        
        return app
    except Exception as e:
        print(f"❌ 应用创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_api_client():
    """测试API客户端"""
    print("\n=== 测试API客户端 ===")
    try:
        client = AlphaVantageClient()
        print(f"✅ API客户端创建成功: {type(client)}")
        
        # 测试搜索功能
        print("\n测试股票搜索...")
        results = client.search_symbols('AAPL')
        print(f"✅ 搜索结果数量: {len(results)}")
        if results:
            print(f"✅ 第一个结果: {results[0]}")
        
        return True
    except Exception as e:
        print(f"❌ API客户端测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processor():
    """测试数据处理器"""
    print("\n=== 测试数据处理器 ===")
    try:
        processor = DataProcessor()
        print(f"✅ 数据处理器创建成功: {type(processor)}")
        return True
    except Exception as e:
        print(f"❌ 数据处理器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_callback_simulation():
    """模拟回调函数调用"""
    print("\n=== 模拟回调函数测试 ===")
    try:
        # 创建应用
        app = create_app()
        
        # 模拟搜索输入
        search_input = "AAPL"
        print(f"模拟搜索输入: {search_input}")
        
        # 直接调用API客户端（模拟回调函数内部逻辑）
        client = AlphaVantageClient()
        results = client.search_symbols(search_input)
        
        print(f"✅ 搜索结果: {len(results)} 个")
        for i, result in enumerate(results[:3], 1):
            symbol = result.get('1. symbol', 'N/A')
            name = result.get('2. name', 'N/A')
            print(f"  {i}. {symbol} - {name}")
        
        return True
    except Exception as e:
        print(f"❌ 回调函数模拟失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 iFinance Dash应用回调函数测试")
    print("=" * 50)
    
    # 测试应用创建
    app = test_app_creation()
    if not app:
        print("\n❌ 应用创建失败，停止测试")
        return
    
    # 测试API客户端
    api_ok = test_api_client()
    
    # 测试数据处理器
    processor_ok = test_data_processor()
    
    # 测试回调函数模拟
    callback_ok = test_callback_simulation()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"  应用创建: {'✅ 成功' if app else '❌ 失败'}")
    print(f"  API客户端: {'✅ 成功' if api_ok else '❌ 失败'}")
    print(f"  数据处理器: {'✅ 成功' if processor_ok else '❌ 失败'}")
    print(f"  回调函数模拟: {'✅ 成功' if callback_ok else '❌ 失败'}")
    
    if all([app, api_ok, processor_ok, callback_ok]):
        print("\n🎉 所有测试通过！应用应该能在Render上正常工作。")
    else:
        print("\n⚠️  部分测试失败，需要进一步调试。")

if __name__ == "__main__":
    main()