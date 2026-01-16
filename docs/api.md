# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`

---

## 对话接口

### 发送消息（非流式）

**POST** `/chat/send`

发送消息并等待完整响应。

**请求体：**
```json
{
  "message": "请帮我检查服务器状态",
  "conversation_id": "conv-xxx",  // 可选，首次对话不需要
  "user_id": "user-123"
}
```

**响应：**
```json
{
  "answer": "好的，我来帮您检查服务器状态...",
  "conversation_id": "conv-xxx",
  "message_id": "msg-xxx",
  "metadata": {}
}
```

### 发送消息（流式）

**POST** `/chat/stream`

发送消息并获取流式响应（SSE）。

**请求体：** 同上

**响应：** Server-Sent Events 格式
```
data: {"event": "message", "answer": "好的"}
data: {"event": "message", "answer": "好的，我来"}
data: {"event": "message_end", "conversation_id": "conv-xxx"}
```

### 获取对话历史

**GET** `/chat/conversations/{conversation_id}/messages`

**参数：**
- `conversation_id`: 对话 ID
- `user_id`: 用户 ID
- `limit`: 返回消息数量（默认 20）

**响应：**
```json
{
  "data": [
    {
      "id": "msg-xxx",
      "role": "user",
      "content": "...",
      "created_at": "2026-01-16T10:00:00Z"
    }
  ]
}
```

### 删除对话

**DELETE** `/chat/conversations/{conversation_id}`

---

## SSH 操作接口

### 测试 SSH 连接

**POST** `/ssh/test-connection`

测试是否能成功 SSH 连接到服务器。

**请求体：**
```json
{
  "host": "192.168.1.100",
  "port": 22,
  "username": "root",
  "password": "xxx"  // 可选，不提供则使用默认密码
}
```

**响应：**
```json
{
  "success": true,
  "message": "连接成功",
  "host": "192.168.1.100",
  "latency_ms": 50.5
}
```

### 执行 SSH 命令

**POST** `/ssh/execute`

在远程服务器执行命令。

**请求体：**
```json
{
  "host": "192.168.1.100",
  "command": "kubectl get pods",
  "port": 22,
  "username": "root",
  "password": "xxx",
  "timeout": 30
}
```

**响应：**
```json
{
  "success": true,
  "command": "kubectl get pods",
  "stdout": "NAME                     READY   STATUS...",
  "stderr": "",
  "exit_code": 0,
  "execution_time_ms": 150.2,
  "timestamp": "2026-01-16T10:00:00Z"
}
```

**允许的命令前缀：**
- kubectl get/describe/logs/top
- docker ps/logs/inspect/stats
- systemctl status
- df -h, free -m, top, ps aux
- netstat -tlnp, ss -tlnp
- ping, curl
- cat /var/log, tail, journalctl

### 获取服务器状态

**POST** `/ssh/server-status`

获取服务器系统资源使用情况。

**请求体：**
```json
{
  "host": "192.168.1.100",
  "port": 22
}
```

**响应：**
```json
{
  "host": "192.168.1.100",
  "online": true,
  "cpu_usage": "25.5",
  "memory_usage": "68.2%",
  "disk_usage": "45%",
  "load_average": "0.85, 0.90, 0.78",
  "uptime": "up 15 days, 3 hours"
}
```

### 服务诊断

**POST** `/ssh/diagnose`

对指定服务进行诊断检查。

**参数：**
- `host`: 服务器 IP
- `service_name`: 服务名称
- `port`: SSH 端口（默认 22）
- `username`: 用户名
- `password`: 密码

**响应：**
```json
{
  "host": "192.168.1.100",
  "service": "nginx",
  "timestamp": "2026-01-16T10:00:00Z",
  "diagnostics": {
    "service_status": {
      "success": true,
      "output": "● nginx.service - A high performance web server..."
    },
    "recent_logs": {
      "success": true,
      "output": "Jan 16 10:00:00 server nginx[1234]: ..."
    },
    "process_check": {
      "success": true,
      "output": "root  1234  0.0  0.2  nginx: master process"
    }
  }
}
```

### 获取允许的命令列表

**GET** `/ssh/allowed-commands`

**响应：**
```json
{
  "commands": [
    "kubectl get",
    "kubectl describe",
    "docker ps",
    "..."
  ],
  "note": "仅允许以这些前缀开头的命令"
}
```

---

## 知识库接口

### 获取知识库列表

**GET** `/knowledge/datasets`

### 获取文档列表

**GET** `/knowledge/datasets/{dataset_id}/documents`

**参数：**
- `page`: 页码（默认 1）
- `limit`: 每页数量（默认 20）

### 上传文档

**POST** `/knowledge/datasets/{dataset_id}/documents/upload`

**请求：** multipart/form-data
- `file`: 文件
- `indexing_technique`: 索引方式（high_quality / economy）

### 删除文档

**DELETE** `/knowledge/datasets/{dataset_id}/documents/{document_id}`

### 知识库检索

**POST** `/knowledge/datasets/{dataset_id}/retrieve`

**请求体：**
```json
{
  "query": "如何重启服务",
  "top_k": 5
}
```

---

## 健康检查

### 健康检查

**GET** `/health`

```json
{
  "status": "healthy",
  "timestamp": "2026-01-16T10:00:00Z"
}
```

### 就绪检查

**GET** `/ready`

```json
{
  "status": "ready",
  "timestamp": "2026-01-16T10:00:00Z"
}
```

---

## 错误响应

所有接口在发生错误时返回统一格式：

```json
{
  "detail": "错误信息描述"
}
```

**HTTP 状态码：**
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器内部错误
- `503` - 服务不可用
- `504` - 请求超时
