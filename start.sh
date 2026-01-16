#!/bin/bash

# ============================================
# 智能运维助手 - 启动脚本 (Linux/Mac)
# 仅启动预构建的镜像，不进行构建
# ============================================

set -e

echo ""
echo "============================================"
echo "  智能运维助手 - 启动工具"
echo "============================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 Docker
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker 未运行或未安装${NC}"
    echo "请先启动 Docker daemon"
    exit 1
fi

# 检查 .env 文件
if [ -f .env ]; then
    echo -e "${GREEN}✓ 已加载 .env 配置文件${NC}"
else
    echo -e "${YELLOW}! 未找到 .env 文件${NC}"
    echo "建议: cp env.example .env"
    echo ""
fi

# 检查镜像
echo -e "${GREEN}检查镜像...${NC}"

if ! docker images | grep -q "ops-assistant-frontend"; then
    echo -e "${RED}✗ 前端镜像不存在${NC}"
    echo "请先运行: docker load -i frontend.tar"
    exit 1
fi
echo -e "${GREEN}✓ 前端镜像已加载${NC}"

if ! docker images | grep -q "ops-assistant-backend"; then
    echo -e "${RED}✗ 后端镜像不存在${NC}"
    echo "请先运行: docker load -i backend.tar"
    exit 1
fi
echo -e "${GREEN}✓ 后端镜像已加载${NC}"

# 启动服务
echo ""
echo -e "${GREEN}启动服务...${NC}"

if docker-compose up -d; then
    echo ""
    echo "============================================"
    echo -e "${GREEN}✓ 启动成功！${NC}"
    echo "============================================"
    echo ""
    echo "服务地址："
    echo "  • 前端: http://localhost:3000"
    echo "  • 后端: http://localhost:8000"
    echo "  • API 文档: http://localhost:8000/docs"
    echo ""
    echo "查看日志："
    echo "  docker-compose logs -f"
    echo ""
    echo "停止服务："
    echo "  docker-compose down"
    echo ""
else
    echo -e "${RED}✗ 启动失败${NC}"
    docker-compose logs
    exit 1
fi
