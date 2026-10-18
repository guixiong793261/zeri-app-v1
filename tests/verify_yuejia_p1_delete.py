# -*- coding: utf-8 -*-
"""月家P1 删除批回归：大煞/八专/四击/安葬土瘟 超范围注册删除验收。

拍板依据：2026-10-18 用户批准「月家P1 批准删除候选」（docs/月家P1_大煞八专四击_对勘.md）、
「P1-5 P1 安葬土瘟-20 删除候选」（docs/P1-5_安葬土瘟_对勘.md）。
影响面快照：docs/影响面快照_月家P1_P14_P15删除.md（验收断言五条）。

断言（走真实产品链路 calculate_sizhu → get_checker → check）：
  A. 大煞触发日：全部事项不出现大煞条目（基类年神链发射已删；谓词保留）
  B. 八专触发日：仅嫁娶出现八专 -15，其余事项无；通配键已删
  C. 四击触发日：全部事项无四击；真四忌（嫁娶/安葬 -12）保留
  D. 土瘟触发日：修造/动土/作灶 -20 保留；安葬无土瘟条目且键已删
  E. P1-4 保留项不受影响：土府/地囊 修造/动土 仍发射；隔离事项仍零命中
退出码：全过 0，任一失败 1。
"""
import io
import sys
import datetime

sys.path.insert(0, r'd:\自编择日软件\专业级正五行择日软件')

from modules.四柱计算器 import calculate_sizhu
from modules.shensha import get_checker
from modules.shensha.神煞基类 import ShenShaChecker
from modules.事项标准 import shensha_score

FAILS = []
CHECKS = [0]

# 谓词宿主：任一子类实例均继承基类谓词（此处用嫁娶 checker 实例）
_PRED = get_checker('嫁娶')


def check(name, cond, detail=''):
    CHECKS[0] += 1
    if cond:
        print('  PASS %s' % name)
    else:
        FAILS.append(name)
        print('  FAIL %s %s' % (name, detail))


EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '开业', '出行', '安床',
          '作灶', '移徙', '入学', '求医', '签约', '安葬']


def make_sizhu(d):
    sz = calculate_sizhu(d, 10, 0)
    sz['year'] = d.year
    sz['month'] = d.month
    sz['day'] = d.day
    sz['date'] = d
    return sz


def shensha_names(event, sz):
    """返回该事项该日命中的 {名: (分, 注)}（含分数为负的凶煞）。"""
    ck = get_checker(event)
    out = {}
    for s in ck.check(sz, []):
        if isinstance(s, dict) and s.get('score', 0) < 0:
            out[s['name']] = (s.get('score'), s.get('description', ''))
    return out


def find_days(pred, year, need=3):
    """在 year 年逐日找谓词触发日。"""
    d = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    out = []
    while d <= end and len(out) < need:
        if pred(make_sizhu(d)):
            out.append(d)
        d += datetime.timedelta(days=1)
    return out


