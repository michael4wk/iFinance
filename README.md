# iFinance - 智能金融数据查询系统

一个基于Python的现代化金融数据查询和可视化应用，提供股票搜索、OHLCV数据查询和展示功能。

## 功能特性

- 🔍 **智能股票搜索**: 支持股票代码和公司名称的模糊搜索与自动补全
- 📊 **OHLCV数据展示**: 获取并展示股票的开盘价、最高价、最低价、收盘价和成交量数据
- 🎨 **现代化界面**: 基于Dash框架的响应式Web界面
- 🔒 **安全配置**: 环境变量管理，API密钥安全存储
- 🧪 **高质量代码**: 完整的测试覆盖和代码质量保证

## 技术栈

- **后端**: Python 3.9+
- **前端**: Dash (Plotly)
- **数据源**: Alpha Vantage API
- **数据处理**: Pandas, NumPy
- **HTTP客户端**: Requests
- **配置管理**: python-dotenv
- **测试框架**: pytest

## 快速开始

### 1. 环境准备

1. **Python 环境**
   ```bash
   # 确保安装了 Python 3.8+
   python3 --version
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   # 创建虚拟环境
   python3 -m venv venv
   
   # 激活虚拟环境
   # macOS/Linux:
   source venv/bin/activate
   # Windows:
   # venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   # 更新pip
   pip install --upgrade pip
   
   # 安装项目依赖
   pip install -r requirements.txt
   ```

### 2. 配置设置

```bash
# 复制环境变量模板
cp config/.env.example .env

# 编辑 .env 文件，填入你的 Alpha Vantage API Key
# 获取API Key: https://www.alphavantage.co/support/#api-key
```

### 3. 运行应用

**方式一：使用启动脚本（推荐）**
```bash
# 一键启动（自动处理虚拟环境、依赖安装、测试等）
./start.sh
```

**方式二：手动启动**
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 启动应用
python run.py

# 或者使用自定义参数
python run.py --host 0.0.0.0 --port 8080 --debug
```

**方式三：基础功能测试**
```bash
# 测试核心功能（不启动Web界面）
python test_basic.py
```

应用将在 `http://127.0.0.1:8050` 启动。

## 项目结构

```
iFinance/
├── src/                    # 源代码目录
│   ├── api/               # API客户端模块
│   ├── data/              # 数据处理模块
│   ├── ui/                # 前端界面模块
│   └── utils/             # 工具函数模块
├── tests/                 # 测试文件目录
├── config/                # 配置文件目录
├── docs/                  # 文档目录
├── requirements.txt       # 生产环境依赖
├── requirements-dev.txt   # 开发环境依赖
└── README.md             # 项目说明文档
```

## 开发指南

### 安装开发依赖

```bash
pip install -r requirements-dev.txt
```

### 代码质量检查

```bash
# 代码格式化
black src/ tests/
isort src/ tests/

# 代码检查
flake8 src/ tests/
mypy src/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html
```

## API文档

详细的API使用说明请参考 [API参考文档](docs/api_reference.md)。

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。在提交代码前，请确保：

1. 代码通过所有测试
2. 代码符合项目的格式规范
3. 添加了必要的测试用例
4. 更新了相关文档

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至项目维护者