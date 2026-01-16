# NPM 安装故障排查指南

## 问题诊断

当 `npm install` 或 `npm ci` 失败时，通常由以下原因导致：

1. **网络连接问题** - 超时、DNS 失败、代理问题
2. **磁盘空间不足** - Node 包体积大
3. **NPM 缓存损坏** - 需要清理
4. **依赖版本冲突** - 需要手动处理
5. **内存不足** - 大型构建失败

---

## 快速修复方案

### 方案 1：本地调试（推荐）

在有网络的机器上先本地调试：

```bash
cd frontend

# 清理所有缓存
npm cache clean --force
rm -rf node_modules package-lock.json

# 增加日志级别重新安装
npm install --verbose

# 查看具体错误信息
npm install 2>&1 | tail -50
```

### 方案 2：修改 NPM 配置

```bash
# 增加超时时间
npm config set fetch-timeout 120000

# 增加重试次数
npm config set fetch-retries 10
npm config set fetch-retry-mintimeout 10000
npm config set fetch-retry-maxtimeout 120000

# 禁用 optional 依赖
npm config set optional false

# 重新安装
npm install --prefer-offline
```

### 方案 3：使用 `npm install` 替代 `npm ci`

在 Docker 中使用更宽松的安装模式：

```dockerfile
# ❌ 严格模式（可能失败）
RUN npm ci --silent

# ✅ 宽松模式（更容错）
RUN npm install --prefer-offline --no-audit --legacy-peer-deps
```

### 方案 4：分阶段构建

如果单次安装超时，分多次执行：

```dockerfile
RUN npm install --only=prod --prefer-offline --no-audit

RUN npm install --only=dev --prefer-offline --no-audit
```

---

## Docker 构建失败排查

### 查看详细日志

```bash
# 不使用 --silent 查看完整错误
docker-compose build --no-cache 2>&1 | grep -A 20 "ERROR\|ERR\|npm ERR"

# 或构建时添加详细输出
docker build --build-arg="BUILD_FLAGS=--verbose" .
```

### 交互式调试

```bash
# 启动一个类似的容器进行调试
docker run -it --rm node:20-alpine sh

# 在容器内测试 npm
npm install -g npm@latest
npm install react react-dom --verbose
```

### 增加构建超时

```bash
# docker-compose 中设置
docker-compose build --build-arg BUILDKIT_STEP_LOG_MAX_SIZE=10485760
```

---

## 常见错误及解决方案

### 错误 1：ERESOLVE unable to resolve dependency tree

**原因**：包版本冲突

**解决**：
```bash
npm install --legacy-peer-deps
npm install --force
```

### 错误 2：ERR! code ETIMEDOUT

**原因**：网络超时

**解决**：
```bash
npm config set fetch-timeout 120000
npm install --retry 5
```

### 错误 3：ERR! code ENOTFOUND

**原因**：DNS 解析失败或无网络

**解决**：
```bash
# 检查 DNS
nslookup registry.npmjs.org

# 修改 DNS（如果可行）
# 或使用镜像源
npm config set registry https://registry.npmmirror.com
```

### 错误 4：ENOMEM - JavaScript heap out of memory

**原因**：Node 内存不足

**解决**：
```dockerfile
# 在 Docker 中增加可用内存
docker run --memory=2g ...

# 或在 npm 脚本中设置
NODE_OPTIONS=--max-old-space-size=2048 npm run build
```

### 错误 5：missing script: build

**原因**：`package.json` 中没有 build 脚本

**解决**：
```bash
# 检查 package.json 的 scripts 部分
cat package.json | grep -A 5 '"scripts"'

# 确保有 build 脚本定义
"scripts": {
  "build": "vite build",  # ← 必须有这一行
  "dev": "vite"
}
```

---

## 优化 Docker 构建速度

### 1. 使用 .dockerignore

```
node_modules
.git
.env
dist
coverage
```

### 2. 多阶段构建缓存

```dockerfile
# 先复制 package.json（利用层缓存）
COPY package*.json ./
RUN npm install

# 再复制源代码
COPY . .
RUN npm run build
```

### 3. 使用构建缓存

```bash
docker-compose build --cache-from ops-assistant-frontend
```

### 4. 离线依赖

在有网络的机器上：
```bash
npm install
npm ci --offline
```

复制 `node_modules` 到 Docker 中：
```dockerfile
COPY node_modules ./node_modules
SKIP RUN npm install
```

---

## 生产环境最佳实践

### 优化后的 Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# 优化 npm 配置
RUN npm config set fetch-timeout 120000 && \
    npm config set fetch-retries 5

# 构建缓存层
COPY package*.json ./
RUN npm install --production --prefer-offline --no-audit

# 应用代码
COPY . .

# 构建
ENV NODE_ENV=production
RUN npm run build

# 生产镜像
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

### 预构建优化

```bash
# 在 CI/CD 中预先缓存
docker build -t ops-assistant-frontend:build-cache --target builder .
docker build --cache-from ops-assistant-frontend:build-cache -t ops-assistant-frontend .
```

---

## 测试步骤

### 验证构建

```bash
# 清理后重新构建
docker-compose build --no-cache

# 查看镜像大小
docker images | grep ops-assistant

# 测试运行
docker-compose up -d
docker-compose ps
```

### 验证应用

```bash
# 检查前端
curl http://localhost:3000

# 检查后端
curl http://localhost:8000/health

# 查看日志
docker-compose logs frontend
docker-compose logs backend
```

---

## 获取帮助

### 收集调试信息

```bash
# 导出完整构建日志
docker-compose build --no-cache 2>&1 | tee build.log

# 查看 npm 配置
docker run node:20-alpine npm config list

# 查看 npm 版本
docker run node:20-alpine npm --version
```

### 常用命令

```bash
# 清理所有 Docker 缓存
docker system prune -a

# 强制重新构建
docker-compose build --no-cache --force-rm

# 增加构建详细度
DOCKER_BUILDKIT=0 docker-compose build

# 查看镜像历史
docker history ops-assistant-frontend
```
