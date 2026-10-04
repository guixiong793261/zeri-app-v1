# 仙命 × 坐山判定 fixture（第二阶段 2.3）

安葬路径 **仙命（亡命）纳音五行 × 坐山正五行** 生克判定的数据驱动回归锚点。
格式定义见 [_schema.json](./_schema.json)；执行入口为
`tests/verify_wangming_shanzuo.py` 的 §F 段。

## 目录结构

```
wangming_shanzuo/
├── README.md            # 本文件：基线管理规则
├── _schema.json         # fixture 格式 v1（含完整示例）
├── basic/               # 基本组合矩阵（2.1：25 组）
├── boundary/            # 边界案例（2.1：比和、方向反转 2 组）
└── integration/         # 叠加场景（叠忌/无制化/有制化/双凶）
```

## 断言规则

### 断言层选择

- 仅 `wangming_nayin_wuxing` + `shanzuo_wuxing`（无日期）→ **只跑纯函数断言**；
- 另含 `date` + `wangming_birth_date`（`event` 默认安葬）→ **追加集成断言**
  （basic/boundary 同样适用——2.1 的 27 组本就是集成验证）；
- `category=integration` → **强制要求** `date` / `wangming_birth_date` /
  `event` 字段（_schema.json if/then 约束）。

### 每条用例的断言内容

1. **纯函数断言**（必有）：`evaluate_wangming_vs_shanzuo()` 的
   `relation / score / level` 与 expected 一致，`reason` 含全部
   `reason_contains` 关键词（包含即可，不全文匹配）。
2. **集成断言**（`input.date` 与 `input.wangming_birth_date` 均存在时）：
   以午时正午调评分器，校验：
   - `veto`：veto_reasons 是否非空；
   - `level_cap`：封顶是否实际生效（严格判定：坐山克仙命 + 无否决 +
     final_score≥60 但等级仍凶；自然低分凶不算封顶）；
   - `report_level` / `final_score`：填写时精确匹配（漂移立即可见）。
   - basic/boundary 案例只要带日期同样跑集成，覆盖不降级。

## 基线更新规则

1. 规则/代码变更后，先跑 `python tests/verify_wangming_shanzuo.py`。
2. 失败案例先归类，再处理：
   - **A 类：规则有意变更** → 更新该 fixture 的 expected 后提交，
     commit message 必须注明口径出处与变更原因；
   - **B 类：规则误变更（bug）** → 修代码，不改 fixture。
3. 新增案例按 _schema.json v1 格式归档；`notes` 仅供人工复查，不参与断言。
4. 每次提交后跑全量确认 **0 漂移**；fixture 与内联断言并存期间，
   两者必须同时通过。
5. 禁止为让用例通过而修改 expected 迁就实现——expected 只在 A 类
   有意变更时修改。

## 命名规范

- 基础：`{三位序号}_{亡命干支拼音}_{坐山拼音}.json`
  例：`001_jiazi_jiashan.json`
- 边界：`{类型}_{描述}.json`
  例：`bihe_jin_jin.json`、`fangxiang_fanzhuan.json`
- 集成：`{场景}_{描述}.json`
  例：`diesha_zhenchong.json`、`shanzuoke_wuzhihua.json`
