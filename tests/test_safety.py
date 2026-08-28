"""安全护栏测试。"""
from hardmesh.errors import SafetyViolation
from hardmesh.safety.limits import PhysicalLimits
from hardmesh.safety.policy import PolicyEngine


def test_default_deny():
    policy = PolicyEngine(default_deny=True)
    result = policy.evaluate({"device_id": "x", "action": "unknown", "risk": "low"})
    assert result["decision"] == "deny"


def test_read_allowed():
    policy = PolicyEngine(default_deny=True)
    result = policy.evaluate({"device_id": "x", "capability": "read", "action": "read", "risk": "low"})
    assert result["decision"] == "allow"


def test_limits_violation():
    limits = PhysicalLimits({"max_temperature_c": 80.0})
    try:
        limits.check("set_temperature", {"target": 120.0})
        assert False
    except SafetyViolation:
        assert True


def test_limits_ok():
    limits = PhysicalLimits({"max_temperature_c": 80.0})
    limits.check("set_temperature", {"target": 60.0})


def test_approval_flow():
    from hardmesh.safety.approval import ApprovalManager
    am = ApprovalManager(mode="nofm", n=1, m=2)
    req = am.require({"action": "estop"}, ["alice", "bob"])
    assert not am.is_approved(req.request_id)
    assert am.approve(req.request_id, "alice")
    assert am.is_approved(req.request_id)
