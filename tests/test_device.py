"""设备抽象层测试。"""
from hardmesh.device.base import Device
from hardmesh.device.builtins import laser, robotic_arm, temperature_sensor
from hardmesh.device.registry import DeviceRegistry
from hardmesh.device.state import DeviceState, can_transition
from hardmesh.errors import CapabilityDenied, DeviceNotFound
from hardmesh.driver.manager import DriverManager


def test_registry_register_and_get():
    reg = DeviceRegistry()
    mgr = DriverManager()
    reg.register_descriptor(laser("laser-01"), mgr.resolve("mock"))
    dev = reg.get("laser-01")
    assert dev.device_id == "laser-01"
    assert "calibrate" in dev.descriptor.capabilities


def test_registry_get_missing_raises():
    reg = DeviceRegistry()
    try:
        reg.get("nope")
        assert False
    except DeviceNotFound:
        assert True


def test_state_transitions():
    assert can_transition(DeviceState.REGISTERED, DeviceState.CONNECTING)
    assert not can_transition(DeviceState.IDLE, DeviceState.UNREGISTERED)


def test_capability_enforced():
    reg = DeviceRegistry()
    mgr = DriverManager()
    sensor = reg.register_descriptor(temperature_sensor("sensor-temp-01"), mgr.resolve("mock"))
    sensor.driver.connect("sensor-temp-01")
    sensor.transition(DeviceState.CONNECTING)
    sensor.transition(DeviceState.IDLE)
    try:
        sensor.act("move")  # 传感器无动作能力
        assert False
    except CapabilityDenied:
        assert True


def test_arm_move():
    reg = DeviceRegistry()
    mgr = DriverManager()
    arm = reg.register_descriptor(robotic_arm("arm-01"), mgr.resolve("mock"))
    arm.driver.connect("arm-01")
    arm.transition(DeviceState.CONNECTING)
    arm.transition(DeviceState.IDLE)
    result = arm.act("move", joints="10,20,30,40,50,60", speed=30.0)
    assert result["done"] is True


def test_filter_by_kind():
    reg = DeviceRegistry()
    mgr = DriverManager()
    reg.register_descriptor(laser("laser-01"), mgr.resolve("mock"))
    reg.register_descriptor(robotic_arm("arm-01"), mgr.resolve("mock"))
    assert len(reg.filter(kind="laser")) == 1
    assert len(reg.filter(kind="arm")) == 1
