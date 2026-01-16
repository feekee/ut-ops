# 内网环境部署指南

本文档说明如何在内网（无法访问外网）环境中部署智能运维助手。

## 🔧 解决方案

### 问题

内网机器无法访问公网源，导致 `apt-get` 和 `npm` 安装依赖失败。

### 方案

1. **配置 APT 源**（后端 Python 依赖）
2. **配置 NPM 源**（前端 Node.js 依赖）
3. **离线构建**（完全离线环境）

---

## 方案 1：使用国内镜像源（推荐）

### 适用场景

- 内网机器可访问特定的国内镜像服务器
- 或内网有本地的镜像源

### 步骤

1. **编辑 .env 文件**

```bash
cd D:\work\ut
copy env.example .env
notepad .env
```

2. **添加镜像源配置**

#### 方案 A：使用阿里云镜像源

```ini
# ============================================
# 内网镜像源配置
# ============================================

# APT 镜像源（Debian/Ubuntu）
# 选一个可用的源：
# - 阿里云：http://mirrors.aliyun.com/
# - 清华大学：https://mirrors.tsinghua.edu.cn/
# - 中科大：https://mirrors.ustc.edu.cn/
# - 华为云：https://mirrors.huaweicloud.com/

APT_SOURCE=deb http://mirrors.aliyun.com/debian/ bookworm main non-free contrib\ndeb-src http://mirrors.aliyun.com/debian/ bookworm main non-free contrib\ndeb http://mirrors.aliyun.com/debian-security bookworm-security main non-free contrib\ndeb-src http://mirrors.aliyun.com/debian-security bookworm-security main non-free contrib

# NPM 镜像源
# 选一个可用的源：
# - 阿里云：https://registry.npmmirror.com
# - 腾讯云：https://mirrors.tencent.com/npm/
# - 官方：https://registry.npmjs.org/

NPM_REGISTRY=https://registry.npmmirror.com
```

#### 方案 B：使用本地镜像服务器

如果公司有本地镜像服务器（如 Nexus、Artifactory 等）：

```ini
# 本地 APT 源
APT_SOURCE=deb http://internal-mirror.company.com/debian/ bookworm main\ndeb http://internal-mirror.company.com/debian-security bookworm-security main

# 本地 NPM 源
NPM_REGISTRY=http://npm-mirror.company.com:8081/repository/npm/
```

3. **构建镜像**

```bash
docker-compose build --no-cache
```

### 调试日志

如果构建失败，查看详细日志：

```bash
docker-compose build --no-cache --verbose
```

---

## 方案 2：完全离线构建

### 适用场景

- 构建机器无网络连接
- 需要完全隔离的部署

### 步骤

#### 1. 在有网络的机器上准备

```bash
# 导出 Node 依赖缓存
cd frontend
npm install
npm ci --prefer-offline --no-audit

# 导出 Python 依赖
cd ../backend
pip download -r requirements.txt -d ./wheels
```

#### 2. 复制到离线机器

```bash
# 复制以下文件到内网机器
- frontend/node_modules/
- backend/wheels/
```

#### 3. 修改 Dockerfile

**frontend/Dockerfile：**

```dockerfile
ARG NPM_OFFLINE=0
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

# 离线模式：使用本地 node_modules
RUN if [ "$NPM_OFFLINE" = "1" ]; then \
    cp -r ../node_modules . 2>/dev/null || npm ci --offline; \
    else \
    npm ci --silent; \
    fi

COPY . .
RUN npm run build

# ... 后续同上
```

**backend/Dockerfile：**

```dockerfile
ARG PIP_OFFLINE=0
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# 离线模式：从本地 wheels 安装
RUN if [ "$PIP_OFFLINE" = "1" ]; then \
    pip install --no-index --find-links ./wheels -r requirements.txt; \
    else \
    pip install --no-cache-dir -r requirements.txt; \
    fi

COPY . .

# ... 后续同上
```

#### 4. 构建

```bash
docker-compose build --build-arg PIP_OFFLINE=1 --build-arg NPM_OFFLINE=1
```

---

## 方案 3：预构建镜像

### 适用场景

- 多台内网机器需要部署
- 不想每次都构建

### 步骤

#### 1. 在有网络的机器构建

```bash
docker-compose build --no-cache
```

#### 2. 保存镜像

```bash
# 导出镜像
docker save ops-assistant-frontend:latest -o frontend.tar
docker save ops-assistant-backend:latest -o backend.tar
docker save redis:7-alpine -o redis.tar
docker save nginx:alpine -o nginx.tar
```

#### 3. 在内网机器加载

```bash
docker load -i frontend.tar
docker load -i backend.tar
docker load -i redis.tar
docker load -i nginx.tar

# 启动
docker-compose up -d
```

---

## 常见问题排查

### 问题 1：apt-get update 失败

```bash
# 查看当前源
docker exec ops-assistant-backend cat /etc/apt/sources.list

# 重新指定源并重建
docker-compose build --no-cache --build-arg APT_SOURCE="..."
```

### 问题 2：npm install 失败

```bash
# 查看当前 npm 配置
docker exec ops-assistant-frontend npm config get registry

# 设置新源
docker-compose build --no-cache --build-arg NPM_REGISTRY="..."
```

### 问题 3：某个依赖包不可用

**Python：**

```bash
# 查找替代包
pip search package-name  # 仅在有网络环境

# 或在 requirements.txt 中指定其他版本或替代包
```

**Node.js：**

```bash
# 查看 package-lock.json 中的版本并尝试更新
npm update
```

---

## 镜像源列表

### APT 源（Debian/Ubuntu）

| 名称 | 地址 | 适用 |
|------|------|------|
| 阿里云 | http://mirrors.aliyun.com/debian/ | bookworm |
| 清华大学 | https://mirrors.tsinghua.edu.cn/debian/ | 主流版本 |
| 中科大 | https://mirrors.ustc.edu.cn/debian/ | 主流版本 |
| 华为云 | https://mirrors.huaweicloud.com/debian/ | bookworm |
| 腾讯云 | http://mirrors.tencentyun.com/debian/ | bookworm |

### NPM 源

| 名称 | 地址 |
|------|------|
| 阿里云 | https://registry.npmmirror.com |
| 腾讯云 | https://mirrors.tencent.com/npm/ |
| 淘宝 | https://registry.npmmirror.com |
| 华为云 | https://repo.huaweicloud.com/repository/npm/ |

---

## 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试前端
curl http://localhost:3000

# 测试后端
curl http://localhost:8000/health
```

---

## 进阶：使用本地镜像服务器

如果公司有 Nexus、Artifactory 或其他镜像服务，可配置为：

```bash
# Nexus
NPM_REGISTRY=http://nexus.company.com:8081/repository/npm-proxy/
APT_SOURCE=deb http://nexus.company.com:8081/repository/debian-proxy/ bookworm main

# Artifactory
NPM_REGISTRY=https://artifactory.company.com/artifactory/api/npm/npm-remote/
```

具体配置请咨询公司 DevOps 团队。
