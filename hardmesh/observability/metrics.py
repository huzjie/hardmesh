"""Prometheus 文本格式指标注册表。"""
import threading
from typing import Dict, List


class MetricsRegistry:
    """轻量 Prometheus 指标注册表（counter/gauge/histogram）。"""

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}

    def counter_inc(self, name: str, value: float = 1.0) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0.0) + value

    def gauge_set(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def histogram_observe(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms.setdefault(name, []).append(value)

    def render(self) -> str:
        lines = []
        with self._lock:
            for n, v in sorted(self._counters.items()):
                lines.append(f"# TYPE {n} counter")
                lines.append(f"{n} {v}")
            for n, v in sorted(self._gauges.items()):
                lines.append(f"# TYPE {n} gauge")
                lines.append(f"{n} {v}")
            for n, vals in sorted(self._histograms.items()):
                lines.append(f"# TYPE {n} histogram")
                if vals:
                    lines.append(f"{n}_count {len(vals)}")
                    lines.append(f"{n}_sum {sum(vals)}")
        return "\n".join(lines) + ("\n" if lines else "")
