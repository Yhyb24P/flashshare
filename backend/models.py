# backend/models.py
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Literal

class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"     # 系统通知
    EXPIRED = "expired"   # 过期通知

# 发送给前端的数据模型
class ChatMessage(BaseModel):
    id: str
    type: MessageType
    room_id: str
    sender: str
    content: Optional[str] = None      # 文字内容
    filename: Optional[str] = None     # 文件名
    file_size: Optional[str] = None    # 文件大小
    download_url: Optional[str] = None # 下载链接
    created_at: float
    expires_at: float

# 内存中存储的元数据结构（比发送给前端的多一个 file_path）
class StoredItem(BaseModel):
    id: str
    type: MessageType
    room_id: str
    file_path: Optional[str] = None  # 仅服务器可见的物理路径
    message_data: ChatMessage        # 包含上面定义的所有展示信息