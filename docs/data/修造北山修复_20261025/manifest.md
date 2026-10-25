# 修造北山修复 R1-R6 归档（2026-10-25）

- 主报告：docs/修造北山过度否决排查报告_20261025.md（commit 4a44dad，成稿即停待拍）
- 立项书：docs/修造北山过度否决排查_立项_20261025.md（commit 56fa57a）
- 本目录：修复前后对比快照 + 探针代码 + manifest（SEED/复现方法）

## 一、commit 链（主仓 main）

| Commit | 内容 |
|--------|------|
| `4a44dad` | 排查报告（只读取证，成稿即停） |
| `56fa57a` | 只读立项 |
| `86b5280` | R1：MOUNTAIN_CHONG 壬→午/癸→午 + 兼向静态权威不回退 + 回归测试 |
| `2eff32e` | R4+R2评分器：正体大凶移出硬煞词表；'冲山（'→'日冲山（' |
| `c9cfe7a` | R5：硬煞展示 [:3]→Top10+等N项（两处） |
| `b44f8d8` | R2：时冲山降级——Layer1 摘时柱 + Layer2 时冲山警告（分值挂 PENDING） |
| `4f05d24` | R3 立项书：月冲山专项只读对勘（本批收口后启动） |
| `f708663` | 部署副本统一同步（手机一键部署两份，SHA 一致） |

## 二、前后对比快照（2025 壬山丙向，12:00 午时，无事主）

| 指标 | 修复前 | 修复后 | 快照文件 |
|------|-------:|-------:|----------|
| check_mountain_day 层否决天次 | 331（年冲山恒否决）+ | **62**（年冲山 0，余日破31/月冲山31/日岁煞3） | probe_a.json |
| 评分器 feixing 非否决天次 | 1/365 | **94/365** | probe_b.json |
| 评分器 pure 非否决天次 | 13/365 | **171/365** | probe_b.json |
| veto 含「年冲山」条次 | 331→（探针B 155 条次，其余被 28 字符截断遮蔽） | **0** | probe_b.json |
| 正体大凶大忌条次 | 40+ | **0**（R4 恢复 §62 强扣分） | probe_b.json |
| 2026 壬/癸山 年冲山 | —（表错不触发） | **331**（岁破正确起例） | r1_verify.json |
| 兼向静态口径 | 被回退映射污染（兼亥巳忌午） | **不回退，静态权威**（兼亥巳忌巳） | r1_verify.json |

## 三、文件清单与复现

| 文件 | 用途 | 复现命令 |
|------|------|----------|
| beishan_probe_a.py | Layer1 check_mountain_day 逐日否决源统计（不截断 key） | `python beishan_probe_a.py` |
| probe_a.json | 探针A 输出（否决总天次/凶煞计数/年冲山出现日） | 自动生成 |
| beishan_probe_b.py | 评分器层完整 key 否决源统计（feixing/pure 双模式） | `python beishan_probe_b.py` |
| probe_b.json | 探针B 输出（非否决天次/TOP veto 计数） | 自动生成 |
| beishan_probe_r1_verify.py | R1 对拍：2025/2026 壬癸山年冲山 + 兼向回归矩阵 | `python beishan_probe_r1_verify.py` |
| r1_verify.json | 对拍输出 | 自动生成 |
| beishan_probe_r1_matrix.py | 24 山静态规则 vs 实际触发矩阵（兼向污染排查） | `python beishan_probe_r1_matrix.py` |
| beishan_probe_r2_hour.py | R2 时冲山降级：午时（壬对冲）警告入忌扣分链路 | `python beishan_probe_r2_hour.py` |
| r2_hour.json | 时冲山验证输出（命中日 2025-02-04 甲辰日庚午时） | 自动生成 |
| beishan_probe.py | 首探针（「89 天」伪影溯源起点） | `python beishan_probe.py` |

- SEED / 环境：Windows + Python 3.11；主仓路径 `d:\自编择日软件\专业级正五行择日软件`；
  探针统一 `sys.path.insert(0, ROOT)` 后导入 modules.*；sxtwl 节气口径（四柱计算器）。
- 修复前基线数字（331 恒否决 / 89 伪影 / 364 全灭）取自主报告 §二/§四 与立项书 §一，
  探针 A/B 于修复前运行过旧版（结果记录于报告），修复后运行版归档于此目录。

## 四、验证汇总（验收时 107/107 全绿）

- unittest：`python -m unittest discover -s tests -p "test_*.py"` → Ran 107 tests, OK
- 部署副本：手机一键部署两份 二十四山择吉天机.py + 评分器.py SHA256 与主仓一致（f708663）
- 统一版仓：专业择日大师_统一版/专业级正五行择日软件_v1.0 同两文件 4 位置 SHA256 一致（2f4c038）
