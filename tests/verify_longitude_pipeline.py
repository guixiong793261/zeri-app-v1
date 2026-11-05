# -*- coding: utf-8 -*-
"""经度透传回归验证：
1) longitude 缺省/None/120.0 三者结果必须逐字段一致（旧行为不变）；
2) 东经 104.1（成都）应触发真太阳时修正（结果或修正标记不同）；
3) 六副本关键文件归一化 SHA 收敛。
退出码 0=通过，1=失败。
"""
import sys, io, hashlib, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.四柱计算器 import calculate_sizhu

fails = []

# 1) 等价性：不传 / None / 120.0
d = date(2000, 1, 7)  # 跨节气边界附近，敏感
r0 = calculate_sizhu(d, 11, 30)
r1 = calculate_sizhu(d, 11, 30, longitude=None)
r2 = calculate_sizhu(d, 11, 30, longitude=120.0)
keys = ['年柱', '月柱', '日柱', '时柱']
for k in keys:
    if not (r0[k] == r1[k] == r2[k]):
        fails.append(f"等价性失败 {k}: {r0[k]}/{r1[k]}/{r2[k]}")
print(f"[1] 缺省/None/120.0 四柱: {[r0[k] for k in keys]}")

# 2) 真太阳时触发：成都 104.1，边界时刻选时柱交界（11:30 午未界）
r3 = calculate_sizhu(d, 11, 30, longitude=104.1)
diff = [k for k in keys if r3[k] != r0[k]]
print(f"[2] 104.1°E 四柱: {[r3[k] for k in keys]}  差异柱: {diff}")
# 注意：差异是否存在取决于边界距离；均时差+经度修正约 -72min，11:30-72min=10:18 应为 巳时（9-11）
if not diff:
    fails.append("真太阳时未生效：104.1°E 与 120°E 结果完全相同（11:30 边界应跨时辰）")

# 3) 六副本 SHA 归一化收敛
def norm_sha(p):
    with open(p, 'rb') as f:
        b = f.read().replace(b'\r\n', b'\n')
    return hashlib.sha256(b).hexdigest()[:16]

groups = [
    ("主程序", [r"主程序.py", r"手机一键部署\模块完整版\主程序.py"]),
    ("日课评分系统", [r"modules\日课评分系统.py", r"手机一键部署\模块完整版\modules\日课评分系统.py"]),
    ("八字排盘", [r"modules\八字排盘.py", r"手机一键部署\模块完整版\modules\八字排盘.py"]),
    ("八字排盘模块", [r"modules\八字排盘模块.py", r"手机一键部署\模块完整版\modules\八字排盘模块.py"]),
]
import os
base = os.path.dirname(os.path.abspath(__file__))
for name, paths in groups:
    shas = [norm_sha(os.path.join(base, '..', p)) for p in paths]
    ok = len(set(shas)) == 1
    print(f"[3] {name}: {'一致' if ok else '不一致!!'} {shas}")
    if not ok:
        fails.append(f"{name} 副本 SHA 不一致: {shas}")

if fails:
    print("FAILED:", *fails, sep='\n  ')
    sys.exit(1)
print("ALL_REGRESSION_OK")
sys.exit(0)
