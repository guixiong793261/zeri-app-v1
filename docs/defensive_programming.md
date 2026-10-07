# 防御性编程规范

本项目实战中踩过的坑与对应规范。每条含"出错场景"与"正确做法"。

## 1. Python 常见陷阱

### 1.1 int 不可变 + setdefault 陷阱（2026-10-07 批次二事故）

**出错场景**：聚合统计时写
```python
m = masked.setdefault(key, 0)
m += 1   # ❌ 只重绑局部变量 m，字典里的值仍是 0
```

**正确做法**：
```python
masked[key] = masked.get(key, 0) + 1   # ✅ 写回字典
```

**教训**：聚合统计代码必须用一个已知案例实测校验输出再信结果。本次 bug 导致报表"叠加他凶=0 条"，而 TOP 表却列出 6 个兼向——数据自相矛盾才暴露。

### 1.2 list.append() 返回 None

**出错场景**：
```python
items = items.append(x)   # ❌ items 变成 None
```

**正确做法**：
```python
items.append(x)   # append 就地修改，返回 None，不要再赋值
```

### 1.3 dict.get() 默认值求值时机

`d.get(k, expensive())` 中默认值无论 key 是否存在都会先求值。昂贵默认用 `if k not in d` 或 `setdefault`（注意 1.1）。

## 2. 后台任务管理

### 2.1 toolhost 记录消失 ≠ 进程死亡（2026-10-07 双进程事故）

**出错场景**：TaskStop 报 "task not found" 后重启任务，结果 OS 进程其实还活着，双进程并发追加写同一 JSONL 结果文件，数据双写污染。

**正确做法**：
- 杀后台任务必须 **OS 层验证进程清零**（按 CommandLine 匹配），不能以 TaskStop 返回值为准；
- Windows: `Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'scan_12shichen'}`；
- 长跑脚本结果文件**先检查是否存在+行数是否符合预期**，存在则断点续跑而非追加覆盖。

## 3. 结构断言（拦截静默退化）

### 3.1 组合名必须是引擎可识别的真实值（2026-10-07 序号串事故）

**出错场景**：建组合清单时取错元组字段（`t[0]`序号而非`t[1]`山名），生成"1山13向"数字串，引擎无法识别，静默退化为纯日期通道——72 组合可用率一模一样，脚本不报错。

**正确做法**（启动期校验，写死在脚本里）：
```python
def validate_combos(combos):
    for c in combos:
        assert '山' in c, f'组合名不含"山"：{c}'
        assert c[0] in MOUNTAIN_RING, f'首字符非山名：{c}'
        # 与引擎解析单点往返校验
        p = parse_shan_xiang_jianxiang(c)
        assert p['主山'], f'引擎无法解析：{c}'
```

### 3.2 聚合后方差检测

```python
availabilities = [get_avail(c) for c in combos]
if len(set(availabilities)) == 1:
    raise RuntimeError('所有组合可用率完全相同，疑似组合名错误/静默退化')
if max(availabilities) - min(availabilities) < 0.001:
    raise RuntimeError('组合间差异过小，疑似数据退化')
```

### 3.3 逐组合计数（防 A 多 B 少错位）

不只校验总数，逐组合断言条数，防止"A 组合多 100 条、B 组合少 100 条，总数仍对但数据错位"。

## 4. 跨口径对比（批次二澄清教训）

比值/百分比必须**同口径**才能对比。对比前显式标注分子分母范围：

| 口径 | 示例 |
|------|------|
| 单组合 | 甲子×丙山 午时单课 |
| 多山合计 | 甲子×24 正向山 午时 |
| 日口径 | ≥1 时辰可用 |
| 时辰口径 | 单时辰可用 |

跨口径的比值（如"单组合午时" ÷ "多山日口径"）不成立，必须先换算到同一口径再求倍数。
