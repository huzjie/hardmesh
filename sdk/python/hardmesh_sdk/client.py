"""hardmesh Python SDK 客户端（stdlib urllib 实现）。"""
import json
import urllib.request
from typing import Any, Dict, List, Optional


class HardmeshClient:
    """hardmesh 控制面 HTTP 客户端。"""

    def __init__(self, base_url: str = "http://localhost:8080", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> Any:
        url = self.base_url + path
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            body = r.read().decode("utf-8")
            return json.loads(body) if body else {}

    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/healthz")

    def list_devices(self) -> List[Dict[str, Any]]:
        return self._request("GET", "/devices").get("devices", [])

    def get_device(self, device_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/devices/{device_id}")

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        path = f"/devices/{device_id}/read"
        if channel:
            path += f"?channel={channel}"
        return self._request("GET", path).get("value")

    def act(self, device_id: str, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", f"/devices/{device_id}/act",
                             {"action": action, "params": params or {}})

    def metrics(self) -> str:
        return self._request("GET", "/metrics")
