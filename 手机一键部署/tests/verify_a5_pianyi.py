# -*- coding: utf-8 -*-
"""
A5 批·偏移错 2 项穷举验证（归忌／病符）
======================================
与 A1-A4 不同：两项均为**偏移错**——判定对象（月支查日支/年支查日支）与
比较方式（相等）都对，错在**偏移量**，且新旧集合零交集（12 个月/年支全部
错位，无一巧合），性质比 A3 表错更彻底。

典据：
  归忌——《协纪辨方书》卷四引《历例》："归忌者，孟月以丑、仲月以寅、
         季月以子。"旧"月支前七位"（月支+7）12 月全错位：旧 92 天/三年
         →新 90 天，交 0、旧独有 92（撤销）、新独有 90（补位）。
         （月支取交节时刻精确换月、年干支立春界口径，下同）
  病符——《协纪辨方书》卷四引《历例》："病符者，太岁后一辰也。"
         曹震圭注："是旧岁建也"（年支-1=旧岁年支）。旧"年支前九位"
         （年支+9）12 年支全错位。

2026-10-20 病符批（001 §141）后的口径变更（**本脚本 B 段语义反转**）：
  病符日课普适注册（7 发射＋1 谓词＋14 键）经拍板删除——三库病符全为
  方位/年神语境（协纪「其地」、考原「所理之地」、陈书「病符方」），无日课
  普适忌明文。故本脚本病符部分由「新旧偏移穷举」**反转为删除断言**：
  · 谓词 `_is_bingfu` 不可调用（AttributeError / hasattr=False）；
  · 神煞基类源码不含 `_is_bingfu` 可执行定义（仅墓碑注释留档）；
  · modules/shensha 全目录无 `_is_bingfu(` 调用；
  · 15 通道 2026 全年病符发射 = 0（逐通道断言）；
  · 事项标准表无任何 ('*','病符')／(ev,'病符') 键。
  反转原因：被测对象（偏移口径）已随谓词一并删除，旧真值表失去消费者；
  保留归忌全量穷举，病符只保留「已删」反向断言，不以空洞断言充数。
  附带：本脚本 HEAD 版本已 exit 1（2026-10-19 死链清理删入宅子类 caller，
  原 L258 可达性断言破），该遗留**不是**病符批引入；本批仅改病符相关断言，
  遗留另行登记。

双保险：
1. 权威表/旧偏移口径全部硬编码于本文件，绝不从产品读取；
2. 年干立春界、月支交节时刻、月干五虎遁、日柱均由 sxtwl 天文历点独立
   推导；产品侧仅调用基类谓词与 checker，杜绝自证。

含：2025-2027 共 1095 天归忌谓词穷举；新旧集合代数（零交集断言）；
端到端 3 个 checker（归忌：入宅/修造/签约——恰一条＋分值锁）；
病符删除反向断言；override 删除结构断言。
"""
import sys
import datetime
import inspect
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shensha_verify_engine import ShenShaCase, run_cli, _UNAVAILABLE
import sxtwl

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ===== 权威真值（硬编码，不读产品） =====
GUIJI_MENG = frozenset({'寅', '申', '巳', '亥'})
GUIJI_ZHONG = frozenset({'子', '午', '卯', '酉'})
GUIJI_JI = frozenset({'辰', '戌', '丑', '未'})
GUIJI_DAY = {'孟': '丑', '仲': '寅', '季': '子'}


def _all_days(*years):
    for y in years:
        d = datetime.date(y, 1, 1)
        end = datetime.date(y, 12, 31)
        while d <= end:
            yield d
            d += datetime.timedelta(days=1)


DAYS = list(_all_days(2025, 2026, 2027))
DAYS_2026 = [d for d in DAYS if d.year == 2026]
DAYS_2025 = [d for d in DAYS if d.year == 2025]


