# 建除层专项·批次 1 任务清单

## 阶段 0：基线固化（改码前）
- [x] T0-A 在 `docs/data/建除层专项_批次1_20261022/` 新建 `probe_channel_totals.py`（15 通道 × 2026 全年总分、建除天次、开业破日/月破共现、四通道小黄道凶星天数），输出 `t0_before.json`。
- [x] T0-B 记录 6 路 144 格与 365 天等值基线 `t0_grid.json`。

## 阶段 1：Commit A（T7 单一事实源 + 六路委托）
- [x] A1 新建 `modules/建除.py`：`ZHI_ORDER/STARS/JIXIONG/JI_STARS/XIONG_STARS/star/star_by_sizhu/is_jianchu/is_jianchu_date` + 导入自检。
- [x] A2 `modules/黄道.py` `_calculate_xiao_huang_dao` 改委托，保留 `未知` 兜底与 `XIAO_HUANG_DAO` 分数字典。
- [x] A3 `modules/今日黄历.py` `calc_jianchu` 改委托，`JIANCHU_NAMES = list(STARS)`。
- [x] A4 `modules/shensha/marriage_shensha.py` `get_jianchu` 保留月支优先级/农历回退，末段改 `star`。
- [x] A5 `modules/shensha/通用神煞.py` `_get_xiao_huangdao` 改委托。
- [x] A6 `modules/shensha/修造神煞扩展.py` `_check_jianchu` 计算体改 `star`，四档分值原样。
- [x] A7 `modules/rules/修造规则.py`、`作灶规则.py`、`安葬规则.py` 三处 `fallback_get_jianchu` 仅改 offset 计算。
- [x] A8 跑 T0 网格等值探针（144×6、365 天、哨兵 224），全等后 commit A。→ `749569b`
- [x] A9 `git commit`：`refactor(建除): 新建建除单一事实源并六路委托（行为等价）`。

## 阶段 2：Commit B（伪谓词 + 双计）
- [x] B1 `开业神煞.py`：`_is_manri/_is_chengri/_is_biari/_is_pori` 改 `is_jianchu`。
- [x] B2 删除破日发射块（L167-169）与 `('开业','破日')` 键。
- [x] B3 探针：2026 年开业 365 天星名 0 错；31 破日扣分 -30；无「月破+破日」共现。
- [x] B4 `git commit`：`fix(开业): 建除谓词改单一事实源并消除破日月破双计`。→ `8ccc328`

## 阶段 3：Commit C（倒挂修复）
- [x] C1 `通用神煞.py` 发射：吉星 +8 / 凶星 0（保留展示与说明）。
- [x] C2 `事项标准.py` 36 键中 18 个凶星键改 0；`SHENSHA_WEIGHT_PENDING` 登记 6 个凶星名。
- [x] C3 探针：4 通道凶星日 0 分、吉星日 8 分；763 天次倒挂清零。
- [x] C4 `git commit`：`fix(建除): 小黄道凶星停发吉分（倒挂清零，分值挂待证）`。→ `a32a9f8`

## 阶段 3.5：Commit E（测试重冻 / 锚点同步，新增）
- [x] E1 键数 1200→1199 同步四份断言（a5/hzzq/shousi/岁破）。
- [x] E2 `verify_shousi` [H] 五通道基线实测重冻（开业 6936／通用 8201／入学 9038／求医 7736／签约 8186）。
- [x] E3 `评分器.H1_ANCHOR_MAP` 删 `('破日','建除破日忌开业')`（40→39），测试侧清单同步。
- [x] E4 既有失败隔离：`verify_alpha_piaoyi` 入宅/移徙月破键在改前 worktree 同样 FAIL，计入 H2。
- [x] E5 `git commit`：`test(建除): 重冻键数与通道基线并同步开业破日锚点`。→ `ce7e270`

## 阶段 4：Commit D（验证/快照/记账）
- [x] D1 新建 `tests/verify_建除层_批次1.py`（23 项断言，退出码 0/1）→ 23/23 PASS。
- [x] D2 跑全量回归四件套（test_core 27／test_business_logic 20／test_integration 52／test_huangdao_truth 35）全绿。
- [x] D3 重跑 `probe_channel_totals.py` → `t1_after.json`，生成 `docs/建除层专项_批次1_影响面快照_20261022.md`（逐通道 Δ）。
- [x] D4 `docs/问题跟踪_001_test_huangdao_truth七项历史失败.md` 追加 `## §161`。
- [x] D5 `git commit`：`test(建除): 批次1 验证脚本与影响面快照`。
- [x] D6 停下报告：commit 列表、verify 退出码、回归结果、快照摘要；六副本待批次 2 统一重建。

## 验收门禁
- [x] 144 格 × 6 路零差异、365 天零差异（阶段 1 后）。
- [x] 哨兵 2026-11-04 入宅 12:00 == 224/上吉（全程）。
- [x] 开业伪谓词 0 错、破日无 -50（阶段 2 后）。
- [x] 4 通道 763 天次倒挂清零（阶段 3 后）。
- [x] verify 退出码 0，含 ≥4 条反向断言（实为 7 条）。
