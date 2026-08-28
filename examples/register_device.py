"""注册自定义设备并执行动作。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardmesh.device.descriptor import ActionSpec, DeviceDescriptor, ParameterSpec
from hardmesh.device.registry import DeviceRegistry
from hardmesh.driver.manager import DriverManager


def main():
    registry = DeviceRegistry()
    manager = DriverManager()

    desc = DeviceDescriptor(
        device_id="pump-01", name="精密注射泵", kind="pump",
        capabilities=["read", "write", "actuate"],
        actions=[
            ActionSpec("infuse", "注入液体", [
                ParameterSpec("volume_ml", type="float", required=True, minimum=0.1, maximum=50.0),
                ParameterSpec("rate_ml_min", type="float", default=1.0),
            ], risk="medium"),
        ],
        driver="mock",
    )
    dev = registry.register_descriptor(desc, manager.resolve("mock"))
    dev.driver.connect("pump-01")
    from hardmesh.device.state import DeviceState
    dev.transition(DeviceState.CONNECTING)
    dev.transition(DeviceState.IDLE)

    result = dev.act("infuse", volume_ml=5.0, rate_ml_min=2.0)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
