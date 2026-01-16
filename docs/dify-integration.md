# Dify 集成指南

本文档说明如何正确集成 Dify API 以及常见问题的解决方案。

## 📋 Dify API 基本概念

### API 端点
```
Base URL: https://your-dify-server/v1

主要端点:
- POST /chat-messages          # 发送消息
- GET /messages                # 获取消息历史
- GET /conversations           # 获取对话列表
- DELETE /conversations/{id}   # 删除对话
```

### 认证方式
```bash
# Header 中添加 API Key
Authorization: Bearer your-api-key-here
```

### 数据格式

#### conversation_id（对话 ID）
- **格式**: UUID v4
- **示例**: `550e8400-e29b-41d4-a716-446655440000`
- **生成方式**: 客户端生成
- **用途**: 维持多轮对话的上下文

#### 请求体示例
```json
{
  "inputs": {},
  "query": "用户问题",
  "response_mode": "blocking",
  "user": "user-id",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 响应示例
```json
{
  "answer": "AI 的回答",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "msg-xxx",
  "metadata": {...}
}
```

---

## ⚙️ 配置步骤

### 1. 获取 API Key

在 Dify 控制台：
1. 进入应用设置
2. 点击 「API Access」或「开发」
3. 创建 API Key
4. 复制 API Key 到 `.env` 文件

```ini
# .env
DIFY_API_BASE_URL=https://your-dify-server/v1
DIFY_API_KEY=app-xxxxxxxxxxxxxx
```

### 2. 创建 Agent 应用

在 Dify 中：
1. 创建新应用 → 选择 「Agent」
2. 配置系统提示词
3. 添加工具（如 SSH 工具）
4. 配置知识库
5. 发布应用

### 3. 验证 API 连接

```bash
# 测试 API 连接
curl -X POST "https://your-dify-server/v1/chat-messages" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {},
    "query": "hello",
    "response_mode": "blocking",
    "user": "test-user"
  }'

# 正常响应应该包含:
# {"answer": "...", "conversation_id": "...", "message_id": "..."}
```

---

## 🐛 常见错误和解决方案

### 错误 1: Conversation ID 不是有效的 UUID

**错误信息**:
```
{"errors":{"conversation_id":"Existing conversation ID xxx is not a valid uuid."}}
```

**原因**: Conversation ID 格式不符合 UUID 标准

**解决方案**:

在前端生成 UUID v4 格式的 ID：

```typescript
// ❌ 错误方式
const generateId = () => Math.random().toString(36).substring(2, 15)
// 生成: b3cs367b9li (无效)

// ✅ 正确方式
const generateId = (): string => {
  const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
  return uuid
}
// 生成: 550e8400-e29b-41d4-a716-446655440000 (有效)
```

### 错误 2: 无效的 API Key

**错误信息**:
```
{"message":"Unauthorized", "code": "invalid_api_key"}
```

**原因**: API Key 不正确或已过期

**解决方案**:
```bash
# 1. 检查 API Key 是否正确
docker-compose -f docker-compose.prod.yml exec backend env | grep DIFY_API_KEY

# 2. 在 Dify 控制台重新生成 API Key
# - Settings → API Access
# - Delete old key → Create new key
# - 更新 .env 文件

# 3. 重启服务
docker-compose -f docker-compose.prod.yml restart backend
```

### 错误 3: 不支持的 response_mode

**错误信息**:
```
{"message":"response_mode must be one of..."}
```

**原因**: response_mode 值不支持

**解决方案**:
```python
# 支持的值:
# - "blocking"      # 等待完整响应
# - "streaming"     # 流式响应（SSE）

# 检查当前设置
curl http://your-backend:8000/api/chat/send -H "Content-Type: application/json" \
  -d '{"message":"test", "response_mode":"blocking"}'
