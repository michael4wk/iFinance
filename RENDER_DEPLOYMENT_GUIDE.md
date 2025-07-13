# Render 部署配置指南

## 问题诊断

经过本地测试确认，应用代码和API连接在本地环境完全正常。Render部署后无响应的根本原因是：**Render平台未配置必要的环境变量**。

## 解决方案：在Render Dashboard配置环境变量

### 步骤1：登录Render Dashboard
1. 访问 [Render Dashboard](https://dashboard.render.com/)
2. 登录您的账户
3. 找到您的 `ifinance-durp` 服务

### 步骤2：配置环境变量
1. 点击您的服务名称进入服务详情页
2. 在左侧菜单中点击 **"Environment"**
3. 点击 **"Add Environment Variable"** 按钮
4. 添加以下环境变量：

#### 必需的环境变量

| 变量名 | 值 | 说明 |
|--------|----|---------|
| `ALPHA_VANTAGE_API_KEY` | `您的API密钥` | Alpha Vantage API密钥（必需） |
| `ALPHA_VANTAGE_BASE_URL` | `https://www.alphavantage.co/query` | API基础URL |
| `DEBUG` | `False` | 生产环境建议设为False |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `HOST` | `0.0.0.0` | 服务器监听地址（Render需要0.0.0.0） |
| `PORT` | `10000` | 端口号（Render默认使用10000） |
| `REQUEST_TIMEOUT` | `30` | API请求超时时间 |
| `MAX_RETRIES` | `3` | 最大重试次数 |
| `RETRY_DELAY` | `1` | 重试延迟时间 |

#### 重要提醒
- **ALPHA_VANTAGE_API_KEY** 是最关键的环境变量，没有它应用无法正常工作
- **HOST** 必须设置为 `0.0.0.0`，这是Render平台的要求
- **PORT** 建议设置为 `10000`，这是Render的默认端口

### 步骤3：保存并重新部署
1. 添加完所有环境变量后，点击 **"Save Changes"**
2. Render会自动触发重新部署
3. 等待部署完成（通常需要几分钟）

### 步骤4：验证部署
1. 部署完成后，访问您的应用：`https://ifinance-durp.onrender.com`
2. 尝试搜索股票代码（如：AAPL）
3. 点击查询按钮，应该能看到数据加载

## 获取Alpha Vantage API密钥

如果您还没有API密钥：

1. 访问 [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. 点击 "Get your free API key today!"
3. 填写注册信息
4. 获取免费API密钥
5. 将密钥添加到Render环境变量中

## 常见问题排查

### 1. 应用仍然无响应
- 检查所有环境变量是否正确设置
- 确认API密钥有效且未超出使用限制
- 查看Render的部署日志是否有错误信息

### 2. API调用失败
- 验证ALPHA_VANTAGE_API_KEY是否正确
- 检查网络连接
- 确认API密钥未达到每日调用限制

### 3. 部署失败
- 检查HOST是否设置为0.0.0.0
- 确认PORT设置正确
- 查看构建日志中的错误信息

## 监控和维护

### 查看应用日志
1. 在Render Dashboard中点击您的服务
2. 点击 "Logs" 标签
3. 查看实时日志输出

### 性能监控
- 监控API调用频率，避免超出限制
- 关注应用响应时间
- 定期检查错误日志

## 联系支持

如果按照以上步骤操作后仍有问题：
1. 检查Render的服务状态页面
2. 查看详细的错误日志
3. 联系Render技术支持

---

**注意**：配置环境变量后，Render会自动重新部署您的应用。请耐心等待部署完成后再进行测试。