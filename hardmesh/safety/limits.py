"""物理限位：温度/电压/电流/力矩等硬性安全边界。"""
from typing import Any, Dict

from hardmesh.errors import SafetyViolation

_LIMIT_PARAMS = {
    "voltage": "max_voltage_v",
    "current": "max_current_a",
    "temperature": "max_temperature_c",
    "torque": "max_torque_nm",
    "power": "max_power_mw",
}


class PhysicalLimits:
    """检查操作参数是否突破物理安全边界。"""

    def __init__(self, limits: Dict[str, float] = None):
        self.limits = limits or {}

    def check(self, action: str, params: Dict[str, Any]) -> None:
        for key, limit_key in _LIMIT_PARAMS.items():
            if key in params and limit_key in self.limits:
                val = params[key]
                if isinstance(val, (int, float)) and val > self.limits[limit_key]:
                    raise SafetyViolation(
                        f"参数 {key}={val} 超出限位 {self.limits[limit_key]}"
                    )
        # 温度类动作的 target 参数特殊校验
        if "target" in params and "max_temperature_c" in self.limits:
            t = params["target"]
            if isinstance(t, (int, float)) and t > self.limits["max_temperature_c"]:
                raise SafetyViolation(
                    f"目标值 {t} 超出温度上限 {self.limits['max_temperature_c']}")

    def set_limit(self, name: str, value: float) -> None:
        self.limits[name] = value
