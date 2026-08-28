"""人工审批：N-of-M 审批 + 逐步升级。"""
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ApprovalRequest:
    request_id: str
    context: Dict[str, Any]
    approvers: List[str]
    approvals: List[str] = field(default_factory=list)
    status: str = "pending"
    created_at: float = field(default_factory=time.time)


class ApprovalManager:
    """管理需要人工审批的高风险操作。"""

    def __init__(self, mode: str = "nofm", n: int = 1, m: int = 2):
        self.mode = mode          # nofm / stepup
        self.n = n
        self.m = m
        self._pending: Dict[str, ApprovalRequest] = {}

    def require(self, context: Dict[str, Any], approvers: List[str]) -> ApprovalRequest:
        req = ApprovalRequest(
            request_id=uuid.uuid4().hex,
            context=context,
            approvers=approvers,
        )
        self._pending[req.request_id] = req
        return req

    def approve(self, request_id: str, approver: str) -> bool:
        req = self._pending.get(request_id)
        if req is None:
            return False
        if approver in req.approvers and approver not in req.approvals:
            req.approvals.append(approver)
        if len(req.approvals) >= self.n:
            req.status = "approved"
            return True
        return False

    def is_approved(self, request_id: str) -> bool:
        req = self._pending.get(request_id)
        return req is not None and req.status == "approved"

    def pending(self) -> List[Dict[str, Any]]:
        return [
            {"request_id": r.request_id, "context": r.context,
             "approvals": r.approvals, "status": r.status}
            for r in self._pending.values() if r.status == "pending"
        ]
