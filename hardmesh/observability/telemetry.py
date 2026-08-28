"""遥测：聚合指标、追踪与审计的统一入口。"""
import time
from typing import Any, Dict, Optional

from hardmesh.observability.metrics import MetricsRegistry
from hardmesh.observability.tracing import TraceContext
from hardmesh.safety.audit import AuditLog


class Telemetry:
    """统一遥测入口，包装 metrics + tracing + audit。"""

    def __init__(self, metrics: Optional[MetricsRegistry] = None,
                 audit: Optional[AuditLog] = None):
        self.metrics = metrics or MetricsRegistry()
        self.audit = audit or AuditLog()

    def operation(self, device_id: str, action: str, result: Any, duration_s: float,
                  actor: str = "system", decision: str = "allow") -> None:
        self.metrics.counter_inc("hardmesh_operations_total")
        self.metrics.counter_inc(f"hardmesh_operations_{action}_total")
        self.metrics.histogram_observe("hardmesh_operation_duration_seconds", duration_s)
        self.audit.record("operation", actor, device_id=device_id, action=action,
                          result=result, decision=decision)
