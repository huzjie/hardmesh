# 贡献指南

感谢你对 hardmesh 的兴趣！

## 开发流程

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feat/xxx`
3. 提交改动（遵循约定式提交）
4. 推送并创建 Pull Request

## 质量要求

- 新增模块需通过 `python -m compileall -q hardmesh`
- 核心逻辑需补充单元测试
- 文档同步更新

## 代码风格

- 遵循 PEP 8
- 内核保持零第三方依赖
- 模块导出与 `__init__.py` 保持一致
