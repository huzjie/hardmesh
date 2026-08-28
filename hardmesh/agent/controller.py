"""设备控制智能体：规划 + 执行 + 观测整合。"""
from typing import Any, Dict, List, Optional

from hardmesh.agent.loop import AgentLoop
from hardmesh.agent.planner import TaskPlanner
from hardmesh.agent.tools import build_tool_definitions, execute_tool
from hardmesh.device.registry import DeviceRegistry


class DeviceController:
    """高层设备控制入口：把自然语言任务转化为设备操作并执行。"""

    def __init__(self, registry: DeviceRegistry, provider=None, max_steps: int = 10):
        self.registry = registry
        self.provider = provider
        self.max_steps = max_steps

    def execute(self, task: str) -> Dict[str, Any]:
        tools = build_tool_definitions(self.registry)
        if self.provider is None or getattr(self.provider, "name", "") == "mock":
            planner = TaskPlanner(self.registry, None)
            steps = planner.plan(task, {"devices": self.registry.ids()})
            results = []
            for s in steps:
                try:
                    if s["action"] == "read":
                        out = self.registry.get(s["device"]).read(s.get("params", {}).get("channel"))
                    else:
                        out = self.registry.get(s["device"]).act(s["action"], **s.get("params", {}))
                    results.append({"step": s, "result": out, "ok": True})
                except Exception as e:
                    results.append({"step": s, "result": None, "ok": False, "error": str(e)})
            return {"task": task, "mode": "rule", "steps": results}
        loop = AgentLoop(self.provider, tools, self.max_steps)
        history = loop.run(task, lambda name, args: execute_tool(self.registry, name, args))
        return {"task": task, "mode": "react", "steps": history}
