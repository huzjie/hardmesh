"""存储层测试。"""
import os
import tempfile

from hardmesh.storage.sqlite import SqliteStore


def test_store_roundtrip():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SqliteStore(path)
    try:
        store.upsert_device("d1", "激光器", "laser", "{}", "idle")
        rows = store.list_devices()
        assert any(r["device_id"] == "d1" for r in rows)
        store.insert_observation("d1", "read", {"channel": "temp"}, 25.5)
        obs = store.recent_observations()
        assert any(o["device_id"] == "d1" for o in obs)
    finally:
        store.close()
        if os.path.exists(path):
            os.remove(path)