```

### 错误 4: 字段验证失败

**错误信息**:
```
{"message":"Input payload validation failed", "errors":{...}}
```

**原因**: 请求数据格式不符合 Dify 要求

**解决方案**:

检查请求格式：
```json
{
  "inputs": {},              // ✅ 必须是对象，不能是字符串
  "query": "用户问题",        // ✅ 必须是字符串
  "response_mode": "blocking", // ✅ 只能是 blocking 或 streaming
  "user": "user-id",         // ✅ 必须是字符串
  "conversation_id": "uuid"  // ✅ 可选，但必须是有效的 UUID
}
```

### 错误 5: 超时错误

**错误信息**:
```
Timeout waiting for response
```

**原因**: 请求超时

**解决方案**:
```bash
# 1. 增加超时时间
# backend/app/config.py
DIFY_TIMEOUT=120  # 增加到 120 秒

# 2. 检查网络连接
docker-compose -f docker-compose.prod.yml exec backend \
  curl -v https://your-dify-server/v1/ping

# 3. 检查 Dify 服务状态
# 访问 Dify 控制台确认服务是否在线
```

---

## 🔄 对话流程详解

### 创建新对话

```
1. 前端生成 UUID (conversation_id)
   ↓
2. 用户输入第一条消息
   ↓
3. 前端 POST /api/chat/send
   {
     "message": "用户问题",
     "conversation_id": "新生成的UUID",
     "user_id": "current-user"
   }
   ↓
4. 后端转发到 Dify
   ↓
5. Dify 创建新对话并返回响应
   ↓
6. 前端显示回复，保存 conversation_id
```

### 继续对话

```
1. 用户输入新消息
   ↓
2. 前端 POST /api/chat/send
   {
     "message": "新问题",
     "conversation_id": "保存的UUID",  // ← 使用之前的 ID
     "user_id": "current-user"
   }
   ↓
3. Dify 在现有对话中添加消息
   ↓
4. AI 基于对话历史生成回复
```

### 获取对话历史

```bash
# 获取特定对话的所有消息
GET /api/chat/conversations/{conversation_id}/messages?user_id=user-id

# 响应包含:
{
  "data": [
    {"id": "msg-1", "role": "user", "content": "问题1", "created_at": "..."},
    {"id": "msg-2", "role": "assistant", "content": "回答1", "created_at": "..."}
  ]
}
```

---

## 📝 最佳实践

### 1. 错误处理

```python
# backend/app/api/chat.py

try:
    response = await client.post(
        f"{settings.DIFY_API_BASE_URL}/chat-messages",
        headers={"Authorization": f"Bearer {settings.DIFY_API_KEY}"},
        json=payload,
        timeout=120.0,
    )
    
    if response.status_code == 400:
        error_data = response.json()
        if "conversation_id" in str(error_data):
            # conversation_id 格式错误
            raise ValueError(f"Invalid conversation ID format")
    elif response.status_code == 401:
        # API Key 无效
        raise ValueError("Invalid API Key")
    elif response.status_code != 200:
        raise ValueError(f"Dify API error: {response.text}")
        
except Exception as e:
    logger.error(f"Failed to call Dify API: {e}")
    raise
```

### 2. 日志记录

```python
# 记录所有 Dify 请求用于调试
logger.info(f"Calling Dify API with conversation_id={conversation_id}")
logger.debug(f"Request payload: {payload}")
logger.info(f"Response status: {response.status_code}")
```

### 3. 缓存策略

```python
# 缓存对话列表避免频繁查询
from functools import lru_cache

@lru_cache(maxsize=100)
def get_conversation(conversation_id: str):
    # 获取对话详情
    ...
```

---

## 🧪 测试清单

### 功能测试

- [ ] 创建新对话
- [ ] 在同一对话中发送多条消息
- [ ] 获取对话历史
- [ ] 删除对话
- [ ] 处理错误响应

### 集成测试

```bash
# 1. 测试 API 连接
curl -H "Authorization: Bearer $DIFY_API_KEY" \
  https://your-dify-server/v1/ping

# 2. 测试消息发送
curl -X POST "https://your-dify-server/v1/chat-messages" \
  -H "Authorization: Bearer $DIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {},
    "query": "你好",
    "response_mode": "blocking",
    "user": "test"
  }'

# 3. 完整流程测试
bash tests/integration_test.sh
```

---

## 📚 参考资源

- [Dify 官方 API 文档](https://docs.dify.ai/api)
- [Dify Agent 配置指南](https://docs.dify.ai/advanced-features/agent-mode)
- [UUID 格式规范](https://en.wikipedia.org/wiki/Universally_unique_identifier)

