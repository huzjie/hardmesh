"""自动化实验工作流：声明式步骤 + 自修复重试。"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardmesh.device.builtins import laser, temperature_sensor
from hardmesh.device.registry import DeviceRegistry
from hardmesh.device.state import DeviceState
from hardmesh.driver.manager import DriverManager
from hardmesh.experiment.retry import SelfRepairRetry
from hardmesh.experiment.observation import Observation
from hardmesh.experiment.workflow import ExperimentWorkflow, Step


def main():
    registry = DeviceRegistry()
    manager = DriverManager()
    laser_dev = registry.register_descriptor(laser("laser-01"), manager.resolve("mock"))
    laser_dev.driver.connect("laser-01")
    laser_dev.transition(DeviceState.CONNECTING)
    laser_dev.transition(DeviceState.IDLE)
    sensor = registry.register_descriptor(temperature_sensor("sensor-temp-01"), manager.resolve("mock"))
    sensor.driver.connect("sensor-temp-01")
    sensor.transition(DeviceState.CONNECTING)
    sensor.transition(DeviceState.IDLE)

    retry = SelfRepairRetry(max_retries=2, base_delay=0.1)

    def executor(step: Step) -> Observation:
        started = time.time()
        try:
            dev = registry.get(step.device_id)
            if step.action == "read":
                result = retry.call(lambda: dev.read("temperature"))
            else:
                result = retry.call(lambda: dev.act(step.action, **step.params))
            return Observation(step_id=step.step_id, device_id=step.device_id,
                               action=step.action, params=step.params, result=result,
                               started_at=started, finished_at=time.time())
        except Exception as e:
            return Observation(step_id=step.step_id, device_id=step.device_id,
                               action=step.action, params=step.params, error=str(e),
                               started_at=started, finished_at=time.time())

    wf = ExperimentWorkflow("laser-stability-check")
    wf.add_step(Step("cal", "laser-01", "calibrate", {"target": 0.99}, "校准激光器"))
    wf.add_step(Step("measure", "sensor-temp-01", "read", {}, "读取温度", depends_on=["cal"]))
    obs = wf.run(executor)

    print(json.dumps({
        "workflow": wf.to_dict(),
        "observations": [o.to_dict() for o in obs],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
