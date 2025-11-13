import json
import redis
import asyncio
from typing import Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from dataclasses import dataclass

# ========== 1. 定义 Redis 持久化存储类 ==========

class RedisSaver(BaseCheckpointSaver):
    """自定义 Redis 存储类，用于保存和加载对话记忆。"""
    def __init__(self, host="localhost", port=8080, db=0):
        pool = redis.ConnectionPool(host='localhost', port=8080, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)

    def _list_key(self, thread_id: str):
        return f"thread:{thread_id}:list"

    def _checkpoint_key(self, thread_id: str):
        return f"thread:{thread_id}:checkpoint"

    async def add_message(self, thread_id: str, role: str, content: str):
        """向 Redis list 追加一条消息"""
        msg = json.dumps({"role": role, "content": content})
        await self.r.rpush(self._list_key(thread_id), msg)

    async def get_messages(self, thread_id: str):
        """获取某个 session 的全部消息"""
        raw = await self.r.lrange(self._list_key(thread_id), 0, -1)
        return [json.loads(m) for m in raw]

    async def trim_messages(self, thread_id: str, max_len: int):
        """保留最近 max_len 条消息"""
        await self.r.ltrim(self._list_key(thread_id), -max_len, -1)

    async def clear_messages(self, thread_id: str):
        await self.r.delete(self._list_key(thread_id))

    # ========== checkpoint 操作 ==========
    async def save_checkpoint(self, thread_id: str, checkpoint: dict):
        """保存完整 checkpoint"""
        await self.r.set(self._checkpoint_key(thread_id), json.dumps(checkpoint))

    async def load_checkpoint(self, thread_id: str) -> Optional[dict]:
        """读取 checkpoint"""
        data = await self.r.get(self._checkpoint_key(thread_id))
        if data:
            return json.loads(data)
        return None

    async def list_threads(self):
        """列出所有线程 ID"""
        keys = await self.r.keys("thread:*:checkpoint")
        return [k.split(":")[1] for k in keys]



# @dataclass
# class Context:
#     """Runtime context injected into tools"""
#     user_id: str
#
# @dataclass
# class ResponseFormat:
#     """Agent's structured response format"""
#     punny_response: str
#     weather_conditions: str | None = None