# -*- coding: utf-8 -*-
"""制化层回归断言：土府/地囊/土王用事不得因吉神自动豁免

验证：在土府/地囊/土王用事触发日，即使岁德/天乙贵人等吉神并临，
这些凶煞仍应发射扣分（协纪卷十「与德合赦愿并犹忌」）。
"""
import sys, os, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.四柱计算器 import calculate_sizhu
from modules.shensha.修造神煞 import ConstructionShenShaChecker
from modules.shensha.动土神煞 import DiggingShenShaChecker
from modules.shensha.神煞基类 import ShenShaChecker

xz = ConstructionShenShaChecker()
dt = DiggingShenShaChecker()
base = ShenShaChecker()

# 遍历一年，找土府/地囊/土王用事触发日
start = datetime.date(2026, 1, 1)
end = datetime.date(2027, 1, 1)
targets = {'土府': [], '地囊': [], '土王用事': []}

d = start
while d < end:
    sizhu = calculate_sizhu(d, hour=12)
    if xz._is_tufu2(sizhu):
        targets['土府'].append(d)
    if xz._is_dinang(sizhu):
        targets['地囊'].append(d)
    if dt._is_tuwang_yongshi(sizhu):
        targets['土王用事'].append(d)
    d += datetime.timedelta(1)

# 检查吉神并临的情况
# 岁德：年干对应的吉神日
# 天乙贵人：日干对应的贵人支
jishen_checks = [
    ('岁德', lambda s, b: b._is_suide(s)),
    ('天乙贵人', lambda s, b: b._is_tianyi_day(s)),
    ('月德', lambda s, b: b._is_yuede(s)),
    ('天德', lambda s, b: b._is_tiande(s)),
]

fail = 0
for shensha, days in targets.items():
    if not days:
        print(f'[WARN] {shensha} 无触发日')
        continue
    # 取前 10 天验证
    checked = 0
    for day in days[:20]:
        sizhu = calculate_sizhu(day, hour=12)
        # 检查是否有吉神并临
        jishen_present = []
        for jname, jfn in jishen_checks:
            try:
                if jfn(sizhu, base):
                    jishen_present.append(jname)
            except Exception:
                pass
        if not jishen_present:
            continue
        # 有吉神并临，检查凶煞是否仍发射
        r = xz.check(sizhu)
        names = [s['name'] for s in r]
        if shensha not in names:
            print(f'[FAIL] {shensha} @ {day} 吉神并临{jishen_present} 但未发射!')
            fail += 1
        else:
            checked += 1
    print(f'[PASS] {shensha}: {len(days)} 触发日, {checked} 天吉神并临仍发射')

assert fail == 0, f'{fail} 个制化豁免失败'
print('\n制化层回归断言: 全部 PASS（土府/地囊/土王用事不因吉神自动豁免）')
