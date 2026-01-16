# ============================================
# 智能运维助手 - 前端 Dockerfile
# ============================================

ARG NPM_REGISTRY=""
ARG MIRROR_HOST=""

# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 设置 npm 超时和重试
RUN npm config set fetch-timeout 60000 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-retries 5

# 如果指定了 NPM 源，则使用自定义源（用于内网环境）
RUN if [ -n "$NPM_REGISTRY" ]; then \
    npm config set registry $NPM_REGISTRY; \
    fi

# 复制依赖文件
COPY package*.json ./

# 安装依赖 - 使用 npm install 替代 npm ci 以获得更好的容错性
RUN npm install --prefer-offline --no-audit --legacy-peer-deps 2>&1 || \
    (echo "First install failed, retrying..." && npm cache clean --force && npm install --prefer-offline --no-audit --legacy-peer-deps)

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build 2>&1 || \
    (echo "Build failed, checking typescript..." && npx tsc --noEmit && npm run build)

# ============================================
# 生产阶段
# ============================================
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
