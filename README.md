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

## 云端部署

### Railway 部署

本项目已配置好 Railway 部署文件，支持一键部署到云端。

#### 部署步骤

1. **准备 GitHub 仓库**
   - Fork 本项目到你的 GitHub 账户
   - 或将代码推送到你的 GitHub 仓库

2. **注册 Railway 账户**
   - 访问 [Railway](https://railway.app)
   - 使用 GitHub 账户注册登录

3. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的 iFinance 仓库

4. **配置环境变量**
   在 Railway 项目设置中添加以下环境变量：
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ENVIRONMENT=production
   DEBUG=false
   TZ=Asia/Shanghai
   ```

5. **部署完成**
   - Railway 会自动检测 `Procfile` 和 `railway.toml`
   - 自动安装依赖并启动应用
   - 获得一个公网访问地址

#### Railway 配置文件

- `Procfile`: 定义应用启动命令
- `railway.toml`: Railway 专用配置
- `.env.example`: 环境变量模板

#### 免费额度

- 每月 $5 免费额度
- 500 小时运行时间
- 自动休眠优化（无访问时自动暂停）

### 其他部署选项

- **Render**: 类似 Railway 的免费部署平台
- **Vercel**: 适合静态站点和 Serverless 函数
- **Heroku**: 需要付费计划
- **自建服务器**: 使用 Docker 或直接部署

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