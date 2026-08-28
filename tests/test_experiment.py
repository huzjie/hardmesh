"""实验编排测试。"""
import time

from hardmesh.experiment.observation import Observation
from hardmesh.experiment.retry import SelfRepairRetry
from hardmesh.experiment.workflow import ExperimentWorkflow, Step


def test_workflow_sequential():
    wf = ExperimentWorkflow("test")
    order = []
    def exec(step):
        order.append(step.step_id)
        return Observation(step_id=step.step_id, result="ok",
                           started_at=time.time(), finished_at=time.time())
    wf.add_step(Step("a", action="x"))
    wf.add_step(Step("b", action="y", depends_on=["a"]))
    obs = wf.run(exec)
    assert order == ["a", "b"]
    assert all(o.ok for o in obs)


def test_retry_success_after_fail():
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("boom")
        return "ok"
    r = SelfRepairRetry(max_retries=3, base_delay=0.01)
    assert r.call(flaky) == "ok"
    assert calls["n"] == 2


def test_observation_duration():
    o = Observation(step_id="s", started_at=10.0, finished_at=12.5)
    assert o.duration_s == 2.5
    assert o.ok
