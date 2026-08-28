"""策略引擎：拒绝式默认（default-deny）的安全决策。"""
from typing import Any, Dict, Optional

from hardmesh.errors import SafetyViolation
from hardmesh.safety.rules import DEFAULT_RULES


class PolicyEngine:
    """基于规则列表的安全策略引擎（按顺序第一个匹配生效）。"""

    def __init__(self, rules=None, default_deny: bool = True):
        self.rules = rules if rules is not None else list(DEFAULT_RULES)
        self.default_deny = default_deny

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估一次操作请求（按规则顺序，第一个匹配生效）。

        context 字段：device_id / capability / action / risk / params。
        返回 {decision: allow|warn|deny|approve, matched_rule, reason}。
        """
        for rule in self.rules:
            if self._match(rule.get("match", {}), context):
                return {"decision": rule["action"], "matched_rule": rule["id"], "reason": rule["description"]}
        if self.default_deny:
            return {"decision": "deny", "matched_rule": None, "reason": "默认拒绝：无匹配规则"}
        return {"decision": "allow", "matched_rule": None, "reason": "默认放行"}

    def enforce(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = self.evaluate(context)
        if result["decision"] == "deny":
            raise SafetyViolation(f"安全策略拒绝：{result['reason']}")
        return result

    @staticmethod
    def _match(match: Dict[str, Any], context: Dict[str, Any]) -> bool:
        for key, val in match.items():
            if key == "actions":
                if context.get("action") not in val:
                    return False
            elif key == "capability":
                if context.get("capability") != val:
                    return False
            elif key == "risk":
                if context.get("risk") != val:
                    return False
            elif key == "kind":
                if context.get("kind") != val:
                    return False
        return True
