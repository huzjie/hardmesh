"""校准指标计算：稳定率与精度。"""
import statistics
from typing import Iterable, List


def compute_stability(samples: Iterable[float]) -> float:
    """稳定率：1 - 变异系数，越接近 1 越稳定。

    CV = std/mean，稳定率 = max(0, 1 - CV)。对标 MHS 案例中的
    「稳定率」语义（58% 人类专家 vs 99.3% Claude）。
    """
    vals: List[float] = [float(v) for v in samples if v is not None]
    if len(vals) < 2:
        return 0.0
    mean = statistics.mean(vals)
    if mean == 0:
        return 0.0
    std = statistics.pstdev(vals)
    cv = std / abs(mean)
    return max(0.0, 1.0 - cv)


def compute_precision(samples: Iterable[float], target: float) -> float:
    """精度：以目标为中心的误差衡量，返回 0..1（1 为完全命中）。"""
    vals = [float(v) for v in samples if v is not None]
    if not vals:
        return 0.0
    mean = statistics.mean(vals)
    rel_err = abs(mean - target) / max(abs(target), 1e-9)
    return max(0.0, 1.0 - min(rel_err, 1.0))


def mean_squared_error(samples: Iterable[float], target: float) -> float:
    vals = [float(v) for v in samples if v is not None]
    if not vals:
        return float("inf")
    return sum((v - target) ** 2 for v in vals) / len(vals)
