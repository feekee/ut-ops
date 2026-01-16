# 🤖 智能运维助手 (Smart O&M Assistant)

基于 Dify 平台的智能运维助手，提供 ChatGPT 风格的对话界面，支持文档知识库、SSH 远程排查等功能。

## ✨ 功能特性

- 🗣️ **ChatGPT 风格对话界面** - 流畅的多轮对话体验
- 📚 **运维文档知识库** - 支持上传运维文档，自动解析系统架构
- 🔧 **远程环境排查** - SSH 连接服务器，执行 kubectl/docker/Linux 命令
- 💡 **通用运维问答** - 基于大模型知识回答技术问题

## 📁 项目结构

```
ut/
├── frontend/                 # 前端项目 (React + TypeScript)
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── pages/           # 页面
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── services/        # API 服务
│   │   └── styles/          # 样式文件
│   └── package.json
├── backend/                  # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── tools/           # SSH/命令工具
│   │   └── models/          # 数据模型
│   └── requirements.txt
├── dify-plugin/             # Dify 自定义插件
│   ├── ssh_tool/            # SSH 工具插件
│   └── ops_commands/        # 运维命令插件
├── docker/                  # Docker 配置
│   └── docker-compose.yml
└── docs/                    # 文档
    └── setup.md
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd D:\work\ut

# 安装前端依赖
cd frontend
npm install

# 安装后端依赖
cd ../backend
pip install -r requirements.txt
```

### 2. 配置 Dify

1. 访问 Dify 控制台
2. 创建 Agent 应用
3. 配置知识库和工具插件
4. 获取 API Key

### 3. 启动服务

```bash
# 启动后端
cd backend
uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend
npm run dev
```

## 📖 详细文档

- [安装部署指南](docs/setup.md)
- [Dify 配置指南](docs/dify-config.md)
- [SSH 工具插件开发](docs/ssh-plugin.md)
- [API 接口文档](docs/api.md)

## 🔐 安全注意事项

⚠️ **重要安全提醒**：

1. **SSH 密钥管理** - 生产环境建议使用密钥认证而非密码
2. **IP 白名单** - 限制可访问的服务器 IP 范围
3. **命令白名单** - 仅允许预定义的安全命令
4. **审计日志** - 记录所有远程操作日志
5. **权限控制** - 实现基于角色的访问控制

## 📝 License

MIT License
