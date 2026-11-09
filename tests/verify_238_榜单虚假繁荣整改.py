# -*- coding: utf-8 -*-
"""001 §238 修造榜单「虚假繁荣」整改回归（2026-11-09 用户拍板）。

背景：修造·坤山榜单 10 天全 4/5✓ 高分，实为极端偏枯日+假吉神堆分，
且全部缺「相主」维度（空事主强行放行）。用户列出四类坑并下达整改：
  坑一/坑四 五行过燥过寒 → 纯展示预警（wuxing_pian_ku + UI 黄底红字框）
  坑二 合局克山仍高分   → 三合克山 -40 / 半合拱合克山 -20（拟定，待拍板）
  坑三 自刑 -8 伏吟 0 太轻 → 自刑额外 -7（合计 -15）/ 伏吟 -15（拟定，待拍板）
  核验 5 项改 6 项        → 专属事项序列插入「相主」

A. 合局克山：三合金句 -40 / 半合 -20 / 出行旁路 / 生扶不克 / 无山向不触发
B. 自刑伏吟加重：-7（基线-8合计-15）/ 伏吟 -15 / 无同支反向
C. 偏枯预警：过燥 / 过寒 / 平和 None / 用户案例 06-04 边界（火=4 触发，阈值收紧至 4 后）
D. 6 项核验端到端：修造完美画像序列 + 空事主相主 N/A
E. 源码锚点防回退
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
from modules.排序键 import perfect_profile, profile_plan_keys

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


def _xj(y, m, d, h=12, ev='修造', sx='坤山艮向'):
    return calculate_score(_sz(y, m, d, h), ev, shan_xiang=sx, zeli_mode='pure')


def _keshan_ji(r):
    return [str(x) for x in (r.get('ji_list') or []) if '克山' in str(x)]


def _ss_detail(r):
    return [str(x) for x in ((r.get('sansha_info') or {}).get('sansha_penalty_detail') or [])]


# ==================== A. 合局克山重扣 ====================
def test_heju_keshan():
    print('\n[A] 合局克山重扣（坑二）')
    # A1 三合：2026-11-17 h=6 → 丙午 己亥 乙未 己卯（亥卯未三合木局）
    r = _xj(2026, 11, 17, 6)
    check('三合木局克山（坤山属土）' in _keshan_ji(r), 'A1 三合木局克山入忌项', _keshan_ji(r))
    check('三合木局克山（坤山属土）（-40分）' in _ss_detail(r),
          'A1 三合克山 -40 分明细', _ss_detail(r))
    check('三合木局克山（坤山属土）' in (r.get('heavy_sha_names') or []),
          'A1 三合克山入 heavy_sha_names（触发 §237 防呆）')
    # A2 半合：2026-11-25 h=12 → 丙午 己亥 癸卯 戊午（亥卯半合木局）
    r = _xj(2026, 11, 25, 12)
    check('半合/拱合木局克山（坤山属土）' in _keshan_ji(r), 'A2 半合木局克山入忌项', _keshan_ji(r))
    check('半合/拱合木局克山（坤山属土）（-20分）' in _ss_detail(r),
          'A2 半合克山 -20 分明细', _ss_detail(r))
    check('半合/拱合木局克山（坤山属土）' in (r.get('heavy_sha_names') or []),
          'A2 半合克山入 heavy_sha_names')
    # A3 出行旁路：同日同事山向，出行不触发（_no_sansha 守卫）
    r = _xj(2026, 11, 17, 6, ev='出行')
    check(not _keshan_ji(r), 'A3 出行旁路不触发克山', _keshan_ji(r))
    # A4 生扶不克：2026-10-19 h=12 → 丙午 戊戌 丙寅 甲午（寅午戌火局，火生坤土）
    r = _xj(2026, 10, 19, 12)
    check(not _keshan_ji(r), 'A4 火局生土不扣（反向）', _keshan_ji(r))
    # A5 无山向不触发
    r = calculate_score(_sz(2026, 11, 17, 6), '修造', zeli_mode='pure')
    check(not _keshan_ji(r), 'A5 无山向不触发克山', _keshan_ji(r))


# ==================== B. 自刑/伏吟加重 ====================
def test_zixing_fuyin():
    print('\n[B] 自刑/伏吟加重（坑三）')
    # B1 自刑：2026-03-15 h=12 → 丙午 辛卯 戊子 戊午（仅年支时支午午自刑一对）
    r = _xj(2026, 3, 15, 12)
    ji = [str(x) for x in (r.get('ji_list') or [])]
    hit = [x for x in ji if '自刑伏吟加重' in x]
    check(hit == ['自刑伏吟加重（年支时支自刑）'], 'B1 午午自刑加重入忌项', hit)
    check('自刑伏吟加重（年支时支自刑）（-7分）' in _ss_detail(r),
          'B1 自刑额外 -7（与基线-8合计-15）', _ss_detail(r))
    check('自刑伏吟加重（年支时支自刑）' not in (r.get('heavy_sha_names') or []),
          'B1 自刑伏吟不入 heavy_sha_names（保 §237 稀缺性）')
    # B2 伏吟：2023-02-14 h=12 → 癸卯 甲寅 癸卯 戊午（年支日支卯卯伏吟一对）
    r = _xj(2023, 2, 14, 12)
    ji = [str(x) for x in (r.get('ji_list') or [])]
    hit = [x for x in ji if '自刑伏吟加重' in x]
    check(any('年支日支伏吟' in x for x in hit), 'B2 卯卯伏吟加重入忌项', hit)
    check('自刑伏吟加重（年支日支伏吟）（-15分）' in _ss_detail(r),
          'B2 伏吟 -15 分明细', _ss_detail(r))
    # B3 反向：同日 h=8（丙辰时，午卯子辰四支互异）→ 不触发
    r = _xj(2026, 3, 15, 8)
    ji = [str(x) for x in (r.get('ji_list') or [])]
    check(not any('自刑伏吟加重' in x for x in ji), 'B3 无同支不触发（反向）',
          [x for x in ji if '自刑' in x or '伏吟' in x])


# ==================== C. 五行偏枯预警 ====================
def test_pianku():
    print('\n[C] 五行偏枯预警（坑一/坑四，纯展示不改分）')
    r = _xj(2026, 6, 1, 12)   # 丙午 癸巳 丙午 甲午：火 6/8
    check(r.get('wuxing_pian_ku') == '过燥', 'C1 2026-06-01 烈火 → 过燥',
          r.get('wuxing_pian_ku'))
    r = _xj(2026, 12, 15, 0)  # 丙午 庚子 癸亥 壬子：水 5/8
    check(r.get('wuxing_pian_ku') == '过寒', 'C2 2026-12-15 水旺 → 过寒',
          r.get('wuxing_pian_ku'))
    r = _xj(2026, 8, 28, 12)  # 丙午 丙申 甲戌 庚午：火 3/8 水 0/8
    check(r.get('wuxing_pian_ku') is None, 'C3 平和日 → None', r.get('wuxing_pian_ku'))
    # C4 用户案例边界：2026-06-04 己酉日（火 4/8），阈值 4 → 触发（2026-11-09 收紧拍板）
    r = _xj(2026, 6, 4, 12)
    check(r.get('wuxing_pian_ku') == '过燥', 'C4 2026-06-04 火=4 ≥ 阈值4 → 过燥（边界锁定）',
          r.get('wuxing_pian_ku'))


# ==================== D. 6 项核验端到端 ====================
def test_six_checks():
    print('\n[D] 核验 5 项 → 6 项（含相主）')
    check(profile_plan_keys('修造') == ['得令', '合局', '德神', '扶山补龙', '相主', '硬忌'],
          'D1 修造 6 维序列', str(profile_plan_keys('修造')))
    owners = [{'name': '福主', 'role': '福主', 'year_sx': '龙'}]
    r = calculate_score(_sz(2026, 8, 28, 12), '修造', owners=[dict(o) for o in owners],
                        shan_xiang='坤山艮向', zeli_mode='pure')
    pp = perfect_profile(r, owners, '修造')
    keys = [i['key'] for i in pp['items']]
    check(keys == ['得令', '合局', '德神', '扶山补龙', '相主', '硬忌'],
          'D2 真实评分端到端 6 维', str(keys))
    check(pp['items'][3]['key'] == '扶山补龙', 'D3 专属项恒在 items[3]')
    check(len(pp['marks']) == 6, 'D4 marks 与 items 同长 6')
    # D5 空事主 → 相主 N/A 第三态（不计 ✓ 也不混入 ok 计数）
    pp2 = perfect_profile(r, [], '修造')
    xz = [i for i in pp2['items'] if i['key'] == '相主']
    check(bool(xz) and xz[0].get('na'), 'D5 空事主相主 N/A',
          xz[0] if xz else '无相主项')
    check(not pp2['all_ok'], 'D5 空事主 all_ok=False（不再 5/5 放行）')


# ==================== E. 源码锚点 ====================
def test_source_anchors():
    print('\n[E] 源码锚点防回退')
    p1 = os.path.join(_ROOT, 'modules', '评分器.py')
    with open(p1, 'r', encoding='utf-8') as f:
        s1 = f.read()
    check("'三合%s局克山（%s山属%s）'" in s1, '评分器：三合克山 -40')
    check("'半合/拱合%s局克山（%s山属%s）'" in s1, '评分器：半合/拱合克山 -20')
    check("'自刑伏吟加重（%s）'" in s1, '评分器：自刑伏吟加重')
    check("'wuxing_pian_ku': _wuxing_pian_ku" in s1, '评分器：偏枯键入 return')
    check('if _pk_fire >= 4:' in s1 and 'elif _pk_water >= 4:' in s1,
          '评分器：偏枯阈值 4/8（2026-11-09 收紧拍板）')
    p2 = os.path.join(_ROOT, 'modules', '排序键.py')
    with open(p2, 'r', encoding='utf-8') as f:
        s2 = f.read()
    check("'德神', _SPECIAL_KEYS[_sp], '相主', '硬忌'" in s2,
          '排序键：专属 6 维序列含相主')
    p3 = os.path.join(_ROOT, '主程序.py')
    with open(p3, 'r', encoding='utf-8') as f:
        s3 = f.read()
    check('"pianku_box"' in s3, '主程序：pianku_box 样式')
    check('本课五行极度偏枯（%s），请结合山家与事主命理三思' in s3,
          '主程序：偏枯警示文案（详情页+tooltip）')


# ==================== F. 精准择时（反推）覆盖 ====================
def test_reverse_ui():
    print('\n[F] 精准择时：偏枯透传 + 分档上限随维度浮动')
    from modules import 反推UI as R

    check(R._band_bounds('修造', '大吉') == (4, 6),
          'F1 修造（6 维）大吉档 4–6', str(R._band_bounds('修造', '大吉')))
    check(R._band_bounds('开业', '大吉') == (4, 5),
          'F2 通用事项（5 维）大吉档 4–5', str(R._band_bounds('开业', '大吉')))
    check(R._band_bounds('修造', '优吉') == (2, 3),
          'F3 优吉档保持 2–3', str(R._band_bounds('修造', '优吉')))

    import datetime as _dt
    from modules.反推引擎 import record_of_day
    rec = record_of_day(_dt.date(2026, 6, 1), '修造',
                        context={'shan_xiang': '坤山艮向', 'zeli_mode': 'pure'})
    check('pian_ku' in rec and rec.get('pian_ku') == '过燥',
          'F4 反推单日记录透传 pian_ku=过燥',
          '%r / %s' % (rec.get('pian_ku'), rec.get('score')))
    check(len((rec.get('check') or {}).get('items') or []) == 6,
          'F5 反推日记录核验 6 维',
          str(len((rec.get('check') or {}).get('items') or [])))

    _d = {'date': '2026-06-01', 'weekday': '周一', 'lunar': '四月十六',
          'sizhu': rec.get('sizhu', ''), 'score': rec.get('score'),
          'level': rec.get('level'), 'kind': rec.get('kind'),
          'jishen': '', 'reason': '', 'deduct_items': [], 'ji_items': [],
          'veto_reasons': [], 'pian_ku': '过燥'}
    _lines = R.ReverseWindow._build_detail_lines(
        None, _d, '修造', {'时辰': '午时', '时段': '11:00-13:00', '时柱': '甲午'}, 0, 0)
    check(any('极度偏枯' in x for x in _lines),
          'F6 反推详情文本含偏枯警示')

    from modules.择日贴 import compose_caution_lines  # noqa: F401  （运行需完整 entry，改用锚点断言）
    for _rel, _need, _lbl in (
            ('modules/反推引擎.py', "'pian_ku': best_r.get('wuxing_pian_ku')",
             'F7 反推引擎：pian_ku 透传'),
            ('modules/反推UI.py', "if _d.get('pian_ku'):",
             'F8 反推详情窗：偏枯警示块'),
            ('modules/择日贴.py', '本课五行极度偏枯',
             'F9 择日贴：偏枯警示行'),
            ('主程序.py', "'pian_ku': record.get('pian_ku') or ''",
             'F10 主程序：反推→择日贴透传')):
        with open(os.path.join(_ROOT, _rel), 'r', encoding='utf-8') as f:
            check(_need in f.read(), _lbl)

    # 001 §238.8：分档页「状态」列显示本档分档，不再直接显示 kind（吉日/慎用）
    check(R._band_status_text('大吉', '吉日') == '大吉',
          'F11 分档状态列：吉日显示分档名', R._band_status_text('大吉', '吉日'))
    check(R._band_status_text('大吉', '慎用') == '大吉·慎用',
          'F12 分档状态列：慎用日加尾注', R._band_status_text('大吉', '慎用'))
    with open(os.path.join(_ROOT, 'modules', '反推UI.py'), 'r',
              encoding='utf-8') as f:
        _s = f.read()
    check("_band_status_text(_band, _d['kind'])" in _s,
          'F13 分档页状态列接线；Top-N 仍显示 kind（不改吉凶分类）')
    check("else ''), _d['kind'])" in _s,
          'F13b Top-N 榜单状态列仍为 吉日/慎用')

    # 001 §238.9：扣分构成金额进入反推详情（克山/自刑伏吟走忌项通道）
    _pidx = R._penalty_index([
        '三合木局克山（坤山属土）（-40分）',
        '自刑伏吟加重（年支日支自刑）（-7分）',
        '月三煞(山向)（-20分）',
        '无分值文本'])
    check(_pidx.get('三合木局克山（坤山属土）') == -40
          and _pidx.get('自刑伏吟加重（年支日支自刑）') == -7
          and _pidx.get('月三煞(山向)') == -20
          and '无分值文本' not in _pidx,
          'F14 扣分构成解析（克山-40/自刑-7/三煞-20，非分值文本跳过）', str(_pidx))

    _rec9 = record_of_day(_dt.date(2026, 6, 1), '修造',
                          context={'shan_xiang': '坤山艮向', 'zeli_mode': 'pure'})
    check(isinstance(_rec9.get('penalty_detail'), list),
          'F15 反推日记录携带 penalty_detail（列表）',
          type(_rec9.get('penalty_detail')).__name__)

    _d9 = {'date': '2026-11-17', 'weekday': '周二', 'lunar': '十月初九',
           'sizhu': '丙午 己亥 乙未 己卯', 'score': 100, 'level': '★★★★ 吉',
           'kind': '吉日', 'jishen': '', 'reason': '', 'deduct_items': [],
           'ji_items': ['三合木局克山（坤山属土）'],
           'penalty_detail': ['三合木局克山（坤山属土）（-40分）'],
           'veto_reasons': [], 'pian_ku': None}
    _w9 = object.__new__(R.ReverseWindow)
    _l9 = _w9._build_detail_lines(
        _d9, '修造', {'时辰': '卯时', '时段': '05-07', '时柱': '己卯'}, 0, 0)
    check(any('三合木局克山（坤山属土）（-40分）' in x for x in _l9),
          'F16 反推详情文本忌项带 -40 金额',
          [x for x in _l9 if '克山' in x])

    for _rel in ('主程序.py', os.path.join('modules', '日课评分系统.py')):
        with open(os.path.join(_ROOT, _rel), 'r', encoding='utf-8') as f:
            _ss = f.read()
        check('扣分构成：' in _ss and '三煞扣分构成' not in _ss,
              'F17 %s：标题改「扣分构成」' % _rel)

    # 001 §238.10：Top-N 排序切换（默认吉日优先；纯总分需二次确认 + 红字标注）
    _dsample = [
        {'date': '2025-10-28', 'score': 288, 'kind': '慎用', 'jishen_fit': 0},
        {'date': '2025-12-16', 'score': 78, 'kind': '吉日', 'jishen_fit': 0},
    ]
    _tier = [d['date'] for d in sorted(
        _dsample, key=lambda d: R._top_sort_key(d, R.SORT_MODE_TIER))]
    _score = [d['date'] for d in sorted(
        _dsample, key=lambda d: R._top_sort_key(d, R.SORT_MODE_SCORE))]
    check(_tier == ['2025-12-16', '2025-10-28'],
          'F18 吉日优先：78分吉日仍压在288分慎用之前', _tier)
    check(_score == ['2025-10-28', '2025-12-16'],
          'F19 纯总分：288分慎用排到前（安全分层关闭）', _score)

    _dn, _ds = R._deduct_brief({'deduct_items': [
        {'name': '鲁班煞', 'score': -20}, {'name': '土王用事', 'score': -20},
        {'name': '太岁堆黄', 'score': -15}]})
    check(_ds == -55 and _dn == '鲁班煞、土王用事、太岁堆黄',
          'F20 降权说明：重煞名称与合计 -55', '%s / %s' % (_dn, _ds))

    _d10 = {'date': '2025-10-28', 'weekday': '周二', 'lunar': '九月初八',
            'sizhu': '乙巳 丙戌 庚午 癸未', 'score': 288, 'level': '★★★★★ 上吉',
            'kind': '慎用', 'jishen': '', 'reason': '', 'ji_items': [],
            'veto_reasons': [], 'pian_ku': None,
            'deduct_items': [{'name': '鲁班煞', 'score': -20},
                             {'name': '土王用事', 'score': -20},
                             {'name': '太岁堆黄', 'score': -15}]}
    _w10 = object.__new__(R.ReverseWindow)
    _l10 = _w10._build_detail_lines(
        _d10, '修造', {'时辰': '未时', '时段': '13-15', '时柱': '癸未'}, 0, 0)
    check(any('降权说明' in x and '-55' in x for x in _l10),
          'F21 详情文本含「降权说明」与 -55 合计',
          [x for x in _l10 if '降权' in x])

    with open(os.path.join(_ROOT, 'modules', '反推UI.py'), 'r',
              encoding='utf-8') as f:
        _s10 = f.read()
    check('排序风险确认' in _s10 and 'SORT_MODE_WARN' in _s10
          and "tag_configure('cautious_score'" in _s10
          and '排序:'.strip() in _s10,
          'F22 排序下拉 + 二次确认 + 红字标签锚点')


def main():
    print('=' * 74)
    print('001 §238 修造榜单「虚假繁荣」整改回归')
    print('=' * 74)
    test_heju_keshan()
    test_zixing_fuyin()
    test_pianku()
    test_six_checks()
    test_source_anchors()
    test_reverse_ui()
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
