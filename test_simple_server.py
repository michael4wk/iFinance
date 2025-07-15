#!/usr/bin/env python3
"""
最简单的Flask服务器测试
用于验证Render部署的基本功能
"""

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Render! Server is working."

@app.route('/health')
def health():
    return {"status": "ok", "message": "Server is healthy"}

@app.route('/env')
def env_info():
    return {
        "PORT": os.environ.get('PORT', 'Not set'),
        "RENDER": os.environ.get('RENDER', 'Not set'),
        "ALPHA_VANTAGE_API_KEY": "***" if os.environ.get('ALPHA_VANTAGE_API_KEY') else 'Not set'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)

# 导出server对象供gunicorn使用
server = app