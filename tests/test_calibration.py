"""校准引擎测试。"""
from hardmesh.calibration.metrics import compute_precision, compute_stability
from hardmesh.calibration.optimizer import GridOptimizer, RandomOptimizer
from hardmesh.calibration.objective import PrecisionObjective


def test_stability_perfect():
    assert compute_stability([10.0] * 20) > 0.999


def test_precision_hit():
    assert compute_precision([1.0] * 10, target=1.0) > 0.999


def test_grid_optimizer_bounds():
    opt = GridOptimizer({"x": [0.0, 1.0]}, steps=4)
    cands = opt.propose(5)
    assert all(0.0 <= c["x"] <= 1.0 for c in cands)


def test_random_optimizer_count():
    opt = RandomOptimizer({"x": [0.0, 10.0], "y": [0.0, 10.0]}, seed=1)
    assert len(opt.propose(20)) == 20


def test_precision_objective():
    obj = PrecisionObjective(lambda p: [p["x"]] * 10, target=5.0)
    assert obj({"x": 5.0}) > 0.99
    assert obj({"x": 100.0}) < 0.5
