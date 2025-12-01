# ⚡ FlashShare (瞬传)

**FlashShare** 是一个基于 **FastAPI** 和 **Vue 3** 构建的轻量级、高性能多用户文件互传系统。

它的核心理念是 **“阅后即焚” (Ephemeral Sharing)**：用户进入特定的“房间”后，可以实时发送文字消息或传输文件。所有数据（消息和文件）在服务器端仅保留极短的时间（如 10 分钟），过期后系统会自动进行物理销毁，确保隐私安全且不占用服务器存储。

## ✨ 核心特性

  * **👥 多用户实时协作**：基于 WebSocket 的房间机制，支持多人同时在线交流。
  * **🚀 文件流式传输**：支持大文件上传与下载，不占用过多服务器内存。
  * **⏱️ 生命周期管理**：内置后台“清洁工”任务，自动检测并物理删除过期文件。
  * **🔒 隐私安全**：数据短暂存储，过期即焚，无持久化数据库负担。
  * **⚡ 极速响应**：前端采用 Vue 3 + Vite，后端采用异步 FastAPI，体验流畅。

## 🛠️ 技术栈

### Backend (后端)

  * **Language**: Python 3.10+
  * **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (异步 Web 框架)
  * **Server**: Uvicorn (ASGI 服务器)
  * **Concurrency**: `asyncio` (用于 WebSocket 和后台清理任务)
  * **Storage**: 内存 (元数据) + 本地文件系统 (文件实体)

### Frontend (前端)

  * **Framework**: [Vue.js 3](https://vuejs.org/) (Composition API)
  * **Build Tool**: [Vite](https://vitejs.dev/)
  * **Styling**: CSS3 Flexbox (原生手写，无繁重 UI 库)

-----

## 📂 目录结构

```text
FlashShare/
├── backend/                 # 后端核心代码
│   ├── main.py              # FastAPI 入口与路由配置
│   ├── connection_manager.py# WebSocket 连接与房间管理
│   ├── cleaner.py           # 后台自动清理任务 (The Cleaner)
│   ├── models.py            # Pydantic 数据模型定义
│   ├── requirements.txt     # Python 依赖清单
│   └── uploads/             # [自动生成] 文件临时存储目录
│
├── frontend/                # 前端界面代码
│   ├── src/
│   │   ├── App.vue          # 主应用逻辑 (聊天/上传/倒计时)
│   │   └── main.js          # Vue 入口
│   ├── index.html           # 网页入口
│   └── package.json         # Node.js 依赖配置
│
└── README.md                # 项目说明文档
```

-----

## 🚀 快速开始

### 1\. 后端环境搭建

确保已安装 Python 3.8 或更高版本。

```bash
# 1. 进入后端目录
cd backend

# 2. (可选) 创建并激活虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务器 (默认端口 8000)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

当看到 `🧹 清理工已启动...` 时，说明后端运行正常。

### 2\. 前端环境搭建

确保已安装 Node.js (推荐 v16+)。

```bash
# 1. 打开新的终端窗口，进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

打开浏览器访问终端显示的地址（通常是 `http://localhost:5173`）。

-----

## 📖 使用指南

1.  **加入房间**：打开网页，输入任意房间号（例如 `1001`）并点击“进入”。
2.  **多端测试**：打开第二个浏览器窗口（或手机浏览器连接同一 WiFi），输入相同的房间号。
3.  **发送消息**：输入文字，对方立即可见。
4.  **传输文件**：点击 📎 图标选择文件上传。
      * 上传完成后，房间内所有人会看到下载链接。
      * 消息右侧会显示倒计时（默认 10 分钟）。
5.  **过期销毁**：倒计时结束后，文件链接失效，服务器物理文件被自动删除，消息变为灰色不可用。

-----

## ⚙️ 配置说明

你可以在 `backend/main.py` 和 `backend/cleaner.py` 中调整核心参数：

  * **文件有效期 (TTL)**:
      * 修改 `backend/main.py` 中的 `DEFAULT_TTL = 600` (单位：秒)。
  * **清理检查频率**:
      * 修改 `backend/main.py` 启动事件中的 `interval=5` (单位：秒)。

-----

## 📝 待办事项 (To-Do)

  * [ ] **部署支持**: 添加 Dockerfile 和 docker-compose.yml。
  * [ ] **文件预览**: 支持图片、PDF 在线预览而非直接下载。
  * [ ] **加密传输**: 实现端到端加密 (E2EE)，服务器无法窥探文件内容。
  * [ ] **最大限制**: 添加文件大小限制 (目前未限制)。

-----

## 🤝 贡献与许可

本项目采用 MIT 许可证。欢迎提交 Issues 和 Pull Requests！

Copyright (c) 2023 FlashShare Team.