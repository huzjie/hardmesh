"""闭环校准循环：测量 → 评估 → 收敛判断 → 停止。"""
from typing import Any, Callable, Dict, List, Optional


class CalibrationLoop:
    """把「设参数 → 测量 → 算分」串成闭环迭代。

    ``setter(params)`` 把参数写到设备；``measure()`` 返回采样列表；
    ``objective(params)->float`` 给当前参数打分。
    """

    def __init__(self, setter: Callable[[Dict[str, Any]], None],
                 measure: Callable[[], List[float]],
                 objective: Callable[[Dict[str, Any]], float],
                 tolerance: float = 0.001, max_iterations: int = 50):
        self.setter = setter
        self.measure = measure
        self.objective = objective
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.history: List[Dict[str, Any]] = []

    def run(self, initial: Dict[str, Any], bounds: Dict[str, List[float]]) -> Dict[str, Any]:
        best_params = dict(initial)
        self.setter(best_params)
        best_score = self.objective(best_params)
        self.history.append({"iteration": 0, "params": dict(best_params), "score": best_score})

        # 简易爬山：单维扰动，接受提升
        import random
        rng = random.Random(0)
        for it in range(1, self.max_iterations + 1):
            improved = False
            for name, (lo, hi) in bounds.items():
                candidate = dict(best_params)
                delta = (hi - lo) * 0.05 * rng.choice([-1, 1])
                candidate[name] = min(hi, max(lo, candidate[name] + delta))
                self.setter(candidate)
                score = self.objective(candidate)
                self.history.append({"iteration": it, "params": dict(candidate), "score": score})
                if score > best_score:
                    best_params, best_score = candidate, score
                    improved = True
            if best_score >= 1.0 - self.tolerance:
                break
            if not improved:
                break
        return {
            "params": best_params,
            "score": best_score,
            "iterations": len(self.history),
            "converged": best_score >= 1.0 - self.tolerance,
            "history": self.history,
        }
