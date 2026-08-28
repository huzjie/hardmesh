"""参数优化器：网格搜索 / 随机搜索（零依赖）。"""
import random
from typing import Any, Dict, List


class Optimizer:
    """优化器基类。"""

    name = "optimizer"

    def __init__(self, bounds: Dict[str, List[float]], seed: int = 42):
        """bounds: {参数名: [min, max]}。"""
        self.bounds = bounds
        self.rng = random.Random(seed)

    def propose(self, count: int) -> List[Dict[str, Any]]:
        raise NotImplementedError


class GridOptimizer(Optimizer):
    """等距网格采样。"""

    name = "grid"

    def __init__(self, bounds: Dict[str, List[float]], steps: int = 10, seed: int = 42):
        super().__init__(bounds, seed)
        self.steps = steps

    def propose(self, count: int) -> List[Dict[str, Any]]:
        per_dim = max(1, int(round(count ** (1.0 / max(1, len(self.bounds))))))
        candidates: List[Dict[str, Any]] = []
        for name, (lo, hi) in self.bounds.items():
            pts = [lo + (hi - lo) * i / max(1, per_dim - 1) for i in range(per_dim)]
            candidates.append((name, pts))
        out: List[Dict[str, Any]] = []
        self._cartesian(candidates, {}, out)
        self.rng.shuffle(out)
        return out[:count]

    def _cartesian(self, dims, cur, out):
        if not dims:
            out.append(dict(cur))
            return
        name, pts = dims[0]
        for p in pts:
            cur[name] = p
            self._cartesian(dims[1:], cur, out)
            cur.pop(name, None)


class RandomOptimizer(Optimizer):
    """随机采样（可复现）。"""

    name = "random"

    def propose(self, count: int) -> List[Dict[str, Any]]:
        out = []
        for _ in range(count):
            d = {}
            for name, (lo, hi) in self.bounds.items():
                d[name] = self.rng.uniform(lo, hi)
            out.append(d)
        return out
