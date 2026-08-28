"""默认安全规则库。"""

# 每条规则：{id, description, risk, action}  action 为 allow/warn/deny/approve
# 规则按列表顺序评估，第一个匹配的规则生效（优先级从上到下递减）。
# 无任何规则匹配时，由 PolicyEngine.default_deny 决定默认行为。
DEFAULT_RULES = [
    {"id": "R003", "description": "超出物理限位的参数直接拒绝", "risk": "critical",
     "action": "deny", "match": {"kind": "limits"}},
    {"id": "R001", "description": "急停/安全关机动作需要人工审批", "risk": "critical",
     "action": "approve", "match": {"actions": ["estop", "shutdown", "emergency_stop"]}},
    {"id": "R002", "description": "高风险动作（移动机械臂）需策略评估", "risk": "high",
     "action": "warn", "match": {"capability": "actuate", "risk": "high"}},
    {"id": "R007", "description": "中风险动作需留意", "risk": "medium",
     "action": "warn", "match": {"capability": "actuate", "risk": "medium"}},
    {"id": "R006", "description": "低风险动作放行", "risk": "low",
     "action": "allow", "match": {"capability": "actuate", "risk": "low"}},
    {"id": "R008", "description": "校准类操作需监控", "risk": "high",
     "action": "warn", "match": {"capability": "calibrate"}},
    {"id": "R009", "description": "写设定值操作放行", "risk": "medium",
     "action": "allow", "match": {"capability": "write"}},
    {"id": "R004", "description": "读取类操作默认放行", "risk": "low",
     "action": "allow", "match": {"capability": "read"}},
]

RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
