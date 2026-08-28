"""W3C Trace Context 传播。"""
import uuid
from typing import Dict, Optional


class TraceContext:
    """生成与解析 W3C traceparent/tracestate。"""

    def __init__(self, trace_id: Optional[str] = None, span_id: Optional[str] = None):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.span_id = span_id or uuid.uuid4().hex[:16]
        self.parent_span_id: Optional[str] = None

    def child(self) -> "TraceContext":
        ctx = TraceContext(self.trace_id)
        ctx.parent_span_id = self.span_id
        return ctx

    def to_traceparent(self) -> str:
        return f"00-{self.trace_id}-{self.span_id}-01"

    @classmethod
    def from_traceparent(cls, header: str) -> "TraceContext":
        parts = header.split("-")
        if len(parts) >= 4:
            ctx = cls(trace_id=parts[1], span_id=parts[2])
            return ctx
        return cls()

    def to_dict(self) -> Dict[str, str]:
        return {"trace_id": self.trace_id, "span_id": self.span_id,
                "parent_span_id": self.parent_span_id or ""}
