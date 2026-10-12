# -*- coding: utf-8 -*-
"""§68 阶段2 前置探测：作灶日五行分<30 且忌事含'灶君'的候选数。

归档自 C:\\Temp 一次性探针（§69 验收拍板A 执行时留档，可复用于
未来规则变化后的样例重扫）。定位已改为相对路径（§68 基建规范，
非 fixtures 豁免范围）。

口径：s64 verify 同款——Scorer().score(12:00, '作灶', OWNER1,
shan_xiang='坤山艮向兼未')。

## 首次探测结果（2026-10-12，HEAD=§66 后规则版本）
- 范围 2024-01-01 ~ 2026-12-31 共 1096 日
- 五行<30 且忌事含灶君：143 日（宽松口径）
- 其中 141 日被 veto 噪声淹没（总分0/veto≥1/he_ge=False）
- veto=0 且 he_ge=True（必修1 假低分回退实际生效）仅 2 日：
  - 2025-09-20  五行=-21  总分=-138  灶君忌日忌作灶   → s64 D2-4d 主样例
  - 2025-10-02  五行=10   总分=-112  灶君忌日忌作灶   → s64 D2-4e 备样例
- 结论：已补双断言（tests/verify_20261009_s64.py D2-4d/e）；两样例
  绑定 §66 后规则版本，规则变化后重跑本脚本验证样例有效性。
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # tools/audit/s68_stage2_probe/ → 仓根（3 层）
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer

OWNER1 = [{'name': '主', 'role': '事主', 'birth_date': '1972-01-08', '生肖': '亥'}]
KUN = '坤山艮向兼未'

sc = Scorer()
n_total = n_below30 = 0
hits = []
d = dt.date(2024, 1, 1)
while d <= dt.date(2026, 12, 31):
    sz = calculate_sizhu(d, 12, 0)
    sz['date'] = d; sz['year'] = d.year; sz['month'] = d.month; sz['day'] = d.day
    r = sc.score(sz, '作灶', owners=OWNER1, shan_xiang=KUN)
    n_total += 1
    _wx = r.get('wu_xing_result') or {}
    wxs = _wx.get('score')
    ji = [str(j) for j in (r.get('ji_list') or [])]
    if wxs is not None and wxs < 30:
        n_below30 += 1
        _zj = [j for j in ji if '灶君' in j]
        if _zj:
            hits.append((d.isoformat(), '五行=%s' % wxs, '总分=%s' % r.get('score'),
                         'he_ge=%s' % _wx.get('he_ge'),
                         'veto=%d' % len(r.get('veto_reasons') or []), _zj))
    d += dt.timedelta(days=1)

print('总日数=%d  五行<30=%d  且忌事含灶君=%d' % (n_total, n_below30, len(hits)))
for h in hits:
    print(' ', h)