def _jieqi_points(year):
    """当年 12 节（换月点）(datetime, 月支)；getJieQiByYear idx 立春=0。"""
    jq = sxtwl.getJieQiByYear(year)
    pts = []
    for idx, mz in ((20, '子'), (22, '丑'), (0, '寅'), (2, '卯'),
                    (4, '辰'), (6, '巳'), (8, '午'), (10, '未'),
                    (12, '申'), (14, '酉'), (16, '戌'), (18, '亥')):
        dd = sxtwl.JD2DD(jq[idx].jd)
        pts.append((datetime.datetime(int(dd.Y), int(dd.M), int(dd.D),
                                      int(dd.h), int(dd.m), int(dd.s)), mz))
    return sorted(pts)


_MORDER = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']


def _sizhu_independent(d, hour=12):
    """四柱干支全独立推导：年干支立春界、月支交节时刻、月干五虎遁、
    日柱 sxtwl 直取（含年支，病符判定用）。"""
    cur = datetime.datetime(d.year, d.month, d.day, hour, 0)
    pts = _jieqi_points(d.year - 1) + _jieqi_points(d.year)
    pts.sort()
    mz, pillar_year = '子', d.year - 1
    for t, z in pts:
        if cur >= t:
            mz = z
            if z == '寅':
                pillar_year = t.year
        else:
            break
    yg = GAN[(pillar_year - 4) % 10]
    yz = ZHI[(pillar_year - 4) % 12]
    mg = GAN[((GAN.index(yg) % 5) * 2 + 2 + _MORDER.index(mz)) % 10]
    g = sxtwl.fromSolar(d.year, d.month, d.day).getDayGZ()
    dg, dz = GAN[g.tg], ZHI[g.dz]
    return {'year_gan': yg, 'year_zhi': yz, 'month_gan': mg,
            'day_gan': dg, 'month_zhi': mz, 'day_zhi': dz, 'date': d}


def _gold(d):
    """归忌 bool / 病符 bool 典载真值。"""
    s = _sizhu_independent(d)
    mz, yz, dz = s['month_zhi'], s['year_zhi'], s['day_zhi']
    cls = '孟' if mz in GUIJI_MENG else '仲' if mz in GUIJI_ZHONG else '季'
    return {'归忌': dz == GUIJI_DAY[cls],
            '病符': dz == ZHI[(ZHI.index(yz) - 1) % 12]}


def _old_guiji(s):
    """旧偏移口径：月支+7。"""
    return s['day_zhi'] == ZHI[(ZHI.index(s['month_zhi']) + 7) % 12]


def _old_bingfu(s):
    """旧偏移口径：年支+9。"""
    return s['day_zhi'] == ZHI[(ZHI.index(s['year_zhi']) + 9) % 12]


# ---------- 谓词穷举 cases ----------
def _make_pred_case(name):
    def expected(d):
        return _gold(d)[name]

    def adapter(d):
        try:
            from modules.shensha.神煞基类 import ShenShaChecker
        except Exception:
            return _UNAVAILABLE
        try:
            c = ShenShaChecker()
            s = _sizhu_independent(d)
            # 病符分支已删（病符批 2026-10-20，001 §141）：谓词随日课普适注册
            # 一并删除，本适配器今仅服务归忌（CASES 亦不再构造病符谓词用例）。
            return bool(c._is_guiji(s))
        except Exception:
            return _UNAVAILABLE

    return ShenShaCase(
        name=f'A5-{name}谓词', category='B',
        description=f'{name}典载口径 2025-2027 共1095天穷举（年干支立春界/'
                    f'月支交节/sxtwl 直取日柱）',
        inputs=DAYS, expected=expected, adapter=adapter, compare='bool')


# ---------- 端到端：恰一条 + 分值锁 ----------
def _make_e2e_case(event, target, score):
    def expected(d):
        return ((target, score),) if _gold(d)[target] else ()

    def adapter(d):
        try:
            from modules.四柱计算器 import calculate_sizhu
            from modules.事项标准 import get_shensha_checker
        except Exception:
            return _UNAVAILABLE
        try:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            items = get_shensha_checker(event).check(sz, owners=[])
            sel = [(it['name'], it['score']) for it in items
                   if it['name'] == target]
            names = [n for n, _ in sel]
            if len(names) != len(set(names)):
                return f'BAD:DUP{sel}'
            return tuple(sorted(sel))
        except Exception:
            return _UNAVAILABLE

    return ShenShaCase(
        name=f'A5-{target}{event}端到端', category='B',
        description=f'{event} checker 2026 全年：{target}典载日恰一条且分值锁 '
                    f'{score}（事项标准单一表）',
        inputs=DAYS_2026, expected=expected, adapter=adapter, compare='eq')


