# backend/main.py
import os
import time
import uuid
import asyncio
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import ChatMessage, StoredItem, MessageType
from connection_manager import ConnectionManager
from cleaner import start_cleaner_task

# --- 配置 ---
UPLOAD_DIR = "uploads"
DEFAULT_TTL = 600  # 默认存活时间 600秒 (10分钟)

# 确保上传目录存在
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI()

# 允许跨域 (方便前端开发)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 全局状态 ---
# 1. 连接管理器
manager = ConnectionManager()
# 2. 内存数据库: { "uuid": StoredItem }
storage: dict[str, StoredItem] = {}

# --- 生命周期 ---
@app.on_event("startup")
async def startup_event():
    # 启动后台清理任务，将 storage 和 manager 传进去
    asyncio.create_task(start_cleaner_task(storage, manager, interval=5))

# --- API 接口 ---

@app.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            # 接收前端发来的纯文本消息
            data = await websocket.receive_json()
            
            # 构造消息对象
            msg_id = str(uuid.uuid4())
            timestamp = time.time()
            expires_at = timestamp + DEFAULT_TTL
            
            chat_msg = ChatMessage(
                id=msg_id,
                type=MessageType.TEXT,
                room_id=room_id,
                sender=client_id,
                content=data.get("content"),
                created_at=timestamp,
                expires_at=expires_at
            )
            
            # 存入内存
            storage[msg_id] = StoredItem(
                id=msg_id, 
                type=MessageType.TEXT, 
                room_id=room_id, 
                message_data=chat_msg
            )
            
            # 广播给房间所有人
            await manager.broadcast_to_room(room_id, chat_msg.dict())
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...), 
    room_id: str = Form(...),
    sender: str = Form(...)
):
    """处理文件流上传"""
    file_id = str(uuid.uuid4())
    # 为了防止文件名冲突，物理文件名带上UUID
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # 1. 写入磁盘
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="文件保存失败")
        
    # 2. 构造元数据
    timestamp = time.time()
    expires_at = timestamp + DEFAULT_TTL
    
    chat_msg = ChatMessage(
        id=file_id,
        type=MessageType.FILE,
        room_id=room_id,
        sender=sender,
        filename=file.filename,
        # file.size 并不总是准确，这里简化处理，也可以用 os.path.getsize
        download_url=f"/api/download/{file_id}",
        created_at=timestamp,
        expires_at=expires_at
    )
    
    # 3. 存入内存
    storage[file_id] = StoredItem(
        id=file_id,
        type=MessageType.FILE,
        room_id=room_id,
        file_path=file_path,
        message_data=chat_msg
    )
    
    # 4. 广播通知：有人传文件了
    await manager.broadcast_to_room(room_id, chat_msg.dict())
    
    return {"status": "ok", "file_id": file_id}


@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    """文件下载接口"""
    item = storage.get(file_id)
    
    # 校验：是否存在？是否过期？是否是文件类型？
    if not item or item.type != MessageType.FILE:
        raise HTTPException(status_code=404, detail="文件不存在或已过期")
    
    if not os.path.exists(item.file_path):
        # 可能是 storage 还没删，但物理文件被意外删除了
        del storage[file_id]
        raise HTTPException(status_code=404, detail="文件实体已丢失")
        
    # 返回文件流，并设置强制下载的文件名
    return FileResponse(
        item.file_path, 
        filename=item.message_data.filename,
        media_type='application/octet-stream'
    )