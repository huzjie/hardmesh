"""Provider 层测试。"""
from hardmesh.providers.mock import MockProvider
from hardmesh.providers import get_provider


def test_mock_complete_calibration():
    p = MockProvider()
    out = p.complete("请校准激光器")
    assert "calibrate" in out


def test_get_provider_mock_fallback():
    p = get_provider("nonexistent", {})
    assert p.name == "mock"


def test_get_provider_real():
    p = get_provider("deepseek", {"api_key": "x"})
    assert p.name == "deepseek"


def test_mock_chat():
    p = MockProvider()
    out = p.chat([{"role": "user", "content": "hello"}])
    assert "tool" in out or "final" in out
