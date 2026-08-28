"""校准引擎：把设备「calibrate」能力包装成可复用的闭环校准流程。"""
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from hardmesh.calibration.loop import CalibrationLoop
from hardmesh.calibration.objective import StabilityObjective
from hardmesh.device.base import Device
from hardmesh.device.state import DeviceState
from hardmesh.errors import CalibrationError


@dataclass
class CalibrationResult:
    device_id: str
    params: Dict[str, Any]
    score: float
    iterations: int
    converged: bool
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "params": self.params,
            "score": self.score,
            "iterations": self.iterations,
            "converged": self.converged,
            "history": self.history,
        }


class CalibrationEngine:
    """驱动设备进行闭环校准。"""

    def __init__(self, max_iterations: int = 50, tolerance: float = 0.001, optimizer: str = "random"):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.optimizer_name = optimizer
        self._lock = threading.RLock()
        self._results: Dict[str, CalibrationResult] = {}

    def calibrate(self, device: Device, target: float,
                  param_bounds: Dict[str, List[float]],
                  initial: Optional[Dict[str, Any]] = None) -> CalibrationResult:
        device.require_capability("calibrate")
        with self._lock:
            device.transition(DeviceState.CALIBRATING)
            try:
                init = initial or {k: (v[0] + v[1]) / 2 for k, v in param_bounds.items()}

                def setter(params):
                    device.act("calibrate", target=target, **params)

                def measure(_params=None):
                    # mock 设备通过 read 得到读数，真实设备由校准动作回传
                    return [float(device.read("value") or 0.0) for _ in range(20)]

                objective = StabilityObjective(measure)
                loop = CalibrationLoop(setter, measure, objective,
                                       tolerance=self.tolerance, max_iterations=self.max_iterations)
                res = loop.run(init, param_bounds)
                result = CalibrationResult(
                    device_id=device.device_id, params=res["params"], score=res["score"],
                    iterations=res["iterations"], converged=res["converged"], history=res["history"],
                )
                self._results[device.device_id] = result
                return result
            except Exception as e:
                raise CalibrationError(f"校准失败 {device.device_id}: {e}")
            finally:
                device.transition(DeviceState.IDLE)

    def last_result(self, device_id: str) -> Optional[CalibrationResult]:
        return self._results.get(device_id)
