"""SQLite 存储：设备/观测/校准结果/审计事件持久化。"""
import json
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional


class SqliteStore:
    """线程安全的 SQLite 存储。"""

    def __init__(self, path: str = "hardmesh.db"):
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                name TEXT,
                kind TEXT,
                descriptor TEXT,
                state TEXT,
                updated_at REAL
            );
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                action TEXT,
                params TEXT,
                result TEXT,
                error TEXT,
                ts REAL
            );
            CREATE TABLE IF NOT EXISTS calibrations (
                device_id TEXT PRIMARY KEY,
                result TEXT,
                score REAL,
                ts REAL
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                device_id TEXT,
                action TEXT,
                detail TEXT,
                ts REAL
            );
            """)
            self._conn.commit()

    def upsert_device(self, device_id: str, name: str, kind: str, descriptor: str, state: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO devices(device_id,name,kind,descriptor,state,updated_at) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(device_id) DO UPDATE SET name=excluded.name, kind=excluded.kind, "
                "descriptor=excluded.descriptor, state=excluded.state, updated_at=excluded.updated_at",
                (device_id, name, kind, descriptor, state, time.time()))
            self._conn.commit()

    def insert_observation(self, device_id: str, action: str, params: Dict, result: Any, error: str = "") -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO observations(device_id,action,params,result,error,ts) VALUES(?,?,?,?,?,?)",
                (device_id, action, json.dumps(params, ensure_ascii=False),
                 json.dumps(result, ensure_ascii=False, default=str), error, time.time()))
            self._conn.commit()

    def save_calibration(self, device_id: str, result: Dict, score: float) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO calibrations(device_id,result,score,ts) VALUES(?,?,?,?) "
                "ON CONFLICT(device_id) DO UPDATE SET result=excluded.result, score=excluded.score, ts=excluded.ts",
                (device_id, json.dumps(result, ensure_ascii=False, default=str), score, time.time()))
            self._conn.commit()

    def record_audit(self, event: str, device_id: str, action: str, detail: Any) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO audit_events(event,device_id,action,detail,ts) VALUES(?,?,?,?,?)",
                (event, device_id, action, json.dumps(detail, ensure_ascii=False, default=str), time.time()))
            self._conn.commit()

    def list_devices(self) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute("SELECT * FROM devices ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]

    def recent_observations(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM observations ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        with self._lock:
            self._conn.close()
