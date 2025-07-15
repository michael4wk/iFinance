#!/usr/bin/env python3
"""
环境对比测试脚本
用于对比本地环境和Render环境的API响应差异
"""

import os
import sys
import json
import requests
from datetime import datetime

# 添加项目根目录到Python路径
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目配置系统
from src.utils.config import config

def log_message(message):
    """记录带时间戳的消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def get_environment_info():
    """获取环境信息"""
    env_info = {
        'python_version': sys.version,
        'platform': sys.platform,
        'environment': os.getenv('ENVIRONMENT', 'local'),
        'debug': os.getenv('DEBUG', 'false'),
        'timezone': os.getenv('TZ', 'Not Set'),
        'api_key_set': bool(config.get('ALPHA_VANTAGE_API_KEY')),
    }
    
    # 获取外部IP
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        if response.status_code == 200:
            env_info['external_ip'] = response.json().get('origin', 'Unknown')
        else:
            env_info['external_ip'] = 'Unable to fetch'
    except Exception as e:
        env_info['external_ip'] = f'Error: {str(e)}'
    
    return env_info

def test_api_call(api_key, function, params, description):
    """通用API调用测试函数"""
    log_message(f"测试: {description}")
    
    url = "https://www.alphavantage.co/query"
    full_params = {**params, "apikey": api_key}
    
    try:
        log_message(f"请求URL: {url}")
        log_message(f"请求参数: {full_params}")
        
        response = requests.get(url, params=full_params, timeout=30)
        
        result = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'response_time': response.elapsed.total_seconds(),
            'success': False,
            'data': None,
            'error': None
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                result['data'] = data
                result['success'] = True
                log_message(f"✅ 请求成功 (耗时: {result['response_time']:.2f}秒)")
                log_message(f"响应数据: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                result['error'] = f"JSON解析错误: {str(e)}"
                result['data'] = response.text
                log_message(f"❌ JSON解析失败: {str(e)}")
                log_message(f"原始响应: {response.text}")
        else:
            result['error'] = f"HTTP错误: {response.status_code}"
            result['data'] = response.text
            log_message(f"❌ HTTP错误: {response.status_code}")
            log_message(f"错误响应: {response.text}")
            
    except Exception as e:
        result = {
            'status_code': None,
            'headers': {},
            'response_time': None,
            'success': False,
            'data': None,
            'error': str(e)
        }
        log_message(f"❌ 请求异常: {str(e)}")
    
    return result

def analyze_symbol_search_response(data, keywords):
    """分析股票搜索响应"""
    analysis = {
        'has_best_matches': False,
        'best_matches_count': 0,
        'best_matches_type': None,
        'has_error_message': False,
        'has_note': False,
        'has_information': False,
        'response_keys': [],
        'symbols_found': []
    }
    
    if isinstance(data, dict):
        analysis['response_keys'] = list(data.keys())
        
        # 检查bestMatches
        if 'bestMatches' in data:
            analysis['has_best_matches'] = True
            best_matches = data['bestMatches']
            analysis['best_matches_type'] = type(best_matches).__name__
            
            if isinstance(best_matches, list):
                analysis['best_matches_count'] = len(best_matches)
                for match in best_matches:
                    if isinstance(match, dict):
                        symbol = match.get('1. symbol', '')
                        name = match.get('2. name', '')
                        analysis['symbols_found'].append({
                            'symbol': symbol,
                            'name': name
                        })
        
        # 检查错误和提示信息
        analysis['has_error_message'] = 'Error Message' in data
        analysis['has_note'] = 'Note' in data
        analysis['has_information'] = 'Information' in data
    
    return analysis

def main():
    """主函数"""
    log_message("开始环境对比测试")
    log_message("=" * 60)
    
    # 获取环境信息
    env_info = get_environment_info()
    log_message("环境信息:")
    for key, value in env_info.items():
        log_message(f"  {key}: {value}")
    
    # 检查API密钥 - 使用项目配置系统而不是直接读取环境变量
    api_key = config.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        log_message("❌ ALPHA_VANTAGE_API_KEY未在项目配置中设置")
        return
    
    log_message(f"✅ API密钥: {api_key[:8]}...{api_key[-4:]} (长度: {len(api_key)})")
    
    # 测试用例
    test_cases = [
        {
            'function': 'GLOBAL_QUOTE',
            'params': {'function': 'GLOBAL_QUOTE', 'symbol': 'AAPL'},
            'description': '基础报价查询 (AAPL)'
        },
        {
            'function': 'SYMBOL_SEARCH',
            'params': {'function': 'SYMBOL_SEARCH', 'keywords': 'TSLA'},
            'description': '股票搜索 (TSLA)'
        },
        {
            'function': 'SYMBOL_SEARCH',
            'params': {'function': 'SYMBOL_SEARCH', 'keywords': 'AAPL'},
            'description': '股票搜索 (AAPL)'
        },
        {
            'function': 'SYMBOL_SEARCH',
            'params': {'function': 'SYMBOL_SEARCH', 'keywords': 'microsoft'},
            'description': '股票搜索 (microsoft)'
        },
        {
            'function': 'SYMBOL_SEARCH',
            'params': {'function': 'SYMBOL_SEARCH', 'keywords': 'tesla'},
            'description': '股票搜索 (tesla)'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        log_message(f"\n{'='*20} 测试 {i}/{len(test_cases)} {'='*20}")
        
        result = test_api_call(
            api_key,
            test_case['function'],
            test_case['params'],
            test_case['description']
        )
        
        # 如果是股票搜索，进行详细分析
        if test_case['function'] == 'SYMBOL_SEARCH' and result['success']:
            keywords = test_case['params']['keywords']
            analysis = analyze_symbol_search_response(result['data'], keywords)
            result['analysis'] = analysis
            
            log_message(f"搜索分析结果:")
            log_message(f"  响应键: {analysis['response_keys']}")
            log_message(f"  包含bestMatches: {analysis['has_best_matches']}")
            log_message(f"  bestMatches类型: {analysis['best_matches_type']}")
            log_message(f"  匹配数量: {analysis['best_matches_count']}")
            log_message(f"  找到的股票: {analysis['symbols_found']}")
            log_message(f"  包含错误信息: {analysis['has_error_message']}")
            log_message(f"  包含提示信息: {analysis['has_note']}")
            log_message(f"  包含说明信息: {analysis['has_information']}")
        
        results.append({
            'test_case': test_case,
            'result': result
        })
    
    # 生成总结报告
    log_message(f"\n{'='*20} 测试总结 {'='*20}")
    
    successful_tests = sum(1 for r in results if r['result']['success'])
    total_tests = len(results)
    
    log_message(f"总测试数: {total_tests}")
    log_message(f"成功测试: {successful_tests}")
    log_message(f"失败测试: {total_tests - successful_tests}")
    log_message(f"成功率: {(successful_tests/total_tests)*100:.1f}%")
    
    # 股票搜索特别分析
    search_tests = [r for r in results if r['test_case']['function'] == 'SYMBOL_SEARCH']
    successful_searches = sum(1 for r in search_tests if r['result']['success'] and r['result'].get('analysis', {}).get('best_matches_count', 0) > 0)
    
    log_message(f"\n股票搜索测试:")
    log_message(f"  搜索测试数: {len(search_tests)}")
    log_message(f"  返回结果的搜索: {successful_searches}")
    log_message(f"  搜索成功率: {(successful_searches/len(search_tests))*100:.1f}%")
    
    # 保存详细结果到文件
    output_file = f"api_test_results_{env_info['environment']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'environment': env_info,
                'test_results': results,
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'search_tests': len(search_tests),
                    'successful_searches': successful_searches
                }
            }, f, indent=2, ensure_ascii=False)
        log_message(f"详细结果已保存到: {output_file}")
    except Exception as e:
        log_message(f"保存结果文件失败: {str(e)}")
    
    log_message("\n测试完成!")

if __name__ == "__main__":
    main()