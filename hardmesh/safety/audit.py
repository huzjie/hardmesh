"""审计日志：追加式 JSONL，记录所有设备操作。"""
import json
import os
import threading
import time
import uuid
from typing import Any, Dict, Optional


class AuditLog:
    """追加式审计日志（JSONL），用于合规与溯源。"""

    def __init__(self, path: str = "hardmesh_audit.jsonl"):
        self.path = path
        self._lock = threading.Lock()

    def record(self, event: str, actor: str, device_id: str = "",
               action: str = "", params: Optional[Dict[str, Any]] = None,
               result: Optional[Any] = None, decision: str = "") -> Dict[str, Any]:
        entry = {
            "ts": time.time(),
            "event": event,
            "actor": actor,
            "device_id": device_id,
            "action": action,
            "params": params or {},
            "result": result,
            "decision": decision,
            "entry_id": uuid.uuid4().hex,
        }
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        return entry

    def read_all(self) -> list:
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return out

    def query(self, device_id: str = "", limit: int = 100) -> list:
        rows = self.read_all()
        if device_id:
            rows = [r for r in rows if r.get("device_id") == device_id]
        return rows[-limit:]
