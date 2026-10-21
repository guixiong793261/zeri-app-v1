# 归档清单 · 下半场第一批只读盘点（2026-10-21）

## 1. 文件与校验值

| 文件 | 大小 | SHA256 |
|------|------|--------|
| `probe_hou3ceng.py` | — | `D2AAA38E8E9979B6568C57AF45D2D7B9E48BBD17F388317893F0CC2868C91876` |
| `hou3ceng_2026.json` | 118 445 B | `C2571F0FD04927159FF45C1D89546982A10DF1FE145126647E9BA5B577497D3D` |

## 2. 口径

- 时间窗：2026-01-01 ~ 2026-12-31，共 365 天
- 时柱：10:00（与 §144 受死日、§147 红嘴朱雀等批一致）
- 事项：15 通道 `入宅/移徙/嫁娶/动土/修造/拆舍/出行/开业/安床/作灶/安葬/入学/求医/签约/通用`
- 取分：`modules.shensha.get_checker(ev).check(sizhu, [])`，取 `name`/`score`/`description`
- 登记判定：`SHENSHA_SCORES` 三级查找（原事项 → `canonical_event` → 通配 `*`）
- 格数：365 × 15 = 5 475 格；实测神煞种类 184
- 性质：**只读**，不改任何生产文件、注册、分值、判据

## 3. 复现

```powershell
cd d:\自编择日软件\专业级正五行择日软件
python "docs\data\下半场盘点_20261021\probe_hou3ceng.py" --json "docs\data\下半场盘点_20261021\hou3ceng_2026.json"
```

退出码 0 = 正常，1 = 异常（含 traceback）。

## 4. JSON 结构

- `meta`：年/时/事项/天数/格数
- `rank`：每神煞 `{ct 天次, days 天数, evs 事项集合, scores 分值集合, abs 绝对分合计, net 净分}`
- `candidates`：候选神煞 `{days, ct, reg 注册键, act 实发, only_reg 注册未发射, only_act_unregistered 发射未注册}`
- `coverage`：每事项 `{kinds, unreg_kinds, unreg_ct, unreg_abs, unreg 明细}`
- `unregistered_total`：全部未登记神煞汇总

## 5. 与稿件数字的核对

稿件（`docs/下半场第一批_已验表源神煞后三层只读盘点_20261021.md`）所有表格数字
均按本 JSON 逐项机核（23 项主表 + 24 项候选），发现并修正 3 处（劫煞/灾煞/岁煞
事项数、三煞性质判定、通用未登记拆分），终稿与 JSON 一致。
