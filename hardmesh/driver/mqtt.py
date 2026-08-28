"""MQTT 物联网驱动：面向无线传感器网络（可选依赖 paho-mqtt）。

未安装 paho-mqtt 时仅登记驱动类，连接时给出明确错误。
"""
from typing import Any, Optional

from hardmesh.driver.base import Driver
from hardmesh.errors import DriverError


class MqttDriver(Driver):
    name = "mqtt"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.broker = self.config.get("broker", "127.0.0.1")
        self.port = int(self.config.get("port", 1883))
        self.topic = self.config.get("topic", "hardmesh/+/value")
        self._client = None

    def connect(self, device_id: str) -> None:
        try:
            import paho.mqtt.client as mqtt  # noqa: WPS433
        except ImportError as e:
            raise DriverError("使用 MQTT 驱动需安装 paho-mqtt: pip install paho-mqtt") from e
        self._client = mqtt.Client()
        self._client.connect(self.broker, self.port, 60)
        self._client.loop_start()

    def disconnect(self, device_id: str) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        # 简化实现：返回订阅缓存（真实场景由回调更新）
        return {"topic": self.topic, "device": device_id}

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        if self._client is None:
            raise DriverError("MQTT 未连接")
        self._client.publish(f"hardmesh/{device_id}/{channel}", str(value))
        return {"ack": True}

    def act(self, device_id: str, action: str, params: dict) -> Any:
        return self.write(device_id, action, params.get("value", ""))
