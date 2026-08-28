"""端到端演示：注册设备 → 策略评估 → 闭环校准 → 读取结果（离线 mock）。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardmesh.calibration.engine import CalibrationEngine
from hardmesh.device.builtins import laser, temperature_sensor
from hardmesh.device.registry import DeviceRegistry
from hardmesh.driver.manager import DriverManager
from hardmesh.safety.limits import PhysicalLimits
from hardmesh.safety.policy import PolicyEngine


def main():
    registry = DeviceRegistry()
    manager = DriverManager()

    from hardmesh.device.state import DeviceState
    laser_dev = registry.register_descriptor(laser("laser-01"), manager.resolve("mock"))
    laser_dev.driver.connect("laser-01")
    laser_dev.transition(DeviceState.CONNECTING)
    laser_dev.transition(DeviceState.IDLE)

    sensor = registry.register_descriptor(temperature_sensor("sensor-temp-01"), manager.resolve("mock"))
    sensor.driver.connect("sensor-temp-01")
    sensor.transition(DeviceState.CONNECTING)
    sensor.transition(DeviceState.IDLE)

    policy = PolicyEngine(default_deny=False)
    limits = PhysicalLimits({"max_temperature_c": 80.0, "max_power_mw": 100.0})

    # 1. 策略评估
    decision = policy.evaluate({"device_id": "laser-01", "capability": "calibrate",
                                "action": "calibrate", "risk": "high", "params": {"target": 0.99}})
    print("[policy]", decision["decision"], "-", decision["reason"])

    # 2. 闭环校准
    engine = CalibrationEngine(max_iterations=30, tolerance=0.005)
    result = engine.calibrate(laser_dev, target=0.99,
                              param_bounds={"power": [10.0, 90.0], "wavelength": [600.0, 900.0]})
    print("[calibrate] score=%.4f converged=%s iterations=%d"
          % (result.score, result.converged, result.iterations))

    # 3. 读取温度
    print("[read] temperature =", sensor.read("temperature"))

    # 4. 完整输出
    print(json.dumps({
        "devices": registry.snapshot(),
        "calibration": result.to_dict(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
