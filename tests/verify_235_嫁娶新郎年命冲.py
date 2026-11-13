# -*- coding: utf-8 -*-
"""001 §235 嫁娶通道相主硬门槛：日支冲新郎年命一票否决（方案C）。

背景：修复前嫁娶通道只判「日支冲新娘生肖」与「日支冲事主日支」，
日支冲【新郎生肖】完全未判 —— 2026-08-26 壬申日（冲新郎寅）被评为上吉。

A. 增量拦截：申日（冲新郎寅）→ 0 分否决，veto 含新郎
B. 对称闭环：酉日（冲新娘卯）→ 0 分否决，veto 含新娘
C. 反向断言：无关日不否决，分数正常
D. 单事主（仅新郎）同样拦截，不依赖双事主顺序
E. 相主明细：score_details 含相主得分/相主详情/[硬性门槛] 文案
F. 总分口径不变：非否决日 总分 == 嫁娶评分+月令+喜用神+太阳太阴
G. 通用通道不受影响：同日开业仍非 0 分
H. 源码锚点：防回退（评分器婚嫁分支调用统一硬门槛；婚嫁算法含新郎对称判定）
"""
import io
import os
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

FAILS = []


def check(cond, label, detail=''):
    print('  [%s] %s%s' % ('PASS' if cond else 'FAIL', label,
                          ('  | ' + str(detail)) if detail else ''))
    if not cond:
        FAILS.append(label)


def _sz(y, m, d, h=12):
    r = calculate_sizhu((y, m, d), h, 0, longitude=120)
    r['year'], r['month'], r['day'] = y, m, d
    return r


BRIDE = {'name': '新娘', 'role': '新娘', 'year_sx': '兔',
         'sizhu': '己卯 丁卯 丁亥 癸卯'}
GROOM = {'name': '新郎', 'role': '新郎', 'year_sx': '虎',
         'sizhu': '戊寅 壬戌 癸巳 壬子'}


def _score(y, m, d, owners, ev='嫁娶'):
    return calculate_score(_sz(y, m, d), ev,
                           owners=[dict(o) for o in owners], zeli_mode='pure')


# ==================== A. 增量拦截：申日冲新郎寅 ====================
def test_groom_chong():
    print('\n[A] 2026-08-26 壬申日 × 新郎虎 → 一票否决')
    r = _score(2026, 8, 26, [BRIDE, GROOM])
    vr = '；'.join(str(v) for v in (r.get('veto_reasons') or []))
    check(int(r.get('score') or 0) == 0, '得分强制归零', r.get('score'))
    check('凶' in str(r.get('level') or ''), '等级为凶', r.get('level'))
    check(bool(vr), '存在否决原因', vr)
    check('新郎' in vr, '否决原因点名新郎', vr)
    check(('申' in vr) and ('寅' in vr), '否决原因含 申→寅 冲', vr)


# ==================== B. 对称闭环：酉日冲新娘卯 ====================
def test_bride_symmetry():
    print('\n[B] 2026-09-08 丁酉日 × 新娘兔 → 仍否决（对称性未回退）')
    r = _score(2026, 9, 8, [BRIDE, GROOM])
    vr = '；'.join(str(v) for v in (r.get('veto_reasons') or []))
    check(int(r.get('score') or 0) == 0, '得分归零', r.get('score'))
    check('新娘' in vr, '否决原因点名新娘', vr)


# ==================== C. 反向断言：无关日不否决 ====================
def test_normal_day():
    # §238.18 重锚：原 2026-08-28 是申月，月支申×新郎年命寅=六冲 → 被相主 VETO
    # 换锚 2026-08-04 甲戌日 未月（day_zhi=戌 month_zhi=未）：
    # 戌/未 均不冲卯（新娘年命）/亥（新娘日支）/寅（新郎年命）/巳（新郎日支）
    print('\n[C] 2026-08-04 甲戌日 → 不否决（反向断言，防误伤）')
    r = _score(2026, 8, 4, [BRIDE, GROOM])
    vr = r.get('veto_reasons') or []
    check(not vr, '无关日无否决', vr)
    check(int(r.get('score') or 0) > 0, '无关日分数正常', r.get('score'))


# ==================== D. 单事主仅新郎 ====================
def test_single_groom():
    print('\n[D] 单事主（仅新郎虎）申日 → 同样拦截')
    r = _score(2026, 8, 26, [GROOM])
    check(int(r.get('score') or 0) == 0, '单新郎仍归零', r.get('score'))
    vr = '；'.join(str(v) for v in (r.get('veto_reasons') or []))
    check('新郎' in vr, '单新郎否决原因点名新郎', vr)


# ==================== E. 相主明细落地 ====================
def test_xiangzhu_detail():
    print('\n[E] 相主明细入 score_details')
    r = _score(2026, 8, 26, [BRIDE, GROOM])
    sd = r.get('score_details') or {}
    check('相主得分' in sd, '含 相主得分 键', sd.get('相主得分'))
    det = [str(x) for x in (sd.get('相主详情') or [])]
    check(bool(det), '含 相主详情 明细', det)
    check(any(x.startswith('[硬性门槛]') for x in det), '明细含 [硬性门槛]',
          [x for x in det if x.startswith('[硬性门槛]')][:2])
    check(any('新郎' in x for x in det), '明细点名新郎')
    check(any('六冲' in x for x in det), '明细写明六冲')

    r2 = _score(2026, 8, 4, [BRIDE, GROOM])
    sd2 = r2.get('score_details') or {}
    check(bool(sd2.get('相主核验说明')),
          '非否决日标注相主口径', sd2.get('相主核验说明'))


