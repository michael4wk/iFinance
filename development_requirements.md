# iFinance 开发需求文档 (v2.0)

---

## 1. 项目愿景与目标

*   **项目愿景**：构建一个用户友好、功能强大、界面美观的个人金融数据分析工具。
*   **初期目标 (MVP)**：快速开发并上线一个Web应用，核心功能是查询和展示指定股票在特定日期的OHLCV数据。

## 2. 技术选型与论证

为了确保项目的可扩展性、可维护性和开发效率，我们对技术栈进行了审慎的选择与论证。

*   **视觉参考**:
    *   为了确保最终产品在用户体验和界面布局上符合预期，以下为项目的设计参考图：
    *   [此处插入项目界面参考图]

*   **核心原则**:
    *   **技术前瞻性**: 虽然初期功能简单，但技术选型应为未来可能的复杂功能（如实时数据流、复杂策略回测、多用户系统）留有接口和扩展空间。选择主流且社区活跃的技术栈，可以保证长期的技术支持和生态活力。
    *   **模块化设计**: 各功能模块（如数据获取、数据处理、前端展示）应高度解耦。这不仅便于分工开发和单元测试，也使得未来替换或升级某个模块（例如，从Alpha Vantage切换到其他数据源）变得简单，而不会影响整个系统的稳定性。
    *   **快速迭代**: 在项目初期，选择能够快速搭建原型并验证核心功能的工具至关重要。这有助于我们及时获得反馈并调整开发方向。

*   **后端：Python**
    *   **论证**：Python在数据科学、金融分析领域拥有无与伦比的生态系统。`requests`库是HTTP请求的行业标准，简单可靠；`pandas`库提供了强大的数据处理和分析能力，是处理金融时间序列数据的首选。选择Python可以让我们站在巨人的肩膀上，高效地完成核心功能。
    *   **组件**:
        *   `requests`: 用于与Alpha Vantage API进行HTTP通信。
        *   `pandas`: 用于数据清洗、格式化和分析。
        *   **Web框架 (Dash/Streamlit)**: 用于快速构建交互式Web界面。两者都非常适合数据驱动的应用，能用纯Python代码生成前端组件，极大降低了前端开发门槛，使我们能聚焦于核心业务逻辑。

*   **前端：基于Web框架自动生成**
    *   **论证**：在项目初期，我们不追求复杂的前端交互和定制化视觉效果。使用Dash或Streamlit这类框架，可以通过Python代码直接生成前端UI，避免了额外学习和维护一个独立前端项目（如React, Vue）的复杂性。这完全符合我们快速迭代的原则。当未来业务需求变得更复杂时，我们依然可以选择开发独立的前端应用与后端API进行交互。

*   **数据源：Alpha Vantage API**
    *   **论证**：Alpha Vantage提供了免费且功能丰富的API，覆盖了我们初期所需的股票搜索和OHLCV数据查询功能。其文档清晰，社区支持良好，是作为项目起点数据源的理想选择。模块化的设计确保了我们未来可以平滑地集成或替换为其他数据源。

## 3. 核心功能需求 (MVP)

### 3.1. 股票查询与自动补全

*   **用户故事**: “作为一名用户，我希望在输入框中输入股票代码或公司名称的部分字符时，系统能自动显示匹配的股票列表，这样我就可以快速、准确地选择我想要的股票。”
*   **实现细节**:
    1.  前端界面提供一个文本输入框作为搜索栏。
    2.  监听输入框的文本变化事件（`onchange`）。
    3.  当用户输入时，向后端发送请求，调用Alpha Vantage的 `SYMBOL_SEARCH` API接口。
    4.  后端将API返回的匹配结果（包含股票代码和公司全称）格式化后返回给前端。
    5.  前端在一个下拉建议列表中展示这些结果，用户点击即可选中。

### 3.2. OHLCV数据查询与展示

