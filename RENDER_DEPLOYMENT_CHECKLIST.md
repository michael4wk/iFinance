# 🚀 Render 部署检查清单

## ✅ 部署前准备

### 1. 账户准备
- [ ] 拥有 GitHub 账户
- [ ] 代码已推送到 GitHub 仓库
- [ ] 获得有效的 Alpha Vantage API Key

### 2. 验证 API Key
```bash
python3 verify_api_key.py your_api_key_here
```
- [ ] 看到 "✅ 验证成功" 消息

---

## 🎯 Render 部署步骤

### 第一步：注册 Render
1. [ ] 访问 [render.com](https://render.com)
2. [ ] 点击 "Get Started" 或 "Sign Up"
3. [ ] 选择 "Sign up with GitHub"
4. [ ] 授权 Render 访问 GitHub
5. [ ] 验证邮箱地址

### 第二步：创建 Web Service
1. [ ] 点击 "New +" → "Web Service"
2. [ ] 选择 "Build and deploy from a Git repository"
3. [ ] 连接 `michael4wk/iFinance` 仓库
4. [ ] 点击 "Connect"

### 第三步：配置设置

**基本设置：**
- [ ] Name: `ifinance`
- [ ] Region: `Oregon (US West)` 或 `Singapore`
- [ ] Branch: `dev`
- [ ] Root Directory: 留空

**构建设置：**
- [ ] Runtime: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 src.main:server`

**计划选择：**
- [ ] 选择 "Free" 计划

### 第四步：环境变量

添加以下环境变量：

- [ ] `ALPHA_VANTAGE_API_KEY` = `your_actual_api_key`
- [ ] `ENVIRONMENT` = `production`
- [ ] `DEBUG` = `false`
- [ ] `TZ` = `Asia/Shanghai`

### 第五步：部署
1. [ ] 点击 "Create Web Service"
2. [ ] 等待部署完成（3-8分钟）
3. [ ] 确认状态显示为 "Live"

---

## 🧪 部署验证

### 功能测试
- [ ] 页面正常加载
- [ ] 搜索功能正常（测试 "AAPL"）
- [ ] 数据查询正常
- [ ] 货币显示正确（测试英国股票）

### 获取应用地址
- [ ] 复制应用URL：`https://ifinance-xxxx.onrender.com`
- [ ] 在浏览器中测试访问

---

## ⚠️ 重要提醒

### 免费计划限制
- ✅ **750小时/月** 免费运行时间
- ⚠️ **15分钟无活动** 后自动休眠
- ⏱️ **冷启动时间** 30秒-2分钟
- 💾 **512MB RAM** + 共享CPU

### API Key 安全
- 🔒 **不要** 在代码中硬编码 API Key
- 🔒 **不要** 提交 API Key 到 GitHub
- 🔒 **只在** Render 环境变量中设置

### 自动部署
- 🔄 推送到 `dev` 分支会自动触发重新部署
- 📝 可在 Render Dashboard 查看部署日志

---

## 🆘 快速故障排除

| 问题 | 解决方案 |
|------|----------|
| 构建失败 | 检查 `requirements.txt` 和依赖包 |
| 启动失败 | 验证启动命令和 `src.main:server` |
| API 错误 | 验证 API Key 有效性 |
| 访问慢 | 正常现象，冷启动需要时间 |

---

## 📞 获取帮助

- 📚 [Render 官方文档](https://render.com/docs)
- 💬 [Render 社区](https://community.render.com)
- 🐛 [项目 Issues](https://github.com/michael4wk/iFinance/issues)

---

**🎉 部署成功后，你的应用将在云端 24/7 运行！**