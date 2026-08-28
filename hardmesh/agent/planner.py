"""任务规划器：规则 + LLM 双模式，把自然语言任务分解为设备操作步骤。"""
import json
from typing import Any, Dict, List, Optional


class TaskPlanner:
    """把自然语言任务分解为结构化步骤序列。"""

    def __init__(self, registry=None, provider=None):
        self.registry = registry
        self.provider = provider

    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.provider is not None:
            return self._plan_llm(task, context)
        return self._plan_rule(task, context)

    def _plan_rule(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        ctx = context or {}
        devices = ctx.get("devices", [])
        steps: List[Dict[str, Any]] = []
        low = task.lower()
        if "校准" in task or "calibrat" in low:
            steps.append({"step_id": "calibrate", "device": "laser-01", "action": "calibrate",
                          "params": {"target": 0.99}, "description": "执行激光校准"})
        if "测" in task or "read" in low or "measure" in low:
            steps.append({"step_id": "measure", "device": "sensor-temp-01", "action": "read",
                          "params": {}, "description": "读取温度测量值"})
        if "移动" in task or "move" in low or "arm" in low:
            steps.append({"step_id": "move", "device": "arm-01", "action": "move",
                          "params": {"joints": "0,0,0,0,0,0", "speed": 30.0}, "description": "机械臂归位"})
        if not steps:
            steps.append({"step_id": "inspect", "device": devices[0] if devices else "arm-01",
                          "action": "read", "params": {}, "description": f"检查设备以理解任务: {task}"})
        return steps

    def _plan_llm(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        prompt = f"将以下硬件任务分解为 JSON 步骤列表（step_id/device/action/params/description）：\n{task}\n设备: {context or {}}\n只输出 JSON 数组。"
        resp = self.provider.complete(prompt)
        try:
            data = json.loads(resp)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        return self._plan_rule(task, context)
