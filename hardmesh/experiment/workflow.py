"""实验工作流：声明式步骤序列，串行/并行执行。"""
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from hardmesh.experiment.observation import Observation


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Step:
    step_id: str
    device_id: str = ""
    action: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    depends_on: List[str] = field(default_factory=list)
    retries: int = 0
    status: StepStatus = StepStatus.PENDING
    observation: Optional[Observation] = None


class ExperimentWorkflow:
    """声明式实验工作流执行器。"""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[Step] = []
        self._index: Dict[str, Step] = {}

    def add_step(self, step: Step) -> "ExperimentWorkflow":
        self.steps.append(step)
        self._index[step.step_id] = step
        return self

    def step(self, step_id: str) -> Step:
        return self._index[step_id]

    def run(self, executor: Callable[[Step], Observation]) -> List[Observation]:
        """按依赖顺序执行步骤，返回观测列表。"""
        done: Dict[str, Observation] = {}
        observations: List[Observation] = []
        remaining = list(self.steps)
        while remaining:
            progressed = False
            for step in list(remaining):
                deps_ok = all(done.get(d, None) and done[d].ok for d in step.depends_on)
                if step.depends_on and not deps_ok:
                    continue
                step.status = StepStatus.RUNNING
                obs = executor(step)
                step.observation = obs
                if obs.ok:
                    step.status = StepStatus.SUCCESS
                else:
                    step.status = StepStatus.FAILED
                done[step.step_id] = obs
                observations.append(obs)
                remaining.remove(step)
                progressed = True
            if not progressed:
                # 剩余步骤因依赖失败无法推进
                for step in remaining:
                    step.status = StepStatus.SKIPPED
                break
        return observations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "steps": [
                {
                    "step_id": s.step_id, "device_id": s.device_id,
                    "action": s.action, "params": s.params,
                    "description": s.description, "depends_on": s.depends_on,
                    "status": s.status.value,
                } for s in self.steps
            ],
        }
