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

# 端口管理函数
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口可用
    fi
}

kill_port() {
    local port=$1
    echo -e "${YELLOW}🔧 检测到端口 $port 被占用，正在清理...${NC}"
    local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✅ 端口 $port 已清理${NC}"
    fi
}

find_available_port() {
    local start_port=$1
    local port=$start_port
    while [ $port -le $((start_port + 50)) ]; do
        if ! check_port $port; then
            echo $port
            return
        fi
        port=$((port + 1))
    done
    echo $start_port  # 如果都被占用，返回起始端口
}

# 运行基础测试（可选）
if [ -f "test_basic.py" ]; then
    echo -e "${BLUE}🧪 运行基础功能测试...${NC}"
    if python test_basic.py; then
        echo -e "${GREEN}✅ 基础功能测试通过${NC}"
    else
        echo -e "${YELLOW}⚠️  基础功能测试失败，但继续启动应用${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未找到测试文件，跳过测试${NC}"
fi

# 端口管理和应用启动
echo -e "${BLUE}🌐 准备启动 Web 应用...${NC}"

# 默认端口
DEFAULT_PORT=8050
SELECTED_PORT=$DEFAULT_PORT

# 检查命令行参数
AUTO_MODE=false
FORCE_KILL=false
CUSTOM_PORT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO_MODE=true
            shift
            ;;
        --kill)
            FORCE_KILL=true
            shift
            ;;
        --port)
            CUSTOM_PORT="$2"
            shift 2
            ;;
        *)
            echo -e "${YELLOW}未知参数: $1${NC}"
            echo -e "${BLUE}用法: $0 [--auto] [--kill] [--port PORT]${NC}"
            echo -e "  --auto: 自动模式，端口被占用时自动选择其他端口"
            echo -e "  --kill: 强制清理默认端口"
            echo -e "  --port: 指定自定义端口"
            shift
            ;;
    esac
done

# 如果指定了自定义端口
if [ ! -z "$CUSTOM_PORT" ]; then
    if [[ "$CUSTOM_PORT" =~ ^[0-9]+$ ]] && [ "$CUSTOM_PORT" -ge 1024 ] && [ "$CUSTOM_PORT" -le 65535 ]; then
        DEFAULT_PORT=$CUSTOM_PORT
        echo -e "${BLUE}🔧 使用自定义端口: $DEFAULT_PORT${NC}"
    else
        echo -e "${RED}❌ 无效端口号: $CUSTOM_PORT，使用默认端口 $DEFAULT_PORT${NC}"
    fi
fi

# 检查默认端口是否被占用
if check_port $DEFAULT_PORT; then
    echo -e "${YELLOW}⚠️  端口 $DEFAULT_PORT 被占用${NC}"
    
    if [ "$FORCE_KILL" = true ]; then
        # 强制清理模式
        kill_port $DEFAULT_PORT
        SELECTED_PORT=$DEFAULT_PORT
    elif [ "$AUTO_MODE" = true ]; then
        # 自动模式：直接选择其他端口
        SELECTED_PORT=$(find_available_port $((DEFAULT_PORT + 1)))
        echo -e "${GREEN}✅ 自动选择端口: $SELECTED_PORT${NC}"
    else
        # 交互模式
        echo -e "${BLUE}选择处理方式:${NC}"
        echo -e "  ${GREEN}1)${NC} 清理端口 $DEFAULT_PORT 并使用"
        echo -e "  ${GREEN}2)${NC} 自动选择其他可用端口"
        echo -e "  ${GREEN}3)${NC} 手动指定端口"
        
        read -t 10 -p "请选择 (1/2/3, 默认为2, 10秒后自动选择): " choice
        choice=${choice:-2}
        
        case $choice in
            1)
                kill_port $DEFAULT_PORT
                SELECTED_PORT=$DEFAULT_PORT
                ;;
            2)
                SELECTED_PORT=$(find_available_port $((DEFAULT_PORT + 1)))
                echo -e "${GREEN}✅ 自动选择端口: $SELECTED_PORT${NC}"
                ;;
            3)
                read -t 10 -p "请输入端口号 (10秒后自动选择): " custom_port
                if [[ "$custom_port" =~ ^[0-9]+$ ]] && [ "$custom_port" -ge 1024 ] && [ "$custom_port" -le 65535 ]; then
                    if check_port $custom_port; then
                        echo -e "${YELLOW}端口 $custom_port 被占用，自动选择其他端口${NC}"
                        SELECTED_PORT=$(find_available_port $((custom_port + 1)))
                    else
                        SELECTED_PORT=$custom_port
                    fi
                else
                    echo -e "${RED}❌ 无效端口号，使用自动选择${NC}"
                    SELECTED_PORT=$(find_available_port $((DEFAULT_PORT + 1)))
                fi
                ;;
            *)
                SELECTED_PORT=$(find_available_port $((DEFAULT_PORT + 1)))
                echo -e "${GREEN}✅ 自动选择端口: $SELECTED_PORT${NC}"
                ;;
        esac
    fi
else
    echo -e "${GREEN}✅ 端口 $DEFAULT_PORT 可用${NC}"
fi

# 启动应用
echo -e "${BLUE}🚀 启动应用...${NC}"
echo -e "${GREEN}📱 应用将在 http://127.0.0.1:$SELECTED_PORT 启动${NC}"
echo -e "${YELLOW}💡 按 Ctrl+C 停止应用${NC}"
echo ""

# 使用选定的端口启动应用
export PORT=$SELECTED_PORT
python src/main.py --port $SELECTED_PORT