#!/bin/bash

# ============================================
# 智能运维助手 - Docker 构建脚本
# ============================================

set -e

echo "🔨 开始构建智能运维助手..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 参数解析
CLEAN_BUILD=${1:-false}
MIRROR_MODE=${2:-false}

if [ "$CLEAN_BUILD" = "clean" ]; then
    echo -e "${YELLOW}🧹 清理 Docker 缓存...${NC}"
    docker system prune -a --force
    docker volume prune --force
fi

# 显示当前配置
echo -e "${GREEN}📝 当前配置：${NC}"
if [ -f .env ]; then
    echo "  ✓ .env 文件已加载"
    grep -E "NPM_REGISTRY|APT_SOURCE" .env || echo "  (未设置镜像源)"
else
    echo "  ⚠️  未找到 .env 文件，使用默认配置"
fi

# 前端构建
echo -e "\n${GREEN}🏗️  构建前端镜像...${NC}"
if docker-compose build frontend 2>&1 | tee -a build.log; then
    echo -e "${GREEN}✅ 前端镜像构建成功${NC}"
else
    echo -e "${RED}❌ 前端镜像构建失败${NC}"
    echo -e "${YELLOW}📋 故障排查：${NC}"
    echo "  1. 检查网络连接"
    echo "  2. 查看文件: docs/npm-troubleshooting.md"
    echo "  3. 尝试命令: docker-compose build --no-cache frontend"
    exit 1
fi

# 后端构建
echo -e "\n${GREEN}🏗️  构建后端镜像...${NC}"
if docker-compose build backend 2>&1 | tee -a build.log; then
    echo -e "${GREEN}✅ 后端镜像构建成功${NC}"
else
    echo -e "${RED}❌ 后端镜像构建失败${NC}"
    echo -e "${YELLOW}📋 故障排查：${NC}"
    echo "  查看构建日志: docker-compose build --no-cache backend"
    exit 1
fi

# 显示镜像信息
echo -e "\n${GREEN}📊 镜像信息：${NC}"
docker images | grep ops-assistant

echo -e "\n${GREEN}✨ 构建完成！${NC}"
echo -e "${YELLOW}下一步：${NC}"
echo "  1. docker-compose up -d"
echo "  2. 访问 http://localhost:3000"
echo "  3. 查看日志: docker-compose logs -f"
