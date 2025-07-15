# Demo API Key 问题解决报告

## 问题概述

在调试 iFinance 股票搜索功能时，发现多个测试脚本返回 Alpha Vantage 的 demo API key 错误信息，导致股票搜索功能返回空结果。

## 根本原因分析

### 1. 问题根源
- **系统环境变量污染**: 系统级别的 `ALPHA_VANTAGE_API_KEY` 环境变量被设置为 `demo`
- **配置系统不一致**: 多个测试脚本直接使用 `os.getenv()` 读取系统环境变量，而不是使用项目的配置系统
- **项目配置系统正常**: 项目的 `src.utils.config` 模块能正确从 `.env` 文件加载真实的 API 密钥

### 2. 影响范围
- ✅ **主应用正常**: `src/main.py` 和 `src/ui/app.py` 使用项目配置系统，工作正常
- ❌ **测试脚本异常**: 独立的测试脚本使用系统环境变量，获取到 demo 密钥

## 解决方案

### 1. 修复的文件列表
以下文件已修复，现在都使用项目配置系统而不是直接读取系统环境变量：

- `compare_environments.py` - 环境对比测试脚本
- `verify_api_key.py` - API 密钥验证脚本
- `render_debug_test.py` - Render 调试测试脚本
- `render_api_test.py` - Render API 测试脚本
- `debug_render_environment.py` - Render 环境调试脚本
- `investigate_price_difference.py` - 价格差异调查脚本

### 2. 修复方法
对每个文件进行以下修改：

```python
# 修改前 (错误方式)
import os
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

# 修改后 (正确方式)
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目配置系统
from src.utils.config import config

# 使用项目配置系统获取API密钥
api_key = config.get('ALPHA_VANTAGE_API_KEY')
```

### 3. 环境清理
- 清除了系统级别的 `ALPHA_VANTAGE_API_KEY=demo` 环境变量
- 确保项目配置系统从 `.env` 文件正确加载真实 API 密钥

## 验证结果

### 修复前
```
系统环境变量 ALPHA_VANTAGE_API_KEY: demo
项目配置中的 ALPHA_VANTAGE_API_KEY: J7DTPEUD0V...
测试脚本搜索成功率: 0%
```

### 修复后
```
系统环境变量 ALPHA_VANTAGE_API_KEY: None
项目配置中的 ALPHA_VANTAGE_API_KEY: J7DTPEUD0V...
测试脚本搜索成功率: 100%
```

## 最佳实践建议

### 1. 配置管理原则
- **统一配置入口**: 所有项目代码都应该通过 `src.utils.config` 模块获取配置
- **避免直接环境变量访问**: 不要在项目代码中直接使用 `os.getenv()`
- **配置层次**: 项目配置系统 > 系统环境变量

### 2. 测试脚本规范
- 独立测试脚本应该导入并使用项目的配置系统
- 确保测试环境与生产环境配置一致
- 使用虚拟环境运行所有测试

### 3. 部署注意事项
- Render 等部署平台应该在环境变量中设置真实 API 密钥
- 本地开发使用 `.env` 文件管理配置
- 避免在系统级别设置项目相关的环境变量

## 启动建议

推荐使用项目提供的 `start.sh` 脚本启动应用：

```bash
# 自动处理虚拟环境、依赖安装和端口管理
./start.sh --auto
```

这样可以确保：
- 正确的虚拟环境激活
- 依赖包自动安装
- 配置文件正确加载
- 端口冲突自动处理

## 总结

通过统一使用项目配置系统，彻底解决了 demo API key 问题。现在所有测试脚本和主应用都能正确使用真实的 Alpha Vantage API 密钥，股票搜索功能完全正常。

**关键教训**: 在多文件项目中，配置管理的一致性至关重要。应该建立统一的配置访问机制，避免直接访问系统环境变量导致的配置不一致问题。