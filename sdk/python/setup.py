"""hardmesh SDK 打包配置。"""
from setuptools import setup, find_packages

setup(
    name="hardmesh-sdk",
    version="0.1.0",
    description="hardmesh 控制面 Python SDK",
    packages=find_packages(),
    python_requires=">=3.9",
)