*   **用户故事**: “作为一名用户，在选定一支股票后，我希望能选择一个具体的日期，并查看该股票当天的开盘价、最高价、最低价、收盘价和成交量信息。”
*   **实现细节**:
    1.  在用户选择股票后，界面上出现一个日期选择器（Date Picker）组件。
    2.  用户选择日期后，后端调用Alpha Vantage的 `TIME_SERIES_DAILY` API，传入选定的股票代码。
    3.  从返回的时间序列数据中，筛选出用户指定日期的数据。
    4.  将该日的OHLCV数据在一个结构清晰、样式美观的表格中展示给用户。
    5.  **明确范围**: MVP阶段 **不包含** 任何形式的图表（如K线图）。

## 4. 数据管理

*   **数据源**: **Alpha Vantage**
    *   **API文档**: [https://www.alphavantage.co/documentation/](https://www.alphavantage.co/documentation/)
    *   **API Key**: `SDMG58OJI9FOIUWW`
    *   **安全提示**: API Key属于敏感信息，**严禁**硬编码在代码中。应通过环境变量或安全的配置文件进行管理。
*   **数据更新策略**: **按需查询 (On-Demand)**。应用本身不存储任何金融数据，所有数据均在用户发起请求时实时从Alpha Vantage API获取。MVP阶段不考虑数据缓存。

## 5. 非功能性需求

*   **用户认证与权限**: **明确排除** 在MVP范围之外。应用对所有用户开放，无需登录。
*   **移动端适配**: **明确排除** 在MVP范围之外。优先保证在桌面端浏览器的良好体验。
*   **性能**: 在单用户操作下应保证流畅。API调用等耗时操作应有明确的加载状态反馈（如加载动画）。
*   **错误处理**: 必须对可预见的错误进行处理，包括但不限于：
    *   API Key无效或达到调用限制。
    *   网络连接失败。
    *   查询的股票或日期无数据。
    *   应向用户展示清晰、友好的错误提示信息。
*   **合规性与数据安全**: 由于不涉及用户个人数据存储和处理，合规性风险较低。主要安全点在于保护好API Key。

## 6. 开发与运维 (DevOps)

*   **版本控制**: **Git**
    *   **分支模型**: 采用 `main` / `dev` 双分支模型。
        *   `main`: 用于存放稳定、可随时部署的版本。
        *   `dev`: 作为主要的开发分支，集成所有新功能。功能开发应在从`dev`切出的`feature/*`分支上进行，完成后合并回`dev`。
*   **自动化测试**: **Pytest**
    *   **测试策略**: 自动化测试是保证代码质量和项目可维护性的基石。
    *   **测试范围**: 在MVP阶段，重点对核心业务逻辑编写单元测试，例如：API客户端的封装、数据处理函数等。

## 7. 项目架构与目录结构

### 7.1. 架构设计原则

我们采用分层模块化架构，确保各模块职责清晰、高度解耦，满足技术前瞻性和可扩展性要求：

*   **数据层 (api/)**: 封装所有外部数据源的访问逻辑，为未来集成多个数据源或切换数据源提供统一接口。
*   **业务逻辑层 (data/)**: 处理数据清洗、格式化、计算等核心业务逻辑，与数据源和UI完全解耦。
*   **表现层 (ui/)**: 专注于用户界面展示和交互，可独立进行UI优化而不影响业务逻辑。
*   **工具层 (utils/)**: 提供通用工具函数，支持代码复用和维护。

### 7.2. 项目目录结构

```
iFinance/
├── src/                    # 源代码目录
│   ├── api/                # 外部API客户端模块
│   │   ├── __init__.py
│   │   ├── alpha_vantage.py    # Alpha Vantage API封装
│   │   └── base_client.py      # API客户端基类（为未来扩展准备）
│   ├── data/               # 数据处理模块
│   │   ├── __init__.py
│   │   ├── processor.py        # 数据清洗和格式化
│   │   └── validator.py        # 数据验证逻辑
│   ├── ui/                 # 前端界面模块
│   │   ├── __init__.py
│   │   ├── components/         # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── search_box.py   # 股票搜索组件
│   │   │   └── data_table.py   # 数据展示表格
│   │   └── app.py              # 主应用入口
│   └── utils/              # 工具函数模块
│       ├── __init__.py
│       ├── config.py           # 配置管理
│       ├── logger.py           # 日志工具
│       └── exceptions.py       # 自定义异常类
├── tests/                  # 测试文件目录
│   ├── __init__.py
│   ├── test_api/
│   ├── test_data/
│   └── test_ui/
├── config/                 # 配置文件目录
│   ├── .env.example            # 环境变量模板
│   └── settings.py             # 应用配置
├── docs/                   # 文档目录
│   └── api_reference.md
├── requirements.txt        # Python依赖管理
├── requirements-dev.txt    # 开发环境依赖
├── .gitignore
├── README.md
└── development_requirements.md
```

## 8. 开发环境配置

### 8.1. 系统要求

*   **Python版本**: 3.8+ （推荐3.9或3.10，确保良好的类型注解支持）
*   **操作系统**: macOS, Linux, Windows（主要开发环境为macOS）
*   **内存**: 最低4GB，推荐8GB+

### 8.2. 开发环境搭建

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发环境额外依赖

# 3. 配置环境变量
cp config/.env.example .env
# 编辑.env文件，添加API Key等配置

# 4. 运行测试确保环境正常
pytest tests/

# 5. 启动开发服务器
python src/ui/app.py
```

### 8.3. 开发工具推荐

*   **IDE**: PyCharm Professional / VS Code（配置Python扩展）
*   **代码格式化**: black, isort
*   **静态分析**: flake8, mypy
*   **Git工具**: SourceTree / GitKraken（可选）

## 9. 代码质量标准

### 9.1. 代码风格规范

*   **遵循PEP 8**: 使用black进行自动格式化
*   **导入排序**: 使用isort管理import语句
*   **行长度**: 最大88字符（black默认）
*   **命名规范**:
    *   变量和函数: snake_case
    *   类名: PascalCase
    *   常量: UPPER_SNAKE_CASE
    *   私有成员: 以单下划线开头

### 9.2. 文档字符串要求

```python
def get_stock_data(symbol: str, date: str) -> Dict[str, Any]:
    """
    获取指定股票在特定日期的OHLCV数据。
    
    Args:
        symbol: 股票代码，如'AAPL'
        date: 查询日期，格式为'YYYY-MM-DD'
    
    Returns:
        包含OHLCV数据的字典
    
    Raises:
        APIError: 当API调用失败时
        DataNotFoundError: 当指定日期无数据时
    """
    pass
```

### 9.3. 类型注解规范

*   所有公共函数必须包含类型注解
*   使用typing模块提供的类型（Dict, List, Optional等）
*   复杂类型使用TypedDict或dataclass定义

## 10. 错误处理与日志

### 10.1. 异常处理策略

*   **API限流处理**: 实现指数退避重试机制，最大重试3次
*   **网络超时**: 设置合理的超时时间（连接5秒，读取30秒）
*   **数据验证**: 对API返回数据进行严格验证，防止格式异常
*   **用户友好错误**: 将技术错误转换为用户可理解的提示信息

### 10.2. 日志管理

```python
# 日志级别配置
DEBUG: 详细的调试信息（仅开发环境）
INFO: 一般信息（API调用、用户操作）
WARNING: 警告信息（API限流、数据异常）
ERROR: 错误信息（API失败、系统异常）
CRITICAL: 严重错误（系统崩溃）
```

## 11. 部署与运行

### 11.1. 本地开发部署

```bash
# 启动开发服务器（支持热重载）
python src/ui/app.py --debug

# 访问地址
http://localhost:8050  # Dash默认端口
# 或
http://localhost:8501  # Streamlit默认端口
```

### 11.2. 环境变量配置

```bash
# .env文件示例
ALPHA_VANTAGE_API_KEY=SDMG58OJI9FOIUWW
DEBUG=True
LOG_LEVEL=INFO
CACHE_ENABLED=False
```

### 11.3. 常见问题排查

*   **API Key无效**: 检查.env文件配置，确认API Key正确
*   **端口占用**: 使用`lsof -i :8050`检查端口占用情况
*   **依赖冲突**: 删除虚拟环境重新创建，或使用`pip check`检查依赖

## 12. 开发实施计划

### 12.1. 开发阶段规划

为确保项目开发的稳定性和可控性，我们将整个开发过程分为五个阶段，每个阶段都有明确的工作内容和预期产出。

#### 第一阶段：项目基础架构搭建
**工作内容：**
1. 创建完整的项目目录结构（src/, tests/, config/, docs/等）
2. 设置Python依赖管理文件（requirements.txt, requirements-dev.txt）
3. 创建基础配置文件（.env.example, settings.py）
4. 设置基础的工具类和异常类框架
5. 初始化测试框架结构

**预期产出：**
- 完整的项目骨架
- 可运行的基础环境
- 为后续开发做好准备

**风险控制：**
- 只创建文件结构和基础配置，不涉及复杂业务逻辑
- 可以快速验证环境是否正确搭建

#### 第二阶段：Alpha Vantage API客户端开发
**工作内容：**
1. 实现Alpha Vantage API的基础客户端类
2. 封装股票搜索功能（SYMBOL_SEARCH API）
3. 封装股票数据获取功能（TIME_SERIES_DAILY API）
4. 添加错误处理和重试机制
5. 编写API客户端的单元测试

**预期产出：**
- 完整的API客户端模块
- 可靠的数据获取功能
- 完善的错误处理机制

#### 第三阶段：数据处理模块开发
**工作内容：**
1. 实现数据清洗和格式化功能
2. 实现数据验证逻辑
3. 处理日期格式转换和数据筛选
4. 编写数据处理模块的单元测试

**预期产出：**
- 稳定的数据处理管道
- 数据质量保证机制
- 灵活的数据格式转换

#### 第四阶段：前端UI组件开发
**工作内容：**
1. 选择并配置Web框架（Dash或Streamlit）
2. 实现股票搜索自动补全组件
3. 实现日期选择器组件
4. 实现OHLCV数据展示表格
5. 基础样式和布局优化

**预期产出：**
- 用户友好的Web界面
- 响应式的交互组件
- 美观的数据展示

#### 第五阶段：功能集成与测试
**工作内容：**
1. 将各模块集成到主应用中
2. 端到端功能测试
3. 错误处理和用户体验优化
4. 性能测试和优化
5. 文档完善

**预期产出：**
- 完整可用的MVP产品
- 全面的测试覆盖
- 完善的用户文档

### 12.2. 开发原则

*   **分步实施**: 每个阶段完成后进行验证，确保功能正常再进入下一阶段
*   **增量开发**: 优先实现核心功能，逐步添加辅助功能
*   **测试驱动**: 每个模块开发完成后立即编写测试，确保代码质量
*   **文档同步**: 代码开发的同时更新相关文档，保持文档的时效性

## 13. 后续扩展方向 (Post-MVP)

*   **数据可视化**: 集成交互式图表，如K线图、成交量图、移动平均线等。
*   **技术分析**: 增加常用技术指标的计算与展示功能。
*   **用户系统**: 引入用户认证，支持创建和管理个人股票池（Portfolio）。
*   **性能优化**: 引入缓存机制（如Redis），减少对外部API的重复调用，提升响应速度。
*   **移动端适配**: 优化UI，使其在移动设备上也能良好地展示和操作。
*   **多数据源集成**: 支持Yahoo Finance、Quandl等多个数据源。
*   **实时数据**: 集成WebSocket实现实时股价推送。