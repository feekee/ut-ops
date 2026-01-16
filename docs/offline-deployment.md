# 内网离线部署指南

本文档说明如何在完全离线的内网环境中部署智能运维助手。

## 📋 部署流程

### 阶段 1：有网络机器 - 镜像构建

在可访问外网的机器上：

```bash
# 1. 克隆或下载项目
git clone <repo-url>
cd ut

# 2. 配置环境（可选，使用默认配置也可以）
cp env.example .env

# 3. 构建镜像
docker-compose build --no-cache

# 4. 验证镜像已构建
docker images | grep ops-assistant
# 输出示例：
# ops-assistant-frontend   latest   abc123   2 days ago   150MB
# ops-assistant-backend    latest   def456   2 days ago   200MB
```

### 阶段 2：有网络机器 - 导出镜像

```bash
# 导出前端镜像
docker save ops-assistant-frontend:latest -o frontend.tar

# 导出后端镜像
docker save ops-assistant-backend:latest -o backend.tar

# 导出 Redis 镜像（可选，如果需要缓存）
docker save redis:7-alpine -o redis.tar

# 导出 Nginx 镜像（已包含在前端镜像中，不需要单独导出）

# 验证导出文件
ls -lh *.tar
# 输出示例：
# -rw-r--r-- 1 user group 150M xxx frontend.tar
# -rw-r--r-- 1 user group 200M xxx backend.tar
```

### 阶段 3：传输镜像到内网

使用以下任一方式传输文件：

- ✅ U 盘、移动硬盘
- ✅ 企业内网文件服务器
- ✅ FTP/SFTP 服务
- ✅ 专线传输

**推荐做法**：
```bash
# 打包所有文件便于传输
tar czf ops-assistant-deploy.tar.gz *.tar docker-compose.yml env.example

# 传输到内网机器
scp ops-assistant-deploy.tar.gz user@internal-server:/tmp/

# 在内网机器上解压
ssh user@internal-server
cd /tmp && tar xzf ops-assistant-deploy.tar.gz
```

### 阶段 4：内网机器 - 加载镜像

在内网机器上：

```bash
# 1. 进入项目目录
cd /path/to/ut

# 2. 加载前端镜像
docker load -i frontend.tar
# 输出: Loaded image: ops-assistant-frontend:latest

# 3. 加载后端镜像
docker load -i backend.tar
# 输出: Loaded image: ops-assistant-backend:latest

# 4. 验证镜像已加载
docker images | grep ops-assistant

# 5. 配置环境变量
cp env.example .env
# 编辑 .env（可选，默认配置即可）
```

### 阶段 5：内网机器 - 启动服务

```bash
# 使用启动脚本（推荐）
# Windows
start.bat

# Linux/Mac
bash start.sh

# 或直接使用 docker-compose
docker-compose up -d
```

### 阶段 6：验证服务

```bash
# 查看运行中的容器
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试前端
curl http://localhost:3000

# 测试后端
curl http://localhost:8000/health

# 测试 API 文档
curl http://localhost:8000/docs
```

---

## 📦 文件清单

### 必需文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `frontend.tar` | ~150MB | 前端镜像 |
| `backend.tar` | ~200MB | 后端镜像 |
| `docker-compose.yml` | ~10KB | 编排配置 |
| `env.example` | ~1KB | 环境变量模板 |

### 可选文件

| 文件 | 说明 |
|------|------|
| `redis.tar` | Redis 缓存镜像 |
| `start.sh` / `start.bat` | 快速启动脚本 |
| 文档文件 | 参考和故障排查 |

### 总体大小估算

```
frontend.tar       150MB
backend.tar        200MB
redis.tar           30MB (可选)
其他文件           < 5MB
────────────────────────
总计               ~385MB (含 Redis)
           或     ~355MB (不含 Redis)
```

---

## 🚀 快速参考

### 有网络机器 - 一键导出

```bash
# Windows PowerShell
$images = @('frontend', 'backend', 'redis:7-alpine')
foreach ($img in $images) {
    $tag = if ($img -match ':') { $img } else { "ops-assistant-$($img):latest" }
    docker save $tag -o "$($img.Replace(':', '-')).tar"
}

# Linux/Mac
for img in frontend backend "redis:7-alpine"; do
    tag=$([ $img = "frontend" ] && echo "ops-assistant-frontend:latest" || echo "ops-assistant-backend:latest")
    [ $img = "redis:7-alpine" ] && tag="redis:7-alpine"
    docker save $tag -o "${img//\//-}.tar"
done
```

