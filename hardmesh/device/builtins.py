"""内置设备描述符工厂：开箱即用的 mock 设备样例。

覆盖机械臂 / 显微镜 / 激光器 / 传感器 / 恒温器五类典型硬件，
`mock` 驱动离线即可连接与操作，用于端到端演示。
"""
from hardmesh.device.descriptor import ActionSpec, DeviceDescriptor, ParameterSpec


def _f(name, **kw):
    return ParameterSpec(name=name, **kw)


def robotic_arm(device_id="arm-01") -> DeviceDescriptor:
    return DeviceDescriptor(
        device_id=device_id, name="六轴机械臂", kind="arm",
        manufacturer="HardMesh", model="HM-Arm-6", version="1.2.0",
        capabilities=["read", "write", "actuate", "configure", "reset"],
        actions=[
            ActionSpec("move", "移动到指定关节坐标", [
                _f("joints", type="str", required=True, description="逗号分隔的六关节角度"),
                _f("speed", type="float", default=30.0, unit="deg/s", minimum=1.0, maximum=100.0),
            ], risk="high"),
            ActionSpec("grip", "控制夹爪开合", [
                _f("force", type="float", default=10.0, unit="N", minimum=0.0, maximum=50.0),
            ], risk="medium"),
            ActionSpec("home", "回机械原点", [], risk="low"),
            ActionSpec("estop", "急停", [], risk="critical", reversible=False),
        ],
        properties={"axes": 6, "payload_kg": 5.0},
        driver="mock", tags=["robotics", "lab"],
    )


def microscope(device_id="microscope-01") -> DeviceDescriptor:
    return DeviceDescriptor(
        device_id=device_id, name="自动显微镜", kind="microscope",
        manufacturer="HardMesh", model="HM-Micro-2", version="1.0.0",
        capabilities=["read", "write", "actuate", "stream"],
        actions=[
            ActionSpec("focus", "自动对焦", [
                _f("z", type="float", required=True, unit="um"),
            ], risk="low"),
            ActionSpec("capture", "采集图像", [
                _f("exposure_ms", type="int", default=50, minimum=1, maximum=5000),
            ], risk="low"),
            ActionSpec("move_stage", "移动载物台", [
                _f("x", type="float", required=True, unit="um"),
                _f("y", type="float", required=True, unit="um"),
            ], risk="medium"),
        ],
        properties={"magnification": "4x-100x"},
        driver="mock", tags=["imaging", "lab"],
    )


def laser(device_id="laser-01") -> DeviceDescriptor:
    return DeviceDescriptor(
        device_id=device_id, name="量子实验室激光器", kind="laser",
        manufacturer="HardMesh", model="HM-Laser-Q", version="3.0.1",
        capabilities=["read", "write", "calibrate", "reset"],
        actions=[
            ActionSpec("set_power", "设置输出功率", [
                _f("power", type="float", required=True, unit="mW", minimum=0.0, maximum=100.0),
            ], capability="write", risk="medium"),
            ActionSpec("set_wavelength", "设置波长", [
                _f("wavelength", type="float", required=True, unit="nm", minimum=300.0, maximum=1600.0),
            ], capability="write", risk="medium"),
            ActionSpec("calibrate", "执行激光校准", [
                _f("target", type="float", required=True, description="目标稳定率/参数"),
            ], capability="calibrate", risk="high"),
            ActionSpec("shutdown", "安全关机", [], capability="reset", risk="high", reversible=False),
        ],
        properties={"max_power_mw": 100.0, "wavelength_range": "300-1600nm"},
        driver="mock", tags=["optics", "quantum"],
    )


def temperature_sensor(device_id="sensor-temp-01") -> DeviceDescriptor:
    return DeviceDescriptor(
        device_id=device_id, name="温度传感器", kind="sensor",
        manufacturer="HardMesh", model="HM-Temp-PT100", version="1.0.0",
        capabilities=["read", "stream"],
        actions=[],
        properties={"unit": "celsius", "range": "-40..150C", "precision": 0.1},
        driver="mock", tags=["sensor", "environment"],
    )


def thermostat(device_id="thermostat-01") -> DeviceDescriptor:
    return DeviceDescriptor(
        device_id=device_id, name="恒温反应器", kind="thermostat",
        manufacturer="HardMesh", model="HM-Thermo-R", version="2.0.0",
        capabilities=["read", "write", "actuate", "configure"],
        actions=[
            ActionSpec("set_temperature", "设定目标温度", [
                _f("target", type="float", required=True, unit="C", minimum=-20.0, maximum=200.0),
            ], risk="medium"),
            ActionSpec("hold", "恒温保持", [
                _f("duration_s", type="int", required=True, minimum=1, maximum=86400),
            ], risk="low"),
        ],
        properties={"range": "-20..200C"},
        driver="mock", tags=["thermal", "chemistry"],
    )


def all_builtins() -> list:
    return [robotic_arm(), microscope(), laser(), temperature_sensor(), thermostat()]
