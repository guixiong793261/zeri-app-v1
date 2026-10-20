# 重出与回扫归档清单（2026-10-20）

复现命令（主仓根执行，`$env:PYTHONIOENCODING='utf-8'`）：

```powershell
# 1) 新旧基线四日全网格（15 事项 × 12 时辰）
python sweep4.py "d:\自编择日软件\专业级正五行择日软件" sw_new.csv
python sweep4.py "<旧基线 git worktree：8b9bbb6>"        sw_old.csv

# 2) 四日 12:00 等级
python lv4.py "d:\自编择日软件\专业级正五行择日软件" > lv_new.txt
python lv4.py "<旧基线>"                              > lv_old.txt

# 3) 全年回扫（365 × 15 = 5475 格）
python sweep_year.py "d:\自编择日软件\专业级正五行择日软件" yr_new.csv
python sweep_year.py "<旧基线>"                              yr_old.csv

# 4) 汇总与归因
python sum_year2.py      # 读 C:\Temp\yr_old.csv / yr_new.csv -> yr_final.json
python diff4.py          # 读 sw_*.csv + lv_*.txt -> diff4.json
python att4.py           # 四日条目级分值差
```

- 旧基线复算方式：`git worktree add <dir> 8b9bbb6`（只读，不改主仓）。
- `probe_cmp.py` 为单点四日明细探针（入宅），保留作抽查用。
- `sw_*.csv` 为四日 720 格原始明细；全年 5475 格 CSV 体积较大未入库，按上述命令可 1:1 重生成（耗时约 2 分钟/端）。

## 文件 SHA256（前 16 位）

| 文件 | SHA256 |
|---|---|
| att4.py | 6057944db35d2637 |
| diff4.json | bf5d049e4495ef8e |
| diff4.py | 06b7430ed8f80144 |
| lv4.py | afc695d10aeb1804 |
| probe_cmp.py | 76b4d4d8d924add1 |
| sum_year2.py | 5f2667dc2f008536 |
| sweep4.py | b07e7705234534ed |
| sweep_year.py | cf16ae8da0b4038e |
| sw_new.csv | cc4d16e01209a745 |
| sw_old.csv | bc4153612b79c24b |
| yr_final.json | 368ea35f92662af6 |
| yr_summary.json | a7f4bbd4b046e64c |

## 结果摘要

- 四日 720 格：总分净变 **+5280**（11-04 +1920、10-23 +2280、07-24 −216、06-01 +1296）。
- 全年 5475 格：变更 2389，口径内（排除归零）1938；跨档 825（口径内 756，升 682／降 74）；口径内 Δ 合计 **+41 486**。
- 归因：土符 +3840、红嘴朱雀 +1152、大时 +576、土王用事 −648（四日）；全年十恶大败 846→0、岁破 248→0、病符 421→0、大煞 352→0、四击 251→0。