# ==================== F. 总分口径：001 §236 B3 起相主已并入 ====================
def test_total_includes_xiangzhu():
    print('\n[F] 非否决日总分 = 嫁娶评分+月令+喜用+太阳太阴+相主（§236 B3）')
    r = _score(2026, 8, 4, [BRIDE, GROOM])
    sd = r.get('score_details') or {}
    _parts = (int(sd.get('嫁娶评分') or 0) + int(sd.get('月令得分') or 0)
              + int(sd.get('喜用神得分') or 0) + int(sd.get('太阳太阴得分') or 0)
              + int(sd.get('相主得分') or 0))
    check(_parts == int(sd.get('总分') or 0),
          '总分 == 嫁娶评分+月令+喜用+太阳太阴+相主',
          '%s vs %s' % (_parts, sd.get('总分')))
    check(_parts == int(r.get('score') or 0),
          '顶层 score 与总分一致', '%s vs %s' % (_parts, r.get('score')))


# ==================== G. 通用通道相主硬门槛也升级（§238.18） ====================
def test_general_channel():
    # §238.18（2026-11-09）：相主硬门槛全量升级——通用通道也不再豁免，
    # 辅助者年命被日课六冲同样 HARD_VETO。
    print('\n[G] §238.18 后通用通道相主硬门槛也升级')
    r = _score(2026, 8, 26, [BRIDE, GROOM], ev='开业')
    # 2026-08-26 壬申日：day_zhi=申 × 新郎年命寅=六冲
    check(int(r.get('score') or 0) == 0,
          '通用通道：辅助者年命被六冲 → 也 VETO（§238.18 无豁免）', r.get('score'))
    vrs = [str(v) for v in (r.get('veto_reasons') or [])]
    check(any('相主硬门槛' in v for v in vrs),
          '通用通道 veto 来源含相主硬门槛', '; '.join(vrs))


# ==================== H. 源码锚点（防回退） ====================
def test_source_anchors():
    print('\n[H] 源码锚点防回退')
    p1 = os.path.join(_ROOT, 'modules', '评分器.py')
    with open(p1, 'r', encoding='utf-8') as f:
        s1 = f.read()
    check('xiangzhu_hard = [_d for _d in _xz_display' in s1,
          '评分器：婚嫁分支接入统一硬门槛清单')
    check(("if (_s.startswith('[硬性门槛]')" in s1
            and "'六冲' not in _s" in s1
            and "'伏吟' not in _s" in s1),
          '评分器：婚嫁分支合并六冲+年命伏吟（自刑仍留待裁，BACKLOG G-4）')
    check("'相主核验说明': '相主为硬门槛项（冲夫妻宫/年命冲即否决），相主得分已并入总分'" in s1,
          '评分器：非否决日相主已并入总分声明')
    p2 = os.path.join(_ROOT, 'modules', '婚嫁评分算法.py')
    with open(p2, 'r', encoding='utf-8') as f:
        s2 = f.read()
    check("details.append(('日支冲新郎生肖', -45))" in s2,
          '婚嫁算法：新郎生肖对称 -45')
    check("_day_clash_veto.append(f'日支{day_zhi}冲新郎本命{groom_bazi[\"year_zhi\"]}')" in s2,
          '婚嫁算法：新郎冲入一票否决清单')


# ==================== I. 口径边界：自刑暂不否决（G-4） ====================
def test_zixing_not_vetoed():
    print('\n[I] 2026-03-02 乙亥日 × 猪命（亥亥自刑）→ 嫁娶暂不否决（BACKLOG G-4）')
    r = _score(2026, 3, 2, [{'name': '新娘', 'role': '新娘', 'year_sx': '猪',
                             'sizhu': '乙亥 己卯 丙申 己亥'}])
    vr = r.get('veto_reasons') or []
    check(not any('自刑' in str(v) for v in vr), '自刑不进入否决原因', vr)
    det = [str(x) for x in ((r.get('score_details') or {}).get('相主详情') or [])]
    check(any(x.startswith('[自刑提示]') for x in det), '明细改写为[自刑提示]', det)
    check(any('暂不否决' in x for x in det), '明细显式标注待裁')


def main():
    print('=' * 74)
    print('001 §235 嫁娶通道「日支冲新郎年命」硬门槛回归')
    print('=' * 74)
    test_groom_chong()
    test_bride_symmetry()
    test_normal_day()
    test_single_groom()
    test_xiangzhu_detail()
    test_total_includes_xiangzhu()
    test_general_channel()
    test_source_anchors()
    test_zixing_not_vetoed()
    print('\n' + '=' * 74)
    if FAILS:
        print('FAIL %d 项：' % len(FAILS))
        for f in FAILS:
            print('  -', f)
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
