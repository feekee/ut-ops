# 故障排查指南

## 后端无法启动 - CORS_ORIGINS 错误

### 错误信息
```
pydantic_settings.sources.SettingsError: error parsing value for field "CORS_ORIGINS"
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

### 原因
CORS 配置格式错误。之前版本期望 JSON 格式，现在已改为简单的逗号分隔格式。

### 解决方案

#### 修改 docker-compose.prod.yml

将：
```yaml
- CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

改为：
```yaml
- CORS_ORIGINS_STR=http://localhost:3000,http://127.0.0.1:3000
```

#### 修改 .env 文件

```ini
# ❌ 错误格式
CORS_ORIGINS=["http://localhost:3000"]

# ✅ 正确格式
CORS_ORIGINS_STR=http://localhost:3000,http://127.0.0.1:3000
```

#### 快速修复命令

```bash
# 停止运行中的容器
docker-compose -f docker-compose.prod.yml down

# 使用最新的配置文件重新启动
docker-compose -f docker-compose.prod.yml up -d
```

---

## 常见错误及解决方案

### 1. 前端无法连接后端

**症状**: 前端报告连接错误或 CORS 错误

**检查步骤**:
```bash
# 1. 验证后端是否运行
docker-compose -f docker-compose.prod.yml ps

# 2. 查看后端日志
docker-compose -f docker-compose.prod.yml logs backend

# 3. 测试连接
curl http://localhost:8000/health

# 4. 检查 CORS 配置是否包含前端 URL
docker-compose -f docker-compose.prod.yml exec backend curl -H "Origin: http://localhost:3000" http://localhost:8000/health -v
```

### 2. 后端无法连接 Dify

**症状**: 发送消息时提示连接失败

**检查步骤**:
```bash
# 1. 验证 Dify API Key 是否正确
docker-compose -f docker-compose.prod.yml logs backend | grep DIFY

# 2. 测试 Dify 连接
docker-compose -f docker-compose.prod.yml exec backend curl -H "Authorization: Bearer YOUR_API_KEY" http://your-dify-server/v1/ping

# 3. 确认环境变量正确
docker-compose -f docker-compose.prod.yml exec backend env | grep DIFY
```

### 3. SSH 命令执行失败

**症状**: SSH 工具返回连接错误

**检查步骤**:
```bash
# 1. 验证 SSH 配置
docker-compose -f docker-compose.prod.yml exec backend env | grep SSH

# 2. 检查 SSH 连接
docker-compose -f docker-compose.prod.yml exec backend ssh -v root@192.168.1.100

# 3. 查看完整错误
docker-compose -f docker-compose.prod.yml logs backend | tail -50
```

### 4. 容器无法启动

**症状**: `docker ps` 显示容器不在运行

**检查步骤**:
```bash
# 1. 查看启动错误
docker-compose -f docker-compose.prod.yml logs

# 2. 验证镜像是否存在
docker images | grep ops-assistant

# 3. 检查磁盘空间
docker system df

# 4. 强制重建
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 调试技巧

### 查看实时日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# 查看最后 N 行日志
docker-compose -f docker-compose.prod.yml logs --tail 100
```

### 进入容器调试

```bash
# 进入后端容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.prod.yml exec frontend sh

# 检查网络连接
docker-compose -f docker-compose.prod.yml exec backend ping frontend
docker-compose -f docker-compose.prod.yml exec backend curl http://frontend:80
```

### 查看配置信息

```bash
# 查看后端环境变量
docker-compose -f docker-compose.prod.yml exec backend env | sort

# 查看特定配置
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.config import settings; print(settings)"
```

---

## 性能问题

### 服务响应慢

```bash
# 1. 检查容器资源使用
docker stats

# 2. 查看日志中的性能指标
docker-compose -f docker-compose.prod.yml logs backend | grep -i "duration\|error"

# 3. 增加容器资源（编辑 docker-compose.prod.yml）
# deploy:
#   resources:
#     limits:
#       cpus: '2'
#       memory: 2G
```

### 内存不足

```bash
# 1. 查看容器内存使用
docker stats ops-assistant-backend

# 2. 清理 Docker 系统
docker system prune -a

# 3. 增加 Docker 内存分配
# Docker Desktop 设置 → Resources → 增加内存
```

---

## 完全重置

如果遇到无法解决的问题，可以完全重置：

```bash
# 1. 停止所有容器
docker-compose -f docker-compose.prod.yml down -v

# 2. 删除所有数据
docker volume rm ops-assistant-backend-data ops-assistant-backend-logs ops-assistant-redis-data

# 3. 删除容器
docker container prune -f

# 4. 重新启动
docker-compose -f docker-compose.prod.yml up -d
```

---

## 获取帮助

遇到问题时收集以下信息：

```bash
# 生成诊断信息
echo "=== Docker Info ===" > diagnosis.txt
docker --version >> diagnosis.txt
docker-compose --version >> diagnosis.txt

echo "=== Running Containers ===" >> diagnosis.txt
docker ps -a >> diagnosis.txt

echo "=== Images ===" >> diagnosis.txt
docker images | grep ops >> diagnosis.txt

echo "=== Logs ===" >> diagnosis.txt
docker-compose -f docker-compose.prod.yml logs >> diagnosis.txt

echo "=== Environment ===" >> diagnosis.txt
docker-compose -f docker-compose.prod.yml exec backend env >> diagnosis.txt

# 查看诊断文件
cat diagnosis.txt
```
