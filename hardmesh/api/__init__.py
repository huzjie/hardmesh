"""控制面 API：FastAPI 优先 + stdlib 兜底。"""
from hardmesh.api.app import create_app  # noqa: F401

__all__ = ["create_app"]