def main():
    print('=== 月家P1 删除批回归 ===')

    # ---------- A. 大煞 ----------
    print('[A] 大煞：全事项无发射，谓词保留')
    days = find_days(lambda sz: _PRED._is_dasha(sz), 2026, 3)
    check('A1 大煞触发日存在(基线)', len(days) == 3, str(days))
    ok_all = True
    for d in days:
        sz = make_sizhu(d)
        for ev in EVENTS:
            names = shensha_names(ev, sz)
            if '大煞' in names:
                ok_all = False
                print('    ✗ %s %s 仍含大煞 %s' % (d, ev, names['大煞']))
    check('A2 大煞触发日全部事项无大煞条目', ok_all)
    ok_key = all(shensha_score(ev, '大煞', None) is None for ev in EVENTS)
    check('A3 大煞分值键全删', ok_key)
    check('A4 谓词 _is_dasha 保留可用', _PRED._is_dasha(make_sizhu(days[0])) is True)

    # ---------- B. 八专 ----------
    print('[B] 八专：仅嫁娶 -15，其余无；通配删')
    bd = find_days(lambda sz: _PRED._is_bazhuan(sz), 2026, 2)
    check('B1 八专触发日存在(基线)', len(bd) == 2, str(bd))
    sz = make_sizhu(bd[0])
    for ev in EVENTS:
        names = shensha_names(ev, sz)
        if ev == '嫁娶':
            check('B2 嫁娶八专-15保留', names.get('八专', (None,))[0] == -15, str(names.get('八专')))
        else:
            check('B3 %s无八专' % ev, '八专' not in names, str(names.get('八专')))
    check('B4 嫁娶键-15', shensha_score('嫁娶', '八专', None) == -15)
    check('B5 通配键已删', shensha_score('*', '八专', None) is None)
    others = [ev for ev in EVENTS if ev != '嫁娶']
    check('B6 其余13事项键全删', all(shensha_score(ev, '八专', None) is None for ev in others))

    # ---------- C. 四击 ----------
    print('[C] 四击：全事项无发射；真四忌保留')
    cd = find_days(lambda sz: _PRED._is_siji(sz), 2026, 2)
    check('C1 四击触发日存在(基线)', len(cd) == 2, str(cd))
    ok_all = True
    for d in cd:
        sz = make_sizhu(d)
        for ev in EVENTS:
            if '四击' in shensha_names(ev, sz):
                ok_all = False
                print('    ✗ %s %s 仍含四击' % (d, ev))
    check('C2 四击触发日全部事项无四击条目', ok_all)
    check('C3 四击键全删(含通配)', all(shensha_score(ev, '四击', None) is None for ev in EVENTS)
          and shensha_score('*', '四击', None) is None)
    check('C4 真四忌嫁娶-12保留', shensha_score('嫁娶', '四忌', None) == -12)
    check('C5 真四忌安葬-12保留', shensha_score('安葬', '四忌', None) == -12)
    check('C6 四击谓词保留可用', _PRED._is_siji(make_sizhu(cd[0])) is True)

    # ---------- D. 土瘟保留项锚（安葬删除断言见 tests/verify_anzang_tuwen_delete.py，x3 批） ----------
    print('[D] 土瘟：修造/动土/作灶保留（现状锚）')
    td = find_days(lambda sz: _PRED._is_tuwen(sz), 2026, 2)
    check('D1 土瘟触发日存在(基线)', len(td) == 2, str(td))
    sz = make_sizhu(td[0])
    check('D2 修造土瘟-20保留', shensha_names('修造', sz).get('土瘟', (None,))[0] == -20)
    check('D3 动土土瘟-20保留', shensha_names('动土', sz).get('土瘟', (None,))[0] == -20)
    check('D4 作灶土瘟-20保留', shensha_names('作灶', sz).get('土瘟', (None,))[0] == -20)

    # ---------- E. P1-4 保留项不受影响 ----------
    print('[E] P1-4：土府/地囊 修造/动土保留，隔离事项零命中')
    check('E1 修造土府键-20', shensha_score('修造', '土府', None) == -20)
    check('E2 修造地囊键-25', shensha_score('修造', '地囊', None) == -25)
    # 修造通道土府走自有谓词 _is_tufu2（寅月辰日…月支对冲映射），地囊走 _is_dinang
    _XZ = get_checker('修造')
    tf_days = find_days(lambda sz: _XZ._is_tufu2(sz), 2026, 2)
    dn_days = find_days(lambda sz: _XZ._is_dinang(sz), 2026, 2)
    check('E3 土府/地囊触发日存在(基线)', len(tf_days) == 2 and len(dn_days) == 2,
          '%s %s' % (tf_days, dn_days))
    ok_keep = True
    for d in tf_days:  # 土府日：修造/动土须发射土府
        sz = make_sizhu(d)
        for ev in ('修造', '动土'):
            if '土府' not in shensha_names(ev, sz):
                ok_keep = False
                print('    ✗ %s %s 缺 土府（保留项被误删）' % (d, ev))
        for ev in ('入学', '求医', '签约'):
            if '土府' in shensha_names(ev, sz):
                ok_keep = False
                print('    ✗ %s %s 隔离项仍命中 土府' % (d, ev))
    for d in dn_days:  # 地囊日：修造/动土须发射地囊
        sz = make_sizhu(d)
        for ev in ('修造', '动土'):
            if '地囊' not in shensha_names(ev, sz):
                ok_keep = False
                print('    ✗ %s %s 缺 地囊（保留项被误删）' % (d, ev))
        for ev in ('入宅', '移徙', '入学', '求医', '签约'):
            if '地囊' in shensha_names(ev, sz):
                ok_keep = False
                print('    ✗ %s %s 隔离项仍命中 地囊' % (d, ev))
    check('E4 保留项发射+隔离项零命中', ok_keep)

    print('---')
    print('CHECKS=%d FAILS=%d' % (CHECKS[0], len(FAILS)))
    if FAILS:
        for f in FAILS:
            print('FAILED: %s' % f)
        return 1
    print('月家P1 删除批回归全部通过')
    return 0


if __name__ == '__main__':
    io.open  # noqa
    sys.exit(main())
