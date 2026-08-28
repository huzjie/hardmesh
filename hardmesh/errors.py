"""hardmesh 统一异常体系。"""


class HardmeshError(Exception):
    """所有 hardmesh 异常的基类。"""


class ConfigError(HardmeshError):
    """配置加载或校验失败。"""


class DeviceNotFound(HardmeshError):
    """设备未在注册中心中找到。"""


class DeviceOffline(HardmeshError):
    """设备处于离线/不可达状态时仍尝试操作。"""


class CapabilityDenied(HardmeshError):
    """请求的能力不被设备支持。"""


class SafetyViolation(HardmeshError):
    """操作违反安全策略（默认拒绝）。"""


class ApprovalRequired(HardmeshError):
    """操作需要人工审批但未获得授权。"""


class CalibrationError(HardmeshError):
    """校准流程失败。"""


class ProtocolError(HardmeshError):
    """MHS 协议编解码/路由错误。"""


class DriverError(HardmeshError):
    """设备驱动通信失败。"""


class StorageError(HardmeshError):
    """存储层错误。"""
