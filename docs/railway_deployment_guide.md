# Railway 部署指南

本指南将指导你一步步完成 iFinance 应用在 Railway 平台的部署。

## 前置条件

- ✅ GitHub 账户
- ✅ Alpha Vantage API Key
- ✅ 项目代码已推送到 GitHub 仓库

## 第一步：准备 Railway 账户

### 1.1 注册 Railway 账户

1. 访问 [Railway 官网](https://railway.app)
2. 点击右上角 "Login" 按钮
3. 选择 "Continue with GitHub" 使用 GitHub 账户登录
4. 授权 Railway 访问你的 GitHub 账户

### 1.2 验证账户

- Railway 会自动验证你的 GitHub 账户
- 新用户将获得每月 $5 的免费额度
- 免费额度包含 500 小时的运行时间

## 第二步：创建新项目

### 2.1 创建项目

1. 登录 Railway 后，点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 在仓库列表中找到 `michael4wk/iFinance`
4. 点击 "Deploy Now"

### 2.2 项目配置

- Railway 会自动检测到 `Procfile` 和 `railway.toml` 配置文件
- 系统将使用 Nixpacks 构建器自动构建项目
- 构建过程大约需要 2-5 分钟

## 第三步：配置环境变量

### 3.1 进入项目设置

1. 在 Railway 项目页面，点击项目名称
2. 点击 "Variables" 标签页
3. 点击 "New Variable" 添加环境变量

### 3.2 添加必需的环境变量

**必需变量：**
```
ALPHA_VANTAGE_API_KEY=your_actual_api_key_here
```

**推荐变量：**
```
ENVIRONMENT=production
DEBUG=false
TZ=Asia/Shanghai
```

### 3.3 获取 Alpha Vantage API Key

如果你还没有 API Key：
1. 访问 [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. 填写表单申请免费 API Key
3. 查收邮件获取 API Key
4. 将 API Key 添加到 Railway 环境变量中

## 第四步：部署和验证

### 4.1 触发部署

1. 添加环境变量后，Railway 会自动重新部署
2. 在 "Deployments" 标签页查看部署进度
3. 部署成功后状态显示为 "Success"

### 4.2 获取访问地址

1. 在项目页面点击 "Settings" 标签
2. 在 "Domains" 部分点击 "Generate Domain"
3. Railway 会生成一个类似 `your-app-name.up.railway.app` 的域名
4. 点击域名即可访问你的应用

### 4.3 验证应用功能

访问生成的域名，确认：
- ✅ 页面正常加载
- ✅ 股票搜索功能正常
- ✅ 数据查询功能正常
- ✅ 货币符号显示正确

## 第五步：监控和维护

### 5.1 查看应用日志

1. 在项目页面点击 "Logs" 标签
2. 查看实时日志输出
3. 监控错误和警告信息

### 5.2 监控资源使用

1. 在 "Metrics" 标签查看资源使用情况
2. 监控内存、CPU 和网络使用
3. 关注免费额度使用情况

### 5.3 自动部署设置

- Railway 默认启用自动部署
- 每次推送到 GitHub 仓库都会触发重新部署
- 可在 "Settings" → "Service" 中调整部署设置

## 故障排除

### 常见问题

**问题 1：部署失败**
- 检查 `requirements.txt` 是否包含所有依赖
- 确认 `Procfile` 和 `railway.toml` 配置正确
- 查看构建日志中的错误信息

**问题 2：应用启动失败**
- 检查环境变量是否正确设置
- 确认 `ALPHA_VANTAGE_API_KEY` 有效
- 查看应用日志中的错误信息

**问题 3：功能异常**
- 检查 API Key 是否有效且未超出限制
- 确认网络连接正常
- 查看应用日志排查具体错误

### 获取帮助

- Railway 文档：https://docs.railway.app
- Railway 社区：https://help.railway.app
- 项目 GitHub Issues：https://github.com/michael4wk/iFinance/issues

## 成本优化

### 免费额度管理

- 每月 $5 免费额度
- 应用会在无访问时自动休眠
- 休眠状态不消耗运行时间
- 首次访问时会有 10-30 秒的冷启动时间

### 优化建议

1. **合理使用**：避免频繁的无意义请求
2. **监控使用量**：定期检查资源使用情况
3. **代码优化**：优化应用性能减少资源消耗

## 下一步

部署成功后，你可以：

1. **分享应用**：将域名分享给其他用户
2. **自定义域名**：在 Railway 中绑定自己的域名
3. **功能扩展**：继续开发新功能并自动部署
4. **监控优化**：根据使用情况优化应用性能

---

**恭喜！** 🎉 你已经成功将 iFinance 应用部署到 Railway 平台。现在你拥有了一个可以公开访问的金融数据查询应用！