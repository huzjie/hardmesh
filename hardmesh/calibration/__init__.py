"""校准引擎：闭环自动化校准（对标 QuEra 量子激光校准 58%→99.3%）。"""
from hardmesh.calibration.engine import CalibrationEngine, CalibrationResult  # noqa: F401
from hardmesh.calibration.objective import ObjectiveFunction, StabilityObjective  # noqa: F401
from hardmesh.calibration.optimizer import GridOptimizer, RandomOptimizer, Optimizer  # noqa: F401
from hardmesh.calibration.metrics import compute_stability, compute_precision  # noqa: F401

__all__ = [
    "CalibrationEngine", "CalibrationResult", "ObjectiveFunction",
    "StabilityObjective", "GridOptimizer", "RandomOptimizer", "Optimizer",
    "compute_stability", "compute_precision",
]
