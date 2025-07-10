#!/bin/bash

# iFinance 应用启动脚本
# 自动激活虚拟环境并启动应用

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 iFinance 智能金融数据查询系统${NC}"
echo -e "${BLUE}======================================${NC}"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}🔧 激活虚拟环境...${NC}"
source venv/bin/activate

# 检查依赖是否安装
echo -e "${BLUE}📦 检查依赖包...${NC}"
if ! python -c "import dash" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  依赖包未安装，正在安装...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 依赖包安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖包已安装${NC}"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，正在创建示例文件...${NC}"
    cp config/.env.example .env
    echo -e "${YELLOW}📝 请编辑 .env 文件，设置您的 Alpha Vantage API Key${NC}"
fi

# 运行基础测试
echo -e "${BLUE}🧪 运行基础功能测试...${NC}"
if python test_basic.py; then
    echo -e "${GREEN}✅ 基础功能测试通过${NC}"
else
    echo -e "${RED}❌ 基础功能测试失败，请检查配置${NC}"
    exit 1
fi

# 启动应用
echo -e "${BLUE}🌐 启动 Web 应用...${NC}"
echo -e "${GREEN}📱 应用将在 http://127.0.0.1:8050 启动${NC}"
echo -e "${YELLOW}💡 按 Ctrl+C 停止应用${NC}"
echo ""

python run.py