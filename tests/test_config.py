"""配置加载测试。"""
import json
import os
import tempfile

from hardmesh.config import load_config


def test_defaults():
    cfg = load_config(None)
    assert cfg["safety"]["default_deny"] is True
    assert cfg["server"]["port"] == 8080


def test_file_override():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"server": {"port": 9999}}, f)
    cfg = load_config(path)
    assert cfg["server"]["port"] == 9999
    os.remove(path)


def test_env_override():
    os.environ["HARDMESH_SERVER__PORT"] = "7777"
    try:
        cfg = load_config(None)
        assert cfg["server"]["port"] == 7777
    finally:
        del os.environ["HARDMESH_SERVER__PORT"]
