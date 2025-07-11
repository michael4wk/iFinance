# Railway 部署检查清单

在开始 Railway 部署之前，请确认以下所有项目都已完成：

## 📋 部署前检查清单

### ✅ 代码准备
- [x] 代码已推送到 GitHub 仓库
- [x] 所有功能测试通过
- [x] 货币显示问题已修复
- [x] 应用在本地正常运行

### ✅ 部署文件
- [x] `Procfile` 文件存在且配置正确
- [x] `railway.toml` 文件存在且配置正确
- [x] `requirements.txt` 包含所有必需依赖
- [x] `src/main.py` 正确导出 server 对象

### ✅ 环境配置
- [x] `.env.example` 文件提供了环境变量模板
- [x] `.gitignore` 正确配置，不会提交敏感信息
- [x] 生产环境配置已优化

### 🔑 API 密钥准备
- [ ] **获取 Alpha Vantage API Key**
  - 访问：https://www.alphavantage.co/support/#api-key
  - 填写申请表单
  - 查收邮件获取 API Key
  - 测试 API Key 有效性

### 🚀 Railway 账户准备
- [ ] **注册 Railway 账户**
  - 访问：https://railway.app
  - 使用 GitHub 账户登录
  - 完成账户验证

## 🎯 快速部署步骤

### 第 1 步：创建 Railway 项目
1. 登录 Railway
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择 `michael4wk/iFinance` 仓库
5. 点击 "Deploy Now"

### 第 2 步：配置环境变量
在 Railway 项目的 "Variables" 标签页添加：
```
ALPHA_VANTAGE_API_KEY=your_actual_api_key_here
ENVIRONMENT=production
DEBUG=false
TZ=Asia/Shanghai
```

### 第 3 步：等待部署完成
- 查看 "Deployments" 标签页
- 等待状态变为 "Success"
- 生成访问域名

### 第 4 步：验证部署
- 访问生成的域名
- 测试股票搜索功能
- 确认数据显示正常

## ⚠️ 重要提醒

1. **API Key 安全**：
   - 不要在代码中硬编码 API Key
   - 只在 Railway 环境变量中设置
   - 定期检查 API Key 使用情况

2. **免费额度管理**：
   - 每月 $5 免费额度
   - 500 小时运行时间
   - 应用会自动休眠节省资源

3. **监控和维护**：
   - 定期查看应用日志
   - 监控资源使用情况
   - 及时处理错误和警告

## 📞 获取帮助

如果遇到问题，可以：
- 查看详细的 [Railway 部署指南](docs/railway_deployment_guide.md)
- 访问 [Railway 官方文档](https://docs.railway.app)
- 在项目 [GitHub Issues](https://github.com/michael4wk/iFinance/issues) 中提问

---

**准备好了吗？** 🚀 让我们开始部署吧！