"""配置加载：JSON 文件 + HARDMESH_* 环境变量（``__`` 表示层级）。

优先级：环境变量 > JSON 文件 > 内置默认值。内核零第三方依赖，
不引入 YAML 解析器，规避手写 YAML 解析的递归下降/注释剥离历史坑。
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from hardmesh.errors import ConfigError

ENV_PREFIX = "HARDMESH_"

_DEFAULTS = {
    "server": {"host": "0.0.0.0", "port": 8080},
    "storage": {"path": "hardmesh.db"},
    "safety": {
        "default_deny": True,
        "approval": {"enabled": False, "mode": "nofm", "n": 1, "m": 2},
        "limits": {
            "max_voltage_v": 24.0,
            "max_current_a": 10.0,
            "max_temperature_c": 80.0,
            "max_torque_nm": 5.0,
        },
    },
    "calibration": {
        "max_iterations": 50,
        "tolerance": 0.001,
        "objective": "stability",
        "optimizer": "random",
    },
    "agent": {
        "provider": "mock",
        "max_steps": 10,
        "model": "",
    },
    "providers": {},
    "observability": {"prometheus": True, "tracing": True},
    "logging": {"level": "INFO"},
}


def _flatten(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        key = f"{prefix}__{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        else:
            out[key] = v
    return out


def _set_path(data: Dict[str, Any], path: str, value: Any) -> None:
    parts = path.split("__")
    cur = data
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def _coerce(value: str) -> Any:
    v = value.strip()
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.lower() in ("null", "none"):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置。``path`` 为 JSON 文件路径，可为 None 仅用默认+环境变量。"""
    config = json.loads(json.dumps(_DEFAULTS))

    if path:
        p = Path(path)
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    file_cfg = json.load(f)
                config = _deep_merge(config, file_cfg)
            except json.JSONDecodeError as e:
                raise ConfigError(f"配置文件 JSON 解析失败: {p}: {e}")

    flat_defaults = _flatten(_DEFAULTS)
    for env_key, env_val in os.environ.items():
        if not env_key.startswith(ENV_PREFIX):
            continue
        path_key = env_key[len(ENV_PREFIX):].lower().replace("__", "__")
        if path_key in flat_defaults:
            _set_path(config, path_key, _coerce(env_val))

    return config


def env_path(prefix: str, *parts: str) -> str:
    """构造环境变量名，如 env_path('HARDMESH', 'safety', 'limits', 'max_voltage_v')。"""
    return prefix + "__".join([""] + [str(p).lower() for p in parts])
