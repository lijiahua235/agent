import json
import redis
import asyncio
from langgraph.checkpoint.base import BaseCheckpointSaver
from dataclasses import dataclass

# ========== 1. 定义 Redis 持久化存储类 ==========

class RedisSaver(BaseCheckpointSaver):
    """自定义 Redis 存储类，用于保存和加载对话记忆。"""
    def __init__(self, host="localhost", port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    async def aget(self, config):
        """根据 thread_id 读取存储的 checkpoint。"""
        thread_id = config["configurable"]["thread_id"]
        data = self.r.get(f"thread:{thread_id}")
        if data:
            return json.loads(data)
        return None

    async def asave(self, config, checkpoint):
        """将 checkpoint 存储到 Redis。"""
        thread_id = config["configurable"]["thread_id"]
        self.r.set(f"thread:{thread_id}", json.dumps(checkpoint))

    async def alist(self, config):
        """列出所有存储的线程 ID（可选）。"""
        keys = self.r.keys("thread:*")
        return [k.split(":")[1] for k in keys]



@dataclass
class Context:
    """Runtime context injected into tools"""
    user_id: str

@dataclass
class ResponseFormat:
    """Agent's structured response format"""
    punny_response: str
    weather_conditions: str | None = None