# Python虚拟环境使用指南

## 什么是虚拟环境？

Python虚拟环境是一个独立的Python运行环境，它允许您为每个项目创建隔离的依赖包环境，避免不同项目之间的包版本冲突。

## 为什么要使用虚拟环境？

1. **依赖隔离**：每个项目可以有自己的依赖包版本
2. **系统保护**：避免污染系统Python环境
3. **版本管理**：可以为不同项目使用不同的Python版本
4. **部署一致性**：确保开发和生产环境的一致性

## iFinance项目虚拟环境设置

### 1. 创建虚拟环境

```bash
# 在项目根目录下创建虚拟环境
cd /path/to/iFinance
python3 -m venv venv
```

### 2. 激活虚拟环境

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 3. 安装项目依赖

```bash
# 确保pip是最新版本
pip install --upgrade pip

# 安装生产环境依赖
pip install -r requirements.txt

# 安装开发环境依赖（可选）
pip install -r requirements-dev.txt
```

### 4. 运行项目

```bash
# 启动iFinance应用
python run.py

# 或者运行测试
python test_basic.py
```

### 5. 退出虚拟环境

```bash
deactivate
```

## 常用命令

### 查看已安装的包
```bash
pip list
```

### 生成依赖文件
```bash
pip freeze > requirements.txt
```

### 删除虚拟环境
```bash
# 先退出虚拟环境
deactivate
# 删除虚拟环境目录
rm -rf venv
```

## 最佳实践

1. **每个项目一个虚拟环境**：为每个Python项目创建独立的虚拟环境
2. **版本控制排除**：将`venv/`目录添加到`.gitignore`文件中
3. **依赖文件管理**：定期更新`requirements.txt`文件
4. **环境变量**：使用`.env`文件管理环境变量
5. **文档记录**：在README中记录环境设置步骤

## 故障排除

### 问题1：虚拟环境激活失败
**解决方案：**
- 检查路径是否正确
- 确保有执行权限：`chmod +x venv/bin/activate`

### 问题2：包安装失败
**解决方案：**
- 更新pip：`pip install --upgrade pip`
- 检查网络连接
- 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

### 问题3：Python版本不匹配
**解决方案：**
- 指定Python版本：`python3.9 -m venv venv`
- 使用pyenv管理多个Python版本

## IDE集成

### VS Code
1. 打开项目文件夹
2. 按`Cmd+Shift+P`（macOS）或`Ctrl+Shift+P`（Windows/Linux）
3. 输入"Python: Select Interpreter"
4. 选择虚拟环境中的Python解释器

### PyCharm
1. File → Settings → Project → Python Interpreter
2. 点击齿轮图标 → Add
3. 选择"Existing environment"
4. 选择虚拟环境中的Python解释器

## 总结

使用虚拟环境是Python开发的最佳实践，它能够：
- 保持项目依赖的独立性
- 避免版本冲突
- 简化部署过程
- 提高开发效率

对于iFinance项目，我们已经配置好了完整的虚拟环境，您只需要按照上述步骤激活环境并安装依赖即可开始开发。