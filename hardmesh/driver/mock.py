"""Mock 驱动：离线确定性的设备模拟，保证端到端可演示。

基于设备 id 的 sha256 确定性输出，同一操作结果可复现，便于测试与演示。
"""
import hashlib
import math
import time
from typing import Any, Optional

from hardmesh.driver.base import Driver


class MockDriver(Driver):
    name = "mock"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._state = {}

    def _seed(self, device_id: str) -> int:
        return int(hashlib.sha256(device_id.encode("utf-8")).hexdigest()[:8], 16)

    def _value(self, device_id: str, channel: str) -> float:
        key = f"{device_id}:{channel}"
        base = self._seed(key)
        t = int(time.time())
        # 确定性 + 轻微时间漂移的模拟读数
        return round(20.0 + (base % 1000) / 100.0 + 2.0 * math.sin(t / 7.0 + base % 10), 3)

    def connect(self, device_id: str) -> None:
        self._state.setdefault(device_id, {"connected": True, "pos": [0.0] * 6})
        self._state[device_id]["connected"] = True

    def disconnect(self, device_id: str) -> None:
        self._state.setdefault(device_id, {})["connected"] = False

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        ch = channel or "value"
        if ch in ("temperature", "temp"):
            return round(25.0 + 3.0 * math.sin(time.time() / 5.0), 2)
        if ch in ("position", "pos"):
            return self._state.get(device_id, {}).get("pos", [0.0] * 6)
        return self._value(device_id, ch)

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        self._state.setdefault(device_id, {})[channel] = value
        return {"channel": channel, "value": value, "ack": True}

    def act(self, device_id: str, action: str, params: dict) -> Any:
        st = self._state.setdefault(device_id, {})
        if action == "move":
            joints = [float(x) for x in str(params.get("joints", "0,0,0,0,0,0")).split(",")]
            st["pos"] = joints
            return {"action": action, "position": joints, "done": True}
        if action == "home":
            st["pos"] = [0.0] * 6
            return {"action": action, "position": [0.0] * 6, "done": True}
        if action == "estop":
            st["estop"] = True
            return {"action": action, "estop": True, "done": True}
        if action == "calibrate":
            return {"action": action, "target": params.get("target"),
                    "stability": min(0.999, 0.5 + self._seed(device_id) % 49 / 100.0)}
        if action == "capture":
            return {"action": action, "image_id": "img_" + hashlib.sha256(
                (device_id + str(time.time())).encode()).hexdigest()[:12], "done": True}
        return {"action": action, "params": params, "done": True}

    def stream(self, device_id: str, channel: Optional[str] = None):
        import time as _t
        for _ in range(20):
            yield {"ts": _t.time(), "value": self.read(device_id, channel)}
            _t.sleep(0.05)
