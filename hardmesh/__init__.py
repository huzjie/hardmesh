"""hardmesh — AI 硬件控制网格与实验室自动化平台。

对标 Anthropic MHS（Model Hardware Standard，模型硬件标准，2026-08-28 发布）：
让 LLM 智能体安全地读取并操控真实物理设备（机械臂、显微镜、激光器、
传感器、仪器仪表），并支撑自动化实验与闭环校准。

内核纯 Python 标准库实现，零第三方运行时依赖，``mock`` 模式完全离线可跑。
"""

__version__ = "0.1.0"
__all__ = ["__version__"]

from hardmesh.device.base import Device, DeviceState, DeviceCapability  # noqa: E402,F401
from hardmesh.device.registry import DeviceRegistry  # noqa: E402,F401
