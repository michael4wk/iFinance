# Render 部署指南

本指南将指导你一步步完成 iFinance 应用在 Render 平台的免费部署。

## 🎯 部署概览

- **平台**: Render (render.com)
- **费用**: 完全免费
- **功能**: 750小时/月免费运行时间
- **限制**: 15分钟无活动后休眠，冷启动30秒-2分钟

---

## 第一步：注册 Render 账户

### 1.1 访问 Render 官网

1. 打开浏览器，访问 [https://render.com](https://render.com)
2. 点击右上角的 **"Get Started"** 或 **"Sign Up"** 按钮

### 1.2 使用 GitHub 账户注册

1. 在注册页面，选择 **"Sign up with GitHub"**
2. 如果未登录 GitHub，会跳转到 GitHub 登录页面
3. 输入你的 GitHub 用户名和密码
4. 授权 Render 访问你的 GitHub 账户
   - 点击 **"Authorize Render"**
   - Render 需要访问你的仓库来进行部署

### 1.3 完成账户设置

1. 授权成功后，会跳转回 Render
2. 填写基本信息（如果需要）
3. 验证邮箱地址（查收邮件并点击验证链接）

---

## 第二步：创建 Web Service

### 2.1 进入 Dashboard

1. 登录成功后，你会看到 Render Dashboard
2. 点击 **"New +"** 按钮
3. 选择 **"Web Service"**

### 2.2 连接 GitHub 仓库

1. 在 "Create a new Web Service" 页面
2. 选择 **"Build and deploy from a Git repository"**
3. 点击 **"Next"**
4. 在仓库列表中找到 `michael4wk/iFinance`
   - 如果没有看到，点击 **"Configure account"** 重新授权
5. 点击仓库右侧的 **"Connect"** 按钮

---

## 第三步：配置部署设置

### 3.1 基本设置

在配置页面填写以下信息：

**Name（服务名称）**
```
ifinance
```

**Region（地区）**
```
Oregon (US West) 或 Singapore（选择离你较近的）
```

**Branch（分支）**
```
main
```

**Root Directory（根目录）**
```
留空（使用仓库根目录）
```

### 3.2 构建设置

**Runtime（运行环境）**
```
Python 3
```

**Build Command（构建命令）**
```
pip install -r requirements.txt
```

**Start Command（启动命令）**
```
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 src.main:server
```

### 3.3 计划选择

1. 选择 **"Free"** 计划
2. 确认免费计划的限制：
   - 750小时/月运行时间
   - 15分钟无活动后休眠
   - 512MB RAM
   - 共享CPU

---

## 第四步：配置环境变量

### 4.1 添加环境变量

在配置页面向下滚动到 **"Environment Variables"** 部分：

**必需变量：**

1. **ALPHA_VANTAGE_API_KEY**
   ```
   Key: ALPHA_VANTAGE_API_KEY
   Value: your_actual_api_key_here
   ```
   
2. **ENVIRONMENT**
   ```
   Key: ENVIRONMENT
   Value: production
   ```
   
3. **DEBUG**
   ```
   Key: DEBUG
   Value: false
   ```
   
4. **TZ**
   ```
   Key: TZ
   Value: Asia/Shanghai
   ```

### 4.2 验证 API Key

在添加 API Key 之前，确保它是有效的：

1. 在本地运行验证脚本：
   ```bash
   python3 verify_api_key.py your_api_key_here
   ```

2. 确认看到 "✅ 验证成功" 的消息

---

## 第五步：开始部署

### 5.1 创建服务

1. 检查所有配置信息
2. 点击页面底部的 **"Create Web Service"** 按钮
3. Render 开始自动部署过程

### 5.2 监控部署进度

1. 部署开始后，你会看到实时日志
2. 部署过程包括：
   - 克隆代码仓库
   - 安装 Python 依赖
   - 启动应用程序
3. 整个过程大约需要 3-8 分钟

### 5.3 部署状态说明

- **Building**: 正在构建应用
- **Deploy**: 正在部署
- **Live**: 部署成功，应用正在运行
- **Failed**: 部署失败，需要检查日志

---

## 第六步：验证部署

### 6.1 获取应用地址

1. 部署成功后，在服务页面顶部会显示应用URL
2. URL 格式类似：`https://ifinance-xxxx.onrender.com`
3. 点击URL或复制到浏览器中打开

### 6.2 测试应用功能

访问应用后，测试以下功能：

1. **页面加载**
   - ✅ 页面正常显示
   - ✅ 没有错误信息

2. **股票搜索**
   - 在搜索框输入 "AAPL"
   - ✅ 出现苹果公司的搜索结果

3. **数据查询**
   - 选择一个股票和日期
   - 点击查询按钮
   - ✅ 显示股票数据和货币信息

4. **货币显示**
   - 测试英国股票（如 AZN.LON）
   - ✅ 确认显示 "p GBX" 货币符号

---

## 第七步：监控和维护

### 7.1 查看应用日志

1. 在 Render Dashboard 中点击你的服务
2. 点击 **"Logs"** 标签
3. 查看实时日志输出
4. 监控错误和警告信息

### 7.2 监控资源使用

1. 在服务页面查看 **"Metrics"** 标签
2. 监控：
   - CPU 使用率
   - 内存使用率
   - 响应时间
   - 请求数量

### 7.3 自动部署设置

- Render 默认启用自动部署
- 每次推送到 GitHub 的 `main` 分支都会触发重新部署
- 可以在 **"Settings"** 中调整自动部署设置

---

## 🚨 故障排除

### 常见问题及解决方案

#### 问题 1：构建失败

**症状**: 在 "Building" 阶段失败

**解决方案**:
1. 检查 `requirements.txt` 文件是否存在
2. 确认所有依赖包名称正确
3. 查看构建日志中的具体错误信息

#### 问题 2：启动失败

**症状**: 构建成功但应用无法启动

**解决方案**:
1. 检查启动命令是否正确
2. 确认 `src/main.py` 中的 `server` 对象存在
3. 检查环境变量是否正确设置

#### 问题 3：API 错误

**症状**: 应用启动但功能异常

**解决方案**:
1. 验证 `ALPHA_VANTAGE_API_KEY` 是否有效
2. 检查 API 调用频率是否超限
3. 查看应用日志中的 API 错误信息

#### 问题 4：应用休眠

**症状**: 访问时需要等待很久

**说明**: 这是正常现象
- 15分钟无访问后应用会自动休眠
- 首次访问需要 30秒-2分钟 冷启动时间
- 这是免费计划的限制

---

## 💡 优化建议

### 性能优化

1. **减少冷启动时间**
   - 优化应用启动速度
   - 减少不必要的依赖

2. **缓存策略**
   - 合理使用数据缓存
   - 避免重复的 API 调用

### 成本管理

1. **监控使用时间**
   - 定期检查月度使用时间
   - 750小时通常足够个人项目使用

2. **优化资源使用**
   - 避免不必要的后台任务
   - 合理设置超时时间

---

## 🎉 部署成功！

恭喜！你已经成功将 iFinance 应用部署到 Render 平台。

### 下一步可以做什么：

1. **分享应用**
   - 将应用URL分享给朋友和同事
   - 在简历或作品集中展示

2. **自定义域名**（可选）
   - 在 Render 中绑定自己的域名
   - 需要付费计划

3. **功能扩展**
   - 继续开发新功能
   - 每次推送代码都会自动部署

4. **监控优化**
   - 根据使用情况优化性能
   - 监控用户反馈

---

## 📞 获取帮助

如果遇到问题：

- **Render 官方文档**: https://render.com/docs
- **Render 社区**: https://community.render.com
- **项目 GitHub Issues**: https://github.com/michael4wk/iFinance/issues
- **Alpha Vantage 支持**: https://www.alphavantage.co/support/

---

**🚀 享受你的云端金融数据应用吧！**