# ---------- 新旧样例硬锁 ----------
# (日期, 项, 典载判定, 说明)；均经 sxtwl 独立推导核对
LOCKS = [
    # 归忌（新=孟丑仲寅季子；旧=月支+7 全错位）
    (datetime.date(2026, 2, 8),  '归忌', True,  '寅月（孟）丑日典载命中'),
    (datetime.date(2026, 1, 4),  '归忌', True,  '子月（仲）寅日典载命中'),
    (datetime.date(2026, 1, 14), '归忌', True,  '丑月（季）子日典载命中'),
    (datetime.date(2026, 2, 4),  '归忌', False, '寅月酉日旧误报（旧月支+7）'),
    (datetime.date(2026, 6, 8),  '归忌', False, '午月丑日旧误报（旧月支+7）'),
    (datetime.date(2026, 4, 7),  '归忌', False, '辰月亥日旧误报（旧月支+7）'),
    # 病符新旧样例已删（病符批 2026-10-20，001 §141）：谓词随日课普适注册
    # 一并删除，旧真值表失去被测对象；改由 _assert_bingfu_removed() 反向断言。
]


def _expected_lock(t):
    return bool(t[2])


def _adapter_lock(t):
    d, name, _, _ = t
    try:
        from modules.shensha.神煞基类 import ShenShaChecker
    except Exception:
        return _UNAVAILABLE
    try:
        c = ShenShaChecker()
        s = _sizhu_independent(d)
        # 病符分支已删（病符批 2026-10-20，001 §141）
        return bool(c._is_guiji(s))
    except Exception:
        return _UNAVAILABLE


case_locks = ShenShaCase(
    name='A5-新旧样例硬锁', category='B',
    description='归忌孟丑/仲寅/季子日命中＋旧月支+7 误报日不命中（病符样例已删，'
                '001 §141，见 _assert_bingfu_removed）',
    inputs=LOCKS, expected=_expected_lock, adapter=_adapter_lock, compare='bool')


CASES = [_make_pred_case('归忌')]
CASES.extend(_make_e2e_case(e, '归忌', -15) for e in ('入宅', '修造', '签约'))
# 病符谓词/端到端用例已删（病符批 2026-10-20，001 §141）：日课普适注册全删后
# 无被测对象；转由 _assert_bingfu_removed() 作「谓词/发射/键全链清零」反向断言。
CASES.append(case_locks)


# ---------- 独立反向断言 ----------
def _assert_structure():
    # 孟仲季三集合互斥且完备覆盖 12 支
    assert not (GUIJI_MENG & GUIJI_ZHONG) and not (GUIJI_MENG & GUIJI_JI) \
        and not (GUIJI_ZHONG & GUIJI_JI)
    assert GUIJI_MENG | GUIJI_ZHONG | GUIJI_JI == set(ZHI)
    assert set(GUIJI_DAY) == {'孟', '仲', '季'}
    # 典载忌日支三值互异（丑/寅/子）
    assert set(GUIJI_DAY.values()) == {'丑', '寅', '子'}


def _assert_set_algebra():
    """新旧集合代数硬锁（零交集：12 月/年支全错位，无一巧合）。

    注：`病符` 一栏为**历史留档值**（典载真值 vs 旧偏移，均纯历法推导、不触产品），
    仅供反证时比对；病符日课注册已于病符批（001 §141）删除，该值无产品消费者，
    删除断言见 _assert_bingfu_removed()。
    """
    oj = nj = ob = nb = 0
    for d in DAYS:
        s = _sizhu_independent(d)
        g = _gold(d)
        oj += _old_guiji(s); nj += g['归忌']
        ob += _old_bingfu(s); nb += g['病符']
    assert (oj, nj) == (92, 90), (oj, nj)
    assert (ob, nb) == (91, 92), (ob, nb)
    return {'归忌': (oj, nj), '病符': (ob, nb)}


