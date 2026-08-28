"""ReAct 风格智能体循环：观察 → 思考 → 工具调用 → 反馈。"""
import json
import time
from typing import Any, Dict, List, Optional


class AgentLoop:
    """基于 LLM 的 ReAct 设备控制循环。"""

    def __init__(self, provider, tools: List[Dict[str, Any]], max_steps: int = 10):
        self.provider = provider
        self.tools = tools
        self.max_steps = max_steps

    def run(self, goal: str, executor) -> List[Dict[str, Any]]:
        history: List[Dict[str, Any]] = []
        tool_desc = json.dumps(self.tools, ensure_ascii=False)
        messages = [
            {"role": "system", "content": f"你是硬件控制智能体。可用工具：{tool_desc}。"
                                          "每步只调用一个工具，输出 JSON: {\"tool\": \"name\", \"args\": {...}} 或 {\"final\": \"总结\"}。"},
            {"role": "user", "content": goal},
        ]
        for step in range(self.max_steps):
            raw = self.provider.chat(messages)
            call = self._parse(raw)
            if call is None:
                history.append({"step": step, "raw": raw, "type": "unknown"})
                break
            if "final" in call:
                history.append({"step": step, "type": "final", "final": call["final"]})
                break
            tool = call.get("tool", "")
            args = call.get("args", {})
            try:
                result = executor(tool, args)
                obs = {"step": step, "type": "tool", "tool": tool, "args": args, "result": result}
            except Exception as e:
                obs = {"step": step, "type": "error", "tool": tool, "error": str(e)}
            history.append(obs)
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": json.dumps(obs, ensure_ascii=False, default=str)})
        return history

    @staticmethod
    def _parse(raw: str) -> Optional[Dict[str, Any]]:
        text = raw.strip()
        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    return None
        return None
