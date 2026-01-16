# 快速启动指南

使用已有的镜像快速启动服务。

## 前置条件

- Docker 已安装并运行
- 已有以下镜像：
  - `cr.utapp.cn/ops/ut-ops-backend:v1`
  - `cr.utapp.cn/ops/ut-ops-fronted:v1`

## 启动服务

### Windows

```bash
run.bat
```

### Linux / Mac

```bash
bash run.sh
```

### 或直接使用 docker-compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 验证服务

```bash
# 查看运行中的容器
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 访问应用

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 常用命令

```bash
# 查看实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend

# 删除所有数据和容器
docker-compose -f docker-compose.prod.yml down -v
```

## 配置环境变量

编辑 `.env` 文件配置：

```ini
# Dify API
DIFY_API_BASE_URL=http://your-dify-server/v1
DIFY_API_KEY=your-api-key

# SSH
SSH_DEFAULT_USERNAME=root
SSH_DEFAULT_PASSWORD=your-password

# 其他配置
DEBUG=false
```

## 故障排查

### 端口已被占用

```bash
# 查看占用端口的进程
netstat -ano | findstr :3000     # Windows
lsof -i :3000                     # Linux/Mac

# 修改端口（编辑 docker-compose.prod.yml）
# ports:
#   - "3001:80"  # 改为 3001
```

### 服务无法连接

```bash
# 检查容器网络
docker-compose -f docker-compose.prod.yml exec backend curl http://frontend:80

# 检查 DNS
docker-compose -f docker-compose.prod.yml exec backend cat /etc/resolv.conf
```

### 查看完整日志

```bash
# 导出日志到文件
docker-compose -f docker-compose.prod.yml logs > logs.txt

# 查看最后 100 行日志
docker-compose -f docker-compose.prod.yml logs --tail 100
```
