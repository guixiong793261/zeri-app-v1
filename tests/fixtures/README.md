# tests/fixtures 说明

## 关于 fixtures 中的 _verify_*.py

- 这些是历史研究的一次性探针，归档时保持原始上下文
- 硬编码路径（`root = r'd:\...'`）是当时的实际写法，**有意保留、非漏改**（§68 拍板豁免，2026-10-12）
- 它们不参与回归与对拍，仅作研究记录
- 新增的 verify 请一律使用 `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` 定位仓根（参见 references/verify_template.py）