### 内网机器 - 一键启动

**Windows:**
```batch
for %%f in (*.tar) do docker load -i %%f
docker-compose up -d
```

**Linux/Mac:**
```bash
for tar in *.tar; do docker load -i "$tar"; done
docker-compose up -d
```

---

## 🔍 故障排查

### 问题 1：docker load 失败

```bash
# 检查文件完整性
ls -lh *.tar

# 验证 tar 文件格式
tar tzf frontend.tar | head

# 手动检查镜像内容
docker inspect $(docker load -i frontend.tar | grep Loaded | cut -d: -f3) 2>/dev/null || echo "Check failed"
```

### 问题 2：容器无法启动

```bash
# 查看详细错误
docker-compose logs

# 检查依赖的镜像
docker-compose config | grep image

# 手动检查镜像是否存在
docker images ops-assistant-*
```

### 问题 3：网络连接问题

```bash
# 检查容器网络
docker-compose exec backend curl http://frontend:80

# 检查 DNS
docker-compose exec backend cat /etc/resolv.conf

# 重启网络
docker-compose down
docker-compose up -d
```

### 问题 4：磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理 Docker 镜像/容器
docker system prune -a

# 或删除特定镜像
docker rmi ops-assistant-frontend:latest
docker load -i frontend.tar
```

---

## 📊 性能优化

### 缩小镜像大小

在构建机器上：

```dockerfile
# 使用多阶段构建
FROM node:20-alpine AS builder
# ... 构建 ...
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

### 压缩传输

```bash
# 压缩镜像文件
tar czf frontend.tar.gz frontend.tar
tar czf backend.tar.gz backend.tar

# 传输压缩后的文件
# 传输后解压
tar xzf frontend.tar.gz
```

---

## 🔐 安全建议

### 镜像验证

```bash
# 计算镜像哈希
sha256sum *.tar

# 在另一台机器上验证
# 确保文件在传输中未被篡改
```

### 隔离部署

```bash
# 使用特定的网络
docker network create ops-network

# 运行容器时指定网络
docker run --network ops-network ...
```

### 备份镜像

```bash
# 在内网机器上定期备份
docker save ops-assistant-frontend:latest -o /backup/frontend-backup.tar
docker save ops-assistant-backend:latest -o /backup/backend-backup.tar
```

---

## 📝 完整流程检查清单

### 构建机器

- [ ] Docker 已安装且运行正常
- [ ] 项目代码完整
- [ ] `docker-compose build` 成功
- [ ] `docker images` 显示 ops-assistant-* 镜像
- [ ] 镜像已导出为 .tar 文件
- [ ] .tar 文件完整性验证（checksum）
- [ ] 所有文件已打包并准备传输

### 传输过程

- [ ] 所有必需文件已准备
- [ ] 使用安全的传输方式
- [ ] 文件校验和已记录
- [ ] 传输完成后验证文件完整性

### 部署机器

- [ ] Docker 已安装且运行正常
- [ ] 项目目录已创建
- [ ] 所有文件已复制到项目目录
- [ ] `docker load -i *.tar` 成功
- [ ] `docker images` 显示所有镜像
- [ ] `.env` 已配置
- [ ] `docker-compose up -d` 成功
- [ ] 容器正在运行（`docker-compose ps`）
- [ ] 前端可访问（http://localhost:3000）
- [ ] 后端可访问（http://localhost:8000/health）

---

## 📞 获取支持

如遇到问题，请参考：

- `docs/npm-troubleshooting.md` - NPM 问题
- `docs/intranet-deployment.md` - 内网部署
- `docs/api.md` - API 文档
- `docs/dify-config.md` - Dify 配置

---

## ✨ 高级话题

### 使用私有镜像仓库

如果有内网镜像仓库（如 Harbor、Nexus），可以：

```bash
# 在构建机器上标记镜像
docker tag ops-assistant-frontend:latest harbor.internal/ops/frontend:latest
docker tag ops-assistant-backend:latest harbor.internal/ops/backend:latest

# 推送到私有仓库
docker push harbor.internal/ops/frontend:latest
docker push harbor.internal/ops/backend:latest

# 在部署机器上直接拉取
docker pull harbor.internal/ops/frontend:latest
docker pull harbor.internal/ops/backend:latest
```

### 集群部署

如果需要在 Kubernetes 集群中部署，参考 Helm Chart（待提供）。

