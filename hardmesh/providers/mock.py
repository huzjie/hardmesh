"""Mock Provider：确定性离线输出，保证端到端可跑。"""
import hashlib
import json
from typing import Dict, List

from hardmesh.providers.base import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def __init__(self, config=None):
        super().__init__(config)

    def _digest(self, text: str) -> int:
        return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)

    def complete(self, prompt: str, **kwargs) -> str:
        if "校准" in prompt or "calibrat" in prompt.lower():
            return json.dumps([
                {"step_id": "calibrate", "device": "laser-01", "action": "calibrate",
                 "params": {"target": 0.99}, "description": "执行激光校准"},
            ], ensure_ascii=False)
        if "读取" in prompt or "read" in prompt.lower():
            return json.dumps([
                {"step_id": "read", "device": "sensor-temp-01", "action": "read",
                 "params": {}, "description": "读取温度"},
            ], ensure_ascii=False)
        return "已完成任务分析（mock 输出）"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        if "final" in last_user.lower() or "总结" in last_user:
            return json.dumps({"final": "设备操作已完成"}, ensure_ascii=False)
        return json.dumps({"tool": "list_devices", "args": {}}, ensure_ascii=False)
