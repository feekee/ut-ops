#!/bin/bash

# ============================================
# 智能运维助手 - 快速启动脚本
# 使用已有的镜像直接启动服务
# ============================================

set -e

echo ""
echo "============================================"
echo "  智能运维助手 - 启动服务"
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

echo -e "${GREEN}启动服务中...${NC}"
echo ""

# 启动服务
if docker-compose -f docker-compose.prod.yml up -d; then
    echo ""
    
    # 等待服务启动
    echo -e "${GREEN}等待服务启动...${NC}"
    sleep 3
    
    # 显示服务状态
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "============================================"
    echo -e "${GREEN}✓ 服务已启动！${NC}"
    echo "============================================"
    echo ""
    echo "访问地址："
    echo "  • 前端: http://localhost:3000"
    echo "  • 后端: http://localhost:8000"
    echo "  • API 文档: http://localhost:8000/docs"
    echo ""
    echo "常用命令："
    echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
    echo "  重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo ""
else
    echo -e "${RED}✗ 启动失败${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi
