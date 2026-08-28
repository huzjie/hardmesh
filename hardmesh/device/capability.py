"""设备能力模型：声明设备支持读/写/校准/动作等能力。"""
from enum import Enum


class Capability(str, Enum):
    """设备能力类别（MHS capability）。"""
    READ = "read"               # 读取测量值/状态
    WRITE = "write"             # 写入设定值/参数
    ACTUATE = "actuate"         # 物理动作（移动/抓取/开关）
    CALIBRATE = "calibrate"     # 校准
    CONFIGURE = "configure"     # 配置
    STREAM = "stream"           # 持续数据流（传感器）
    EXECUTE = "execute"         # 执行自定义程序
    RESET = "reset"             # 复位/急停

    @classmethod
    def all(cls):
        return [c.value for c in cls]