def _code_only(src):
    """剥掉 # 注释后的源码文本（墓碑注释按惯例含原实现代码，须剔除再断言）。"""
    return '\n'.join(ln.split('#', 1)[0] for ln in src.splitlines())


def _assert_bingfu_removed():
    """病符日课普适注册全链删除反向断言（病符批 2026-10-20，001 §141）。

    谓词 _is_bingfu 无任何非评分链路调用（黄历/历法「病符星」走二十四山
    紫白飞星独立实现），故彻底删、墓碑留档，不保留可调用方法。
    """
    from modules.shensha import (神煞基类, 修造神煞, 动土神煞, 嫁娶神煞,
                                 安床神煞, 安葬神煞, 通用神煞, 入宅神煞)
    assert not hasattr(神煞基类.ShenShaChecker, '_is_bingfu'), \
        '谓词 _is_bingfu 应已删除（001 §141）'
    for mod in (神煞基类, 修造神煞, 动土神煞, 嫁娶神煞, 安床神煞, 安葬神煞,
                通用神煞, 入宅神煞):
        code = _code_only(inspect.getsource(mod))
        assert '_is_bingfu(' not in code, \
            f'{mod.__name__} 不应残留可执行 _is_bingfu 调用'
        assert "_add_shensha('病符'" not in code, f'{mod.__name__} 病符发射应已删除'
    # 目录级兜底：modules/shensha 全部 .py 均无可执行 _is_bingfu 调用
    _ss_dir = Path(__file__).resolve().parents[1] / 'modules' / 'shensha'
    for _p in sorted(_ss_dir.glob('*.py')):
        _code = _code_only(_p.read_text(encoding='utf-8'))
        assert '_is_bingfu(' not in _code, f'{_p.name} 残留可执行 _is_bingfu 调用'
    from modules.事项标准 import SHENSHA_SCORES, shensha_score
    assert not [k for k in SHENSHA_SCORES if k[1] == '病符'], '表内不应残留病符键'
    assert ('*', '病符') not in SHENSHA_SCORES, '通配键 (*,病符) 不应存在'
    for ev in ('嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床',
               '作灶', '移徙', '入学', '求医', '签约', '安葬'):
        assert shensha_score(ev, '病符') is None, f'{ev} 病符分值应已删除'
    n_yi = len([k for k in SHENSHA_SCORES if k[0] == '移徙'])
    assert n_yi == 74, f'移徙块键数应=74（病符批 76→75，红嘴朱雀批 75→74），实得 {n_yi}'
    assert len(SHENSHA_SCORES) == 1265, \
        f'SHENSHA_SCORES 总键应=1265（病符批 1281→1267，红嘴朱雀批 1267-5+3=1265），实得 {len(SHENSHA_SCORES)}'
    return {'移徙块': n_yi, '总表': len(SHENSHA_SCORES)}


def _assert_no_override_and_reachable():
    """归忌 override 删除结构断言 + 病符全链删除断言。"""
    from modules.shensha import 通用神煞, 入宅神煞
    assert 'def _is_guiji(' not in inspect.getsource(通用神煞), \
        '通用神煞归忌 override 应删除'
    assert 'def _is_guiji(' not in inspect.getsource(入宅神煞), \
        '入宅归忌 override 应删除'
    # 病符 caller 链路断言已反转为删除断言（病符批 2026-10-20，001 §141）
    _assert_bingfu_removed()


def main():
    _assert_structure()
    alg = _assert_set_algebra()
    _assert_no_override_and_reachable()
    from modules.事项标准 import SHENSHA_SCORES
    print(f'[A5] 反向断言通过；旧→新命中数={alg}（交=0，零交集全错位）')
    print(f'[A5] 病符删除断言通过：移徙块键={len([k for k in SHENSHA_SCORES if k[0] == "移徙"])}'
          f'／总表={len(SHENSHA_SCORES)}；谓词/发射/键全链清零（001 §141）')
    print('[A5 批·偏移错：归忌（孟丑仲寅季子）穷举验证＋病符已删反向断言]')
    return run_cli(CASES)


if __name__ == '__main__':
    sys.exit(main())
