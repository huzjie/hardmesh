"""实验观测数据模型。"""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Observation:
    step_id: str
    device_id: str = ""
    action: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def duration_s(self) -> float:
        return self.finished_at - self.started_at if self.finished_at else 0.0

    @property
    def ok(self) -> bool:
        return not self.error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id, "device_id": self.device_id,
            "action": self.action, "params": self.params,
            "result": self.result, "error": self.error,
            "started_at": self.started_at, "finished_at": self.finished_at,
            "duration_s": self.duration_s, "ok": self.ok,
        }
