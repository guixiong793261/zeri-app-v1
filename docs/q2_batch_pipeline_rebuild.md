# Q2 批量审查管线重建说明

> 2026-10-08 拍板：批量管线脚本（原 C:\Temp 四件套）已清理不重建。
> 本文档记录管线结构与复现方法，作为未来重建的唯一依据。
> 审查产物已归档入库：审查结果/（manifest / owners / 35 样本渲染文本 / audits / 汇总 / _round1 备份）。

## 1. 管线入口与调用链

```
manifest.json + owners.json          （抽样定义，已入库：审查结果/_batch/）
      │
      ▼
① render  渲染：逐样本调沙箱生成日课详情文本
      │   产物：审查结果/_batch/samples/NN_事项_日期.txt（35 份，已入库）
      ▼
② audit   审查：对每份渲染文本跑独立重推对账
      │   产物：审查结果/_batch/audits.json（已入库）
      ▼
③ aggregate 汇总：按严重度/类型聚类
          产物：审查结果/summary.md、coverage.md、issues_pending.md、
                by_severity/{critical,major,minor}.md、by_event/*/review_*.md
```

首轮（110 问题版）完整备份在 审查结果/_round1/。

## 2. 依赖的沙箱模块与注入方式

渲染依赖 **zeri-detail-sandbox** 技能（.trae/skills/zeri-detail-sandbox/scripts/run_detail_sandbox.py，
不进版本控制，随工作区迁移）：

- **真实主程序加载**：`importlib.util.spec_from_file_location('_zeri_sandbox_main', 主程序.py)` 后 exec，
  使沙箱渲染走产品真实渲染管线（情况 C），非模拟文本。
- **content 块提取**：`extract_content_block` 从主程序源码提取 `content = f"""` 到
  `text.insert` 之间的块，包装成 `_build(...)` 函数执行。
  **关键约束**：块外局部变量在沙箱内不可见（如 sansha_info 须传 `{}`），
  块内一律用 `detail.get(...)` 取值。
- **事主构建**：`build_owners` 把审查 owners.json 原始格式规范化为 GUI 格式，
  并用 `calculate_xishen_yongshen` 预计算喜用神注入（否则相主/喜用段与真实管线不一致）。
- **时柱授权**：`_auth_sizhu` 调 `resolve_recommended_hour(sz, event, norm_owners, shan)`，
  仅当时柱支 == best_zhi 时置 True——保证"系统择定推荐时柱"标注与真实择优一致。

审查（audit）侧为独立重推模块，不调用产品评分函数，自行重算：
四柱（sxtwl）、神煞净分、五行恒等式、月令拆分、喜用合计、生肖相主、
评级阈值、时辰表，再与渲染文本对账。

## 3. 抽样参数（manifest.json 已入库）

| 参数 | 值 |
|------|-----|
| SEED | 20261007 |
| 日期池 | 2024-01-01 ~ 2026-12-31 |
| 事项数 | 13 |
| 每事项候选日 | 30 |
| 每事项抽取 | 3（不足则全取并记 shortage） |
| 山向 | 坤山艮向兼未 |
| 时辰 | 偶数时辰 |
| 事主 | owners.json 4 人（name 全空、role=事主1..4，年柱：辛亥/辛亥/甲戌/戊寅） |

## 4. 如何复现 35 样本

1. 读 `审查结果/_batch/manifest.json` 的 samples 列表——**样本已固定**，
   复现渲染不需要重新抽样，直接按 (event, date, hour) 逐条渲染即可。
2. 若要重新抽样：用 SEED=20261007 对日期池按"每事项 30 候选、随机抽 3"
   重跑抽样器，结果应与 manifest 完全一致（种子可复现）。
3. 每样本渲染输出应与 `审查结果/_batch/samples/NN_*.txt` 逐字一致
   （评分口径未变的前提下；若产品代码演进导致差异，差异本身即审查对象）。

## 5. 为什么脚本本身不入库

- 管线四件套（render/audit/aggregate/compare）依赖上述沙箱技能与即时口径，
  脱离沙箱无法独立运行，边际价值有限；
- 结果可验证性由 SEED + manifest + 已归档渲染文本保证，不依赖脚本存续；
- 重建成本高于收益。若未来确需重跑批量审查，按本文 §1-§3 重写约半日工作量。
