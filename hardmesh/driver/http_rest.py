"""HTTP/REST 设备驱动：面向 REST 风格 API 的智能仪器。"""
import json
import urllib.request
from typing import Any, Optional

from hardmesh.driver.base import Driver
from hardmesh.errors import DriverError


class HttpRestDriver(Driver):
    name = "http"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.base_url = self.config.get("base_url", "http://127.0.0.1:8000")
        self.timeout = float(self.config.get("timeout", 5.0))

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> Any:
        url = self.base_url.rstrip("/") + path
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                body = r.read().decode("utf-8")
                return json.loads(body) if body else {}
        except Exception as e:
            raise DriverError(f"HTTP 请求失败 {method} {url}: {e}")

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        return self._request("GET", f"/devices/{device_id}/read?channel={channel or ''}")

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        return self._request("POST", f"/devices/{device_id}/write", {"channel": channel, "value": value})

    def act(self, device_id: str, action: str, params: dict) -> Any:
        return self._request("POST", f"/devices/{device_id}/act", {"action": action, "params": params})
