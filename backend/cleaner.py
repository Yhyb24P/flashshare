# backend/cleaner.py
import asyncio
import time
import os
from typing import Dict
# 确保这里导入没问题，如果 connection_manager.py 也不存在会报另一个错，但目前先修这个
from connection_manager import ConnectionManager
from models import StoredItem, MessageType

async def start_cleaner_task(storage: Dict[str, StoredItem], manager: ConnectionManager, interval: int = 10):
    """
    后台清理任务
    :param storage: 全局内存数据库
    :param manager: WebSocket管理器 (用于通知前端)
    :param interval: 检查间隔 (秒)
    """
    print(f"🧹 清理工已启动，每 {interval} 秒检查一次...")
    
    while True:
        try:
            current_time = time.time()
            expired_ids = []

            # 1. 扫描过期项目
            for item_id, item in storage.items():
                if item.message_data.expires_at < current_time:
                    expired_ids.append(item_id)

            # 2. 执行清理
            for item_id in expired_ids:
                if item_id not in storage:
                    continue
                    
                item = storage[item_id]
                
                # A. 如果是文件，物理删除
                if item.type == MessageType.FILE and item.file_path:
                    if os.path.exists(item.file_path):
                        try:
                            os.remove(item.file_path)
                            print(f"🗑️ 物理文件已删除: {item.file_path}")
                        except Exception as e:
                            print(f"❌ 删除文件失败: {e}")

                # B. 通知房间内的用户
                await manager.broadcast_to_room(
                    item.room_id,
                    {
                        "type": MessageType.EXPIRED,
                        "id": item_id,
                        "content": "该消息/文件已过期并被销毁"
                    }
                )

                # C. 从内存中移除记录
                del storage[item_id]
                print(f"🧹 记录已清除: {item_id}")

        except Exception as e:
            print(f"❌ 清理任务出错: {e}")

        # 休息一下
        await asyncio.sleep(interval)