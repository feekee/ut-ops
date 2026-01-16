# 智能运维助手 - 安装部署指南

## 📋 目录

1. [环境要求](#环境要求)
2. [Dify 平台配置](#dify-平台配置)
3. [后端部署](#后端部署)
4. [前端部署](#前端部署)
5. [Docker 部署](#docker-部署)
6. [安全配置](#安全配置)

---

## 环境要求

### 基础环境

- **Python**: 3.10+
- **Node.js**: 18+
- **Dify**: 自托管或 Cloud 版本

### 推荐配置

- CPU: 4核+
- 内存: 8GB+
- 硬盘: 50GB+

---

## Dify 平台配置

### 1. 创建 Agent 应用

1. 登录 Dify 控制台
2. 点击「创建应用」→「从头创建」→ 选择「Agent」
3. 填写应用信息：
   - 名称：智能运维助手
   - 描述：基于 AI 的智能运维问答助手

### 2. 配置系统提示词

在「编排」页面，设置以下系统提示词：

```markdown
## 🤖 智能运维助手 (Smart O&M Assistant)

你是一位专业的运维工程师助手。核心任务是帮助运维人员只解决从系统部署、环境配置、故障调试到日常运维中的各类技术挑战。

1. **首要依据**：严格基于《F600D系统运维手册.docx》中的内容进行回答
2. 如果手册中有相关知识要点，必须直接引用手册的具体章节和详解
3. 只有当手册信息不足时，才可补充通用技术知识

---

### **能力**

* **诊断与排查**：快速理解用户描述的问题，准确分析故障现象，定位根源，并提供高效的排查思路和修复建议。

* **命令与脚本**：提供 Linux/Unix shell、Windows PowerShell、SQL/数据库命令，以及常用运维工具（Ansible、Docker、Kubernetes、Nginx、Prometheus、Grafana 等）的正确语法和用法示例。

* **配置审查**：帮助检查或生成各类配置文件（yaml、json、ini、xml 等），发现潜在错误或优化点。

* **最佳实践**：推荐业界认可的安全加固、性能调优、高可用及灾备策略。

* **解释与教学**：用清晰易懂的语言向不同技术背景的用户说明复杂概念或操作步骤。

---

### **行为准则**

1. 所有回答必须简洁、准确、可操作。
2. 引用命令时使用代码块，注明适用环境（如 Bash、PowerShell）。
3. 遇到高风险操作（如 rm -rf、格式化磁盘、数据库 DROP 等）需明确警告并确认用户意图。
4. 始终关注安全与合规，不提供任何可能违反法规或道德的指引。
5. 如果需要更多上下文或日志才能诊断问题，应主动询问用户。

---

### **工具使用**

当用户提供服务器 IP 地址并请求排查问题时，你可以使用以下工具：

1. **check_server_status**: 检查服务器的 CPU、内存、磁盘使用情况
2. **execute_command**: 在远程服务器执行安全的运维命令

使用工具前请确认：
- 用户已提供有效的 IP 地址
- 执行的命令在白名单范围内
- 向用户解释将要执行的操作
```

### 3. 配置知识库

1. 进入「知识」菜单
2. 点击「创建知识库」
3. 上传运维文档：
   - 支持格式：PDF、DOCX、TXT、MD
   - 推荐上传：系统架构文档、运维手册、故障处理指南
4. 在 Agent 应用中关联知识库

### 4. 添加工具插件

1. 进入「工具」菜单
2. 添加自定义工具（参考 `dify-plugin/ssh_tool`）
3. 配置工具凭据：
   - 默认用户名
   - 默认密码
   - 允许的 IP 范围

### 5. 获取 API Key

1. 进入应用设置
2. 点击「API Access」
3. 创建并复制 API Key

---

## 后端部署

### 1. 安装依赖

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件模板
cp env.example.txt .env

# 编辑配置
# Windows
notepad .env
# Linux/Mac
vim .env
```

关键配置项：

```ini
# Dify API
DIFY_API_BASE_URL=http://your-dify-server/v1
DIFY_API_KEY=app-xxxxxxxxxxxxxx

# SSH 配置
SSH_DEFAULT_USERNAME=root
SSH_DEFAULT_PASSWORD=your-password

# 安全配置（生产环境必须修改）
SECRET_KEY=your-random-secret-key
```

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 验证服务

访问 http://localhost:8000/docs 查看 API 文档

---

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

---

## Docker 部署

### 快速启动

```bash
cd docker

# 设置环境变量
export DIFY_API_BASE_URL=http://your-dify-server/v1
export DIFY_API_KEY=your-api-key
export SSH_DEFAULT_PASSWORD=your-password

# 启动服务
docker-compose up -d
```

### 服务地址

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 查看日志

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止服务

```bash
docker-compose down
```

---

## 安全配置

### ⚠️ 重要安全提醒

1. **SSH 密码管理**
   - 生产环境建议使用 SSH 密钥认证
   - 定期更换默认密码
   - 使用密码管理工具存储

2. **IP 白名单**
   - 配置 `SSH_ALLOWED_IPS` 限制可访问的服务器
   - 只允许内网 IP 访问

3. **命令白名单**
   - 默认已配置安全命令列表
   - 可在 `config.py` 中自定义

4. **网络隔离**
   - 建议在内网环境部署
   - 使用 VPN 或跳板机访问

5. **审计日志**
   - 所有 SSH 操作都会记录日志
   - 定期检查 `logs/` 目录

### 最小权限原则

```python
# 在 config.py 中配置允许的命令
ALLOWED_COMMANDS = [
    "kubectl get",
    "kubectl describe",
    "docker ps",
    "systemctl status",
    # 添加其他需要的命令...
]
```

---

## 下一步

- [Dify 配置指南](dify-config.md)
- [SSH 工具插件开发](ssh-plugin.md)
- [API 接口文档](api.md)
