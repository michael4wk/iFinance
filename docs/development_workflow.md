# iFinance 开发工作流程指南

> 本文档详细说明了 iFinance 项目的标准开发工作流程，包括分支管理、测试策略、部署流程等。

## 📋 目录

- [开发环境设置](#开发环境设置)
- [标准开发工作流程](#标准开发工作流程)
- [分支管理策略](#分支管理策略)
- [测试策略](#测试策略)
- [部署流程](#部署流程)
- [代码质量保证](#代码质量保证)
- [常用命令参考](#常用命令参考)

## 🛠️ 开发环境设置

### 1. 虚拟环境管理

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 2. 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入必要的配置
# - ALPHA_VANTAGE_API_KEY
# - 其他配置项
```

### 3. 项目规则

- **始终使用 `start.sh` 脚本启动应用**
- **在同一虚拟环境中进行开发和测试**
- **确保系统环境不被篡改，避免潜在安全问题**

## 🔄 标准开发工作流程

### 阶段 1: 功能开发

```bash
# 1. 确保在 dev 分支
git checkout dev
git pull origin dev

# 2. 创建功能分支（可选，适用于大型功能）
git checkout -b feature/new-feature-name

# 3. 开发新功能
# - 编写代码
# - 添加注释
# - 编写测试用例
```

### 阶段 2: 本地测试验证

```bash
# 1. 使用启动脚本测试
./start.sh

# 2. 运行单元测试
pytest tests/ -v

# 3. 运行代码覆盖率测试
pytest --cov=src --cov-report=html

# 4. 手动功能测试
# - 访问 http://localhost:8050
# - 测试所有相关功能
# - 验证新功能正常工作
# - 确保现有功能未受影响
```

### 阶段 3: 代码质量检查

```bash
# 1. 代码格式化
black src/ tests/
isort src/ tests/

# 2. 代码静态检查
flake8 src/ tests/
mypy src/

# 3. 安全检查（可选）
bandit -r src/
```

### 阶段 4: 提交到开发分支

```bash
# 1. 添加文件到暂存区
git add .

# 2. 提交更改（使用规范的提交信息）
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修复bug描述"
# 或
git commit -m "docs: 更新文档"

# 3. 推送到远程仓库
git push origin dev
# 或推送功能分支
git push origin feature/new-feature-name
```

### 阶段 5: 部署前测试（重要！）

```bash
# 1. 本地测试 gunicorn 启动
gunicorn --bind 127.0.0.1:8050 --workers 1 --timeout 120 src.main:server

# 2. 在 Railway 创建测试环境
# - 连接 dev 分支
# - 配置环境变量
# - 验证部署成功
# - 进行功能测试
```

### 阶段 6: 合并到主分支

```bash
# 1. 切换到主分支
git checkout main
git pull origin main

# 2. 合并开发分支
git merge dev
# 或合并功能分支
git merge feature/new-feature-name

# 3. 创建版本标签
git tag v1.x.x -m "版本 1.x.x: 功能描述"

# 4. 推送到远程仓库
git push origin main --tags
```

### 阶段 7: 生产环境部署

- Railway 自动检测 main 分支更新
- 自动部署到生产环境
- 监控部署状态和应用健康

## 🌿 分支管理策略

### 分支结构

```
main (生产分支)
├── v1.0.0 (标签)
├── v1.1.0 (标签)
└── v1.2.0 (标签)

dev (开发分支)
├── feature/user-auth (功能分支)
├── feature/data-export (功能分支)
└── hotfix/critical-bug (热修复分支)
```

### 分支用途

- **main**: 生产环境分支，只包含稳定、经过测试的代码
- **dev**: 开发分支，用于集成和测试新功能
- **feature/***: 功能分支，用于开发特定功能
- **hotfix/***: 热修复分支，用于紧急修复生产环境问题

### 分支保护规则

- **main 分支**：
  - 禁止直接推送
  - 必须通过 Pull Request 合并
  - 需要代码审查
  - 必须通过所有测试

## 🧪 测试策略

### 测试层级

1. **单元测试** (`tests/test_*`)
   - 测试单个函数和类
   - 快速执行，高覆盖率

2. **集成测试** (`tests/integration/`)
   - 测试模块间交互
   - API 调用测试

3. **端到端测试** (`tests/e2e/`)
   - 完整用户流程测试
   - UI 交互测试

### 测试命令

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api/test_alpha_vantage.py

# 运行带覆盖率的测试
pytest --cov=src --cov-report=html

# 运行性能测试
pytest tests/performance/ --benchmark-only
```

### 测试环境

- **本地测试**: 使用 `./start.sh` 启动
- **CI/CD 测试**: GitHub Actions 自动运行
- **云端测试**: Railway 测试环境

## 🚀 部署流程

### 环境配置

| 环境 | 分支 | 用途 | 访问方式 |
|------|------|------|----------|
| 开发环境 | dev | 功能开发和测试 | 本地 localhost:8050 |
| 测试环境 | dev | 云端集成测试 | Railway 测试域名 |
| 生产环境 | main | 正式服务 | Railway 生产域名 |

### 部署配置文件

- **Procfile**: 定义应用启动命令
- **railway.toml**: Railway 专用配置
- **requirements.txt**: 生产环境依赖
- **.env.example**: 环境变量模板

### 部署检查清单

- [ ] 本地测试通过
- [ ] 代码质量检查通过
- [ ] 单元测试覆盖率 > 80%
- [ ] 云端测试环境验证通过
- [ ] 环境变量配置正确
- [ ] 数据库迁移（如需要）
- [ ] 监控和日志配置

## 📊 代码质量保证

### 代码规范

```bash
# 代码格式化
black src/ tests/ --line-length 88

# 导入排序
isort src/ tests/ --profile black

# 代码检查
flake8 src/ tests/ --max-line-length 88

# 类型检查
mypy src/ --strict
```

### 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例**:
```
feat(api): 添加股票搜索自动补全功能

- 实现基于 Alpha Vantage 的股票搜索
- 添加防抖动优化
- 增加缓存机制提升性能

Closes #123
```

## 📚 常用命令参考

### Git 操作

```bash
# 查看当前状态
git status

# 查看提交历史
git log --oneline -10

# 查看分支
git branch -a

# 切换分支
git checkout <branch-name>

# 创建并切换分支
git checkout -b <new-branch>

# 合并分支
git merge <branch-name>

# 删除分支
git branch -d <branch-name>

# 推送标签
git push origin --tags
```

### 项目管理

```bash
# 启动应用
./start.sh

# 安装依赖
pip install -r requirements.txt

# 更新依赖
pip freeze > requirements.txt

# 清理缓存
find . -type d -name "__pycache__" -delete
find . -name "*.pyc" -delete
```

### Railway 部署

```bash
# 本地测试 gunicorn
gunicorn --bind 127.0.0.1:8050 src.main:server

# 检查部署配置
cat Procfile
cat railway.toml
```

## 🔧 故障排除

### 常见问题

1. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **依赖冲突**
   ```bash
   # 检查依赖
   pip check
   
   # 更新 pip
   pip install --upgrade pip
   ```

3. **测试失败**
   ```bash
   # 详细测试输出
   pytest -v -s
   
   # 只运行失败的测试
   pytest --lf
   ```

4. **部署失败**
   - 检查环境变量配置
   - 验证 Procfile 语法
   - 查看 Railway 部署日志

## 📝 最佳实践

1. **开发习惯**
   - 频繁提交，小步快跑
   - 编写有意义的提交信息
   - 及时更新文档

2. **测试习惯**
   - 先写测试，再写代码 (TDD)
   - 保持高测试覆盖率
   - 定期运行完整测试套件

3. **部署习惯**
   - 永远先在测试环境验证
   - 保持生产环境配置简洁
   - 监控应用性能和错误

4. **协作习惯**
   - 及时同步远程分支
   - 解决冲突时保持沟通
   - 代码审查时给出建设性意见

---

**文档版本**: v1.0  
**最后更新**: 2024年  
**维护者**: iFinance 开发团队

> 💡 **提示**: 本文档会随着项目发展持续更新，建议定期查看最新版本。