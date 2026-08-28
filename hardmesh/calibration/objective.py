"""校准目标函数：给定参数，通过测量得到标量得分（越大越好）。"""
from typing import Any, Callable, Dict, List


class ObjectiveFunction:
    """目标函数抽象：把一组参数映射到一个 [0,1] 得分。"""

    name = "objective"

    def __call__(self, params: Dict[str, Any]) -> float:
        raise NotImplementedError


class StabilityObjective(ObjectiveFunction):
    """稳定率目标：多次采样后取稳定率作为得分。

    ``measure`` 是一个 ``callable(params) -> list[float]`` 的测量函数，
    返回多次采样的原始读数。
    """

    name = "stability"

    def __init__(self, measure: Callable[[Dict[str, Any]], List[float]], samples: int = 20):
        self.measure = measure
        self.samples = samples

    def __call__(self, params: Dict[str, Any]) -> float:
        from hardmesh.calibration.metrics import compute_stability
        return compute_stability(self.measure(params)[:self.samples])


class PrecisionObjective(ObjectiveFunction):
    """精度目标：读数均值逼近目标值。"""

    name = "precision"

    def __init__(self, measure: Callable[[Dict[str, Any]], List[float]], target: float, samples: int = 20):
        self.measure = measure
        self.target = target
        self.samples = samples

    def __call__(self, params: Dict[str, Any]) -> float:
        from hardmesh.calibration.metrics import compute_precision
        return compute_precision(self.measure(params)[:self.samples], self.target)
