# backend/connection_manager.py
from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # 结构: { "room_id": [WebSocket1, WebSocket2, ...] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            # 如果房间空了，可以清理key，节省内存
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        """向特定房间内的所有用户广播消息"""
        if room_id in self.active_connections:
            # 浅拷贝列表以防发送过程中连接断开导致遍历报错
            for connection in self.active_connections[room_id][:]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # 发送失败通常意味着连接已断开，这里简单处理
                    self.disconnect(connection, room_id)