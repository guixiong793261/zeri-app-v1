# -*- coding: utf-8 -*-
"""
择日贴模块 —— 日课收藏与成帖输出
入口：择日结果列表右键某行 →「加入择日贴」；工具菜单 →「择日贴」

两种视图（按传统择吉帖模板优化）：
  1. 单课详解（择吉选日帖）：公元/岁次/农历/干支(完整四柱)/星期 + 吉时三级(首选大吉/次选吉/备选次吉)
     + 宜/忌 + 吉神方位(财神/喜神/福神/贵神) + 冲煞 + 用事/事主 + 评级 + 择日师落款
  2. 择日总录：多课汇总表 + 自动择定首选/备选吉日 + 择日评语

黄历字段（宜忌/吉神方位/时辰吉凶/冲煞/农历）按日期自动推算，与今日黄历同口径。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import html
import os
import tempfile
import webbrowser

from .四柱计算器 import get_lunar_date, calculate_sizhu
from .今日黄历 import (get_yi_ji, calc_shichen_jixiong, XI_SHEN, FU_SHEN,
                       YANG_GUI, YIN_GUI, CAI_SHEN, SHA_FANG,
                       SHENGXIAO_MAP, SHICHEN_HOURS, TIAN_GAN_ORDER, DI_ZHI_ORDER)

# 时辰区间（二十四小时制）
_SHICHEN_RANGE = {
    '子': '23:00—00:59', '丑': '01:00—02:59', '寅': '03:00—04:59', '卯': '05:00—06:59',
    '辰': '07:00—08:59', '巳': '09:00—10:59', '午': '11:00—12:59', '未': '13:00—14:59',
    '申': '15:00—16:59', '酉': '17:00—18:59', '戌': '19:00—20:59', '亥': '21:00—22:59'
}
_WEEK_CN = ['一', '二', '三', '四', '五', '六', '日']
_CN_MONTHS = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
_CN_DIGIT = '〇一二三四五六七八九'
_MONTH_KEY = {'正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
              '七': 7, '八': 8, '九': 9, '十': 10, '冬': 11, '腊': 12}


def _lunar_month_str(m, is_leap=False):
    """农历月统一为中文（'七月'；数字1-12自动转；源串含'闰'时保留闰月前缀）"""
    if isinstance(m, str):
        # get_lunar_date 的 month 已含闰前缀（'闰七月'）但无 is_leap 键：
        # 中文→数字转换会丢'闰'，须先从源串回收闰标记（修复闰月显示丢"闰"）。
        if '闰' in m:
            is_leap = True
        key = m.replace('月', '').replace('闰', '')
        if key in _MONTH_KEY:
            m = _MONTH_KEY[key]
        else:
            return m if m.endswith('月') else m + '月'
    leap = '闰' if is_leap else ''
    return f"{leap}{_CN_MONTHS[m - 1]}月"


def _lunar_day_str(d):
    """农历日统一为中文（'十六'；数字16自动转）"""
    if isinstance(d, str):
        return d
    names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
             '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
             '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
    return names[d - 1] if 1 <= d <= 30 else str(d)


def _cn_year_num(y):
    return ''.join(_CN_DIGIT[int(c)] for c in str(y))


def _cn_month_num(m):
    names = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
    return names[m - 1] if 1 <= m <= 12 else str(m)


def _owner_year_gz(owner):
    """从 owner dict 取年干支：优先 year_gz，其次 sizhu 首柱，否则 ''"""
    if not isinstance(owner, dict):
        return ''
    if owner.get('year_gz'):
        return owner['year_gz']
    sz = owner.get('sizhu') or ''
    if sz:
        f = sz.split()[0] if sz.split() else ''
        if len(f) >= 2:
            return f[:2]
    return ''


def _owner_year_sx(owner):
    """从 owner 取生肖：优先 year_sx，其次 year_gz[1] 查 SHENGXIAO_MAP"""
    if not isinstance(owner, dict):
        return ''
    sx = owner.get('year_sx') or ''
    if sx:
        return sx
    gz = _owner_year_gz(owner)
    if len(gz) >= 2:
        return SHENGXIAO_MAP.get(gz[1], '')
    return ''


def _sx_to_zhi(sx):
    """生肖 → 地支（SHENGXIAO_MAP 反查；用于吉时冲命校验）。"""
    if not sx:
        return ''
    for _z, _s in SHENGXIAO_MAP.items():
        if _s == sx:
            return _z
    return ''


def _owner_life_line(owner, label_suffix='贵庚'):
    """按模板格式显示：父：辛卯年（辛卯干支）或 宅主：○○年（○○干支）贵庚"""
    if not isinstance(owner, dict):
        return ''
    gz = _owner_year_gz(owner)
    if gz:
        return f"{gz}年（{gz}）{label_suffix}"
    name = owner.get('name') or ''
    return f"{name if name else ''}（——）{label_suffix}".strip()


def _prepare_owners(e):
    """把 e 中的 owners_list（dict list 优先）或 owners（字符串）标准化。
    返回 dict：{
      'list': [ {name,role,year_gz,year_sx,sizhu,...}, ...],
      'xianming': {...} or None,  # 安葬仙命（死者）
      'zhushi': [...],            # 安葬主事人（孝子1..N）
      'parents': [父, 母 or None], # 修造/动土 父母福主
      'zhaizhu': {...} or None,   # 入宅 宅主
      'fuzhu_list': [...],        # 入宅 福主
      'engagement_people': [乾造,坤造 or None] # 订婚纳彩
    }
    """
    raw = e.get('owners_list') or []
    if isinstance(raw, list) and raw and any(isinstance(x, dict) for x in raw):
        owners = [dict(x) for x in raw if isinstance(x, dict)]
    else:
        # 回退：从 groom/bride 构造（婚嫁类）
        owners = []
        for k, role in (('groom', '新郎'), ('bride', '新娘')):
            d = e.get(k)
            if isinstance(d, dict):
                d.setdefault('role', role)
                owners.append(d)
        # 回退：字符串 owners 占位
        if not owners:
            s = str(e.get('owners') or '')
            if s and s not in ('无', '-', '—'):
                for tok in s.replace('\n', '；').replace(';', '；').split('；'):
                    tok = tok.strip().strip('，').strip(',')
                    if tok:
                        owners.append({'name': tok, 'role': tok, 'year_gz': '', 'year_sx': ''})

    xianming = None   # 仙命 = 安葬：死者（role 含"死者"）
    zhushi = []       # 主事人 = 安葬孝子们
    engagement_people = []  # 乾造/坤造
    groom_d = bride_d = None
    for o in owners:
        role = str(o.get('role') or o.get('name') or '')
        if '死者' in role and xianming is None:
            xianming = o
        elif '孝子' in role:
            zhushi.append(o)
        # 婚嫁角色（嫁娶/订婚/纳采）：乾造坤造
        if role in ('新郎', '乾造') or (role and '新郎' in role):
            if groom_d is None:
                groom_d = o
        if role in ('新娘', '坤造') or (role and '新娘' in role):
            if bride_d is None:
                bride_d = o
    engagement_people = [groom_d, bride_d]

    # 父母/宅主/福主：按 order 排：
    #   入宅：宅主 = [0]；福主 = [1:]
    #   其他（修造/动土/安葬/通用）：父母 = [0][1]；福主 = [2:]
    life_owners = [o for o in owners if o is not xianming and o not in zhushi]
    parents = [None, None]
    zhaizhu = None
    fuzhu_list = []
    ev = str(e.get('event_type') or '')
    if life_owners:
        parents[0] = life_owners[0]
        if len(life_owners) > 1:
            parents[1] = life_owners[1]
        zhaizhu = life_owners[0]
        fuzhu_list = life_owners[1:] if ev == '入宅' else life_owners[2:]

    return {
        'list': owners,
        'xianming': xianming,
        'zhushi': zhushi,
        'parents': parents,
        'zhaizhu': zhaizhu,
        'fuzhu_list': fuzhu_list,
        'engagement_people': engagement_people,
    }


def prepare_entry(entry):
    """补齐日课的黄历字段。entry 需含 date(YYYY-MM-DD)，可选 sizhu/score/level/owners/event_type
    新增：
      - _template：marriage/engagement/xiuzao/dongtu/ruzhai/anzhang/common
      - _owners_map：通过 _prepare_owners 解析（仙命/主事/父母/宅主/福主/乾造坤造）
      - _shanxiang / _fenjin：修造/动土/入宅/安葬坐山分金线
      - 婚嫁类 groom/bride/fu_xing/zi_xing 已兼容保留。"""
    e = dict(entry)
    dt = datetime.strptime(e['date'], "%Y-%m-%d").date()

    # 四柱：优先用日课自带的（与择日结果一致），否则按午时推算
    nian = yue = ri = shi = ''
    parts = str(e.get('sizhu', '')).split()
    if len(parts) == 4 and all(len(p) >= 2 for p in parts):
        nian, yue, ri, shi = (p[:2] for p in parts)
    else:
        sz = calculate_sizhu(dt, 12, 0)
        nian = sz.get('年柱', '')
        yue = sz.get('月柱', '')
        ri = sz.get('日柱', '')
        shi = sz.get('时柱', '')
    if not (nian and yue and ri and shi):
        raise ValueError(f"{e['date']} 四柱计算失败")

    lunar = get_lunar_date(dt)
    day_gan, day_zhi = ri[0], ri[1]

    # 吉时三级：按十二时辰吉凶得分取前三
    hours = calc_shichen_jixiong(day_gan, day_zhi, nian[1], yue[1])
    # 001 §193 主轨 Commit1（2026-10-28 拍板）：婚嫁类吉时须过新人年命冲克校验。
    # 原实现只取通书时辰吉凶分（黄道/贵人/禄神等），冲新郎/新娘年支的时辰会被
    # 印成「大吉」发轿时辰——2026 年冲新娘年支时辰进入前三吉时的天数：未命 171、
    # 申 164、亥 146、午 122 天。冲命时辰一律不参与吉时分派（时辰层已将其列
    # 禁用，见 嫁娶神煞扩展.get_lucky_hours）。
    _avoid_zhi = set()
    if str(e.get('event_type') or '') in ('嫁娶', '订婚', '订盟', '订盟纳采', '纳采'):
        for _o in (_prepare_owners(e).get('list') or []):
            _gz = _owner_year_gz(_o)
            _z = _gz[1] if len(_gz) >= 2 else ''
            if not _z:
                _z = _sx_to_zhi(_owner_year_sx(_o))
            if len(_z) == 1 and _z in DI_ZHI_ORDER:
                _avoid_zhi.add(DI_ZHI_ORDER[(DI_ZHI_ORDER.index(_z) + 6) % 12])
    good = sorted(
        [h for h in hours if h['score'] > 0 and h['zhi'] not in _avoid_zhi],
        key=lambda x: -x['score'])[:4]
    grades = ['大吉', '吉', '次吉', '吉']
    jishi = []
    for i, h in enumerate(good):
        jishi.append({
            'ganzhi': h['ganzhi'],
            'zhi': h['zhi'],
            'range': _SHICHEN_RANGE.get(h['zhi'], ''),
            'grade': grades[i] if i < 3 else '吉',
            'tags': '/'.join(h['tags'][:2]),
            'start_hour': SHICHEN_HOURS.get(h['zhi'], (0,))[0] if h.get('zhi') else 0,
        })

    # 吉时手动覆盖（2026-09-07用户要求：吉时支持手动修改）
    # jishi_override = {'段序号': '时支'}；段序号0起，时支须为当日十二时辰之一。
    # 手动段显示该时辰自身吉凶等级（吉/平/凶），区别于自动段的名次等级（大吉/吉/次吉）。
    _ov = e.get('jishi_override')
    if isinstance(_ov, dict) and _ov:
        for _k, _zhi in _ov.items():
            try:
                _idx = int(_k)
            except (TypeError, ValueError):
                continue
            if not (0 <= _idx <= 5):
                continue
            _h = next((x for x in hours if x.get('zhi') == _zhi), None)
            if _h is None:
                continue
            _slot = {
                'ganzhi': _h['ganzhi'],
                'zhi': _h['zhi'],
                'range': _SHICHEN_RANGE.get(_h['zhi'], ''),
                'grade': _h.get('level') or '吉',
                'tags': '/'.join(_h['tags'][:2]),
                'start_hour': SHICHEN_HOURS.get(_h['zhi'], (0,))[0] if _h.get('zhi') else 0,
                'manual': True,
            }
            if _idx < len(jishi):
                jishi[_idx] = _slot
            else:
                jishi.append(_slot)

    yi, ji = get_yi_ji(day_gan, day_zhi)

    e['_dt'] = dt
    e['_nian'], e['_yue'], e['_ri'], e['_shi'] = nian, yue, ri, shi
    e['_lunar_month'] = _lunar_month_str(lunar.get('month'), lunar.get('is_leap', False))
    e['_lunar_day'] = _lunar_day_str(lunar.get('day'))
    e['_lunar_str'] = e['_lunar_month'] + e['_lunar_day']
    e['_lunar_year'] = nian  # 干支年（如 辛卯 / 辛丑）
    e['_week'] = f"星期{_WEEK_CN[dt.weekday()]}"
    e['_shengxiao'] = SHENGXIAO_MAP.get(nian[1], '')
    e['_jishi'] = jishi
    e['_yi'] = yi
    e['_ji'] = ji
    e['_cai'] = CAI_SHEN.get(day_gan, '—')
    e['_xi'] = XI_SHEN.get(day_gan, '—')
    e['_fu'] = FU_SHEN.get(day_gan, '—')
    e['_gui'] = YANG_GUI.get(day_gan, '—')
    # 日冲干支（六十甲子序+30，即干支各进六位）与被冲生肖
    _cg = (TIAN_GAN_ORDER.index(day_gan) + 6) % 10
    _cz = (DI_ZHI_ORDER.index(day_zhi) + 6) % 12
    e['_chong_gz'] = TIAN_GAN_ORDER[_cg] + DI_ZHI_ORDER[_cz]
    e['_chong_sx'] = SHENGXIAO_MAP.get(DI_ZHI_ORDER[_cz], '')
    e['_sha'] = SHA_FANG.get(day_zhi, '—')

    # 模板分派
    _ev = str(e.get('event_type') or '')
    if _ev == '嫁娶':
        e['_template'] = 'marriage'
    elif _ev in {'订婚', '订盟', '订盟纳采', '纳采'}:
        e['_template'] = 'engagement'
    elif _ev in {'修造', '拆舍', '作灶', '安床'}:
        e['_template'] = 'xiuzao'
    elif _ev == '动土':
        e['_template'] = 'dongtu'
    elif _ev == '入宅':
        e['_template'] = 'ruzhai'
    elif _ev == '安葬':
        e['_template'] = 'anzhang'
    else:
        e['_template'] = 'common'
    e['_is_marriage'] = (e['_template'] == 'marriage')  # 兼容旧变量

    # owners_list 解析 → 仙命/主事/父母/宅主/福主
    e['_owners_map'] = _prepare_owners(e)

    # 坐山分金线（修造/动土/入宅/安葬：标题里第一行）
    # 主程序可在 add_result_to_zeri_tie 打包：shan_xiang（如 子山午向兼壬丙）、fenjin（如 庚子庚午）
    shan = str(e.get('shan_xiang') or '')
    fj = str(e.get('fenjin') or '')
    if shan:
        if fj and fj not in ('—', '无'):
            e['_shan_line'] = f"{shan}　分金{fj}"
        else:
            e['_shan_line'] = shan
    else:
        e['_shan_line'] = '○○山○○向兼○○分金' if e['_template'] in {'xiuzao', 'dongtu', 'ruzhai', 'anzhang'} else ''

    # 婚嫁类 groom/bride 兜底（engagement 也需要乾造坤造）
    if e['_template'] in {'marriage', 'engagement'}:
        # 从 _owners_map 回写 groom/bride（若尚未在 entry 顶层定义）
        eng = e['_owners_map']['engagement_people']
        e.setdefault('groom', eng[0])
        e.setdefault('bride', eng[1])
        # groom/bride 缺失：从 owners 字符串拆（占位兼容）
        if not e.get('groom') and not e.get('bride'):
            o = str(e.get('owners') or '')
            if o:
                if '新郎' in o:
                    e['groom'] = {'name': '新郎', 'role': '乾造', 'sizhu': '', 'yangqi': ''}
                if '新娘' in o:
                    e['bride'] = {'name': '新娘', 'role': '坤造', 'sizhu': '', 'yintai': ''}
        # 夫星子星兜底
        if not e.get('fu_xing'):
            b = e.get('bride')
            if isinstance(b, dict):
                e['fu_xing'] = b.get('fu', '')
        if not e.get('zi_xing'):
            b = e.get('bride')
            if isinstance(b, dict):
                e['zi_xing'] = b.get('zi', '')

    return e


def compose_detail(e):
    """纯文本版单课帖（复制/导出用）——按模板分派"""
    lines = compose_detail_lines(e)
    return '\n'.join(t for _, t in lines)


# ==================== 各用事专用行序列生成函数 ====================

def _jishi_hhmm(jishi_item):
    """把吉时dict格式化为 "HH时MM分"（时辰起点）；无则 '○时○分' 占位"""
    if not isinstance(jishi_item, dict):
        return '○时○分'
    h = jishi_item.get('start_hour')
    if h is None:
        zhi = jishi_item.get('zhi') or ''
        rng = jishi_item.get('range') or ''
        if rng and rng[:2].isdigit():
            h = int(rng[:2])
        else:
            return '○时○分'
    h = int(h) % 24
    return f"{h:02d}时00分"


def _zhushi_line(owners_list):
    """主事人：事主1、事主2、事主3 → 逗号"""
    names = []
    for o in owners_list or []:
        if isinstance(o, dict):
            nm = o.get('name') or ''
            if nm:
                names.append(nm)
    if not names:
        return '＿＿＿、＿＿＿、＿＿＿'
    return '、'.join(names)


# ============ 帖式公共小工具（2026-09-06 模板加全） ============

_YEAR_SANSHA_FANG = {  # 年三煞：年支三合局煞方（与评分器 year_sansha_map 口径一致）
    '申': ('巳午未', '南'), '子': ('巳午未', '南'), '辰': ('巳午未', '南'),
    '寅': ('亥子丑', '北'), '午': ('亥子丑', '北'), '戌': ('亥子丑', '北'),
    '巳': ('寅卯辰', '东'), '酉': ('寅卯辰', '东'), '丑': ('寅卯辰', '东'),
    '亥': ('申酉戌', '西'), '卯': ('申酉戌', '西'), '未': ('申酉戌', '西'),
}
_WUHUANG_PATH = ['中', '乾', '兑', '艮', '离', '坎', '坤', '震', '巽']  # 洛书轨迹，与二十四山模块一致
_WUHUANG_DIR = {'乾': '西北（戌乾亥）', '兑': '西（庚酉辛）', '艮': '东北（丑艮寅）',
                '离': '南（丙午丁）', '坎': '北（壬子癸）', '坤': '西南（未坤申）',
                '震': '东（甲卯乙）', '巽': '东南（辰巽巳）'}
_ZHONGSANG_MAP = {'寅': ['庚', '甲'], '卯': ['乙', '辛'], '辰': ['戊', '己'],
                  '巳': ['丙', '壬'], '午': ['丁', '癸'], '未': ['戊', '己'],
                  '申': ['庚', '甲'], '酉': ['乙', '辛'], '戌': ['戊', '己'],
                  '亥': ['丙', '壬'], '子': ['丁', '癸'], '丑': ['戊', '己']}
_FURI_MAP = {'寅': '甲', '卯': '乙', '辰': '丙', '巳': '丁', '午': '戊', '未': '己',
             '申': '庚', '酉': '辛', '戌': '壬', '亥': '癸', '子': '甲', '丑': '乙'}


def _score_line(e):
    """评分行文本（干支行下方，与嫁娶贴体系化；无评分返回''）"""
    _sc = str(e.get('score') or '').strip()
    _lv = str(e.get('level') or '').strip()
    if _sc and _lv:
        return f"评　分：{_sc}分　{_lv}"
    if _sc:
        return f"评　分：{_sc}分"
    if _lv:
        return f"评　分：{_lv}"
    return ''


def _jishi_stage(e, idx):
    """第idx档吉时文本（如 '甲申时（15:00—16:59）　大吉'）；不足时回退最后一档，无吉时'—'"""
    js = e.get('_jishi') or []
    if not js:
        return '—'
    j = js[idx] if len(js) > idx else js[-1]
    return f"{j['ganzhi']}时（{j['range']}）　{j['grade']}"


# 各模板吉时分段标签（与 compose_* 吉时行行首一致，供手动修改对话框与双击定位）
_STAGE_LABELS = {
    'marriage': ['发轿时辰', '回轿时辰', '拜堂合卺'],
    'engagement': ['起担（男方出发）', '纳聘（送达聘礼）', '交换庚帖·定盟'],
    'xiuzao': ['祭拜山神·土地', '动土开挖·奠基', '定基下石'],
    'dongtu': ['祭拜山神·土地', '动土开挖·奠基', '定基下石'],
    'ruzhai': ['新宅开大门（进宅）', '安香火·神位（镇宅）', '安床铺（安床仪式）', '开灶点火（进火）'],
    'anzhang': ['祭山·告神', '破土开圹（挖穴）', '下棺入土（落葬）', '封墓竣事（回土）'],
    'common': ['首选', '次选', '备选', '又备'],
}


def _jishi_stage_labels(tpl):
    """模板对应吉时分段标签；未知模板回退通用4段"""
    return _STAGE_LABELS.get(tpl, _STAGE_LABELS['common'])

def _stage_label(e, idx):
    """第idx段吉时的有效标签：优先用户手动覆盖 jishi_labels={'段序号': '文字'}，否则用模板默认。
    （2026-09-08 用户要求：吉时项下事项文字可自由修改）"""
    labs = _jishi_stage_labels(e.get('_template') or '')
    ov = e.get('jishi_labels')
    if isinstance(ov, dict):
        v = ov.get(str(idx))
        if v is None:
            v = ov.get(idx)
        if v is not None and str(v).strip():
            return str(v).strip()
    if 0 <= idx < len(labs):
        return labs[idx]
    return labs[-1] if labs else ''

def _stage_labels_effective(e):
    """本课各段吉时的有效标签列表（含用户覆盖），供双击定位等使用"""
    labs = _jishi_stage_labels(e.get('_template') or '')
    return [_stage_label(e, i) for i in range(len(labs))]

def _year_sansha_text(e):
    """年三煞方位说明：'北（亥子丑）'；无年柱返回''"""
    yz = (e.get('_nian') or '')[1:2]
    if yz in _YEAR_SANSHA_FANG:
        br, d = _YEAR_SANSHA_FANG[yz]
        return f"{d}（{br}）"
    return ''


def _year_wuhuang_text(e):
    """年五黄方位（流年紫白，与二十四山模块 check_wu_huang 同口径）：'南（丙午丁）'/'中宫'"""
    y = e['_dt'].year
    m = (y - 1864) % 9
    s = (1 - m) % 9 or 9
    palace = _WUHUANG_PATH[(5 - s) % 9]
    if palace == '中':
        return '中宫（全域宜静）'
    return _WUHUANG_DIR.get(palace, palace)


def _zhongsang_hits(e):
    """重丧类凶煞实测（口径与安葬神煞模块一致）：返回犯煞名列表，空=均避开"""
    yz = (e.get('_nian') or '')[1:2]
    mz = (e.get('_yue') or '')[1:2]
    rg = e.get('_ri') or ''
    dg, dz = rg[:1], rg[1:2]
    hits = []
    if dg in _ZHONGSANG_MAP.get(mz, []):
        hits.append('重丧日')
    if dg in _ZHONGSANG_MAP.get(yz, []):
        hits.append('年重丧')
    season = {'寅': '春', '卯': '春', '辰': '春', '巳': '夏', '午': '夏', '未': '夏',
              '申': '秋', '酉': '秋', '戌': '秋', '亥': '冬', '子': '冬', '丑': '冬'}.get(mz)
    if season and dz == {'春': '辰', '夏': '未', '秋': '戌', '冬': '丑'}[season]:
        hits.append('三丧日')
    if dg == _FURI_MAP.get(mz):
        hits.append('复日')
    return hits


def _owner_sizhu_text(o):
    """事主四柱文本：有四柱用四柱，否则年命；'○○'占位"""
    if not isinstance(o, dict):
        return '○○'
    sz = str(o.get('sizhu') or '').strip()
    if sz:
        return sz
    gz = _owner_year_gz(o)
    return f"{gz}年命" if gz else '○○'


def _owner_xiyong_text(o):
    """主事人喜用神文本（喜用神计算器现算；失败返回''）"""
    try:
        from .喜用神计算器 import calculate_xishen_yongshen
        parts = str((o or {}).get('sizhu') or '').split()
        if len(parts) != 4:
            return ''
        d = {'年柱': parts[0], '月柱': parts[1], '日柱': parts[2], '时柱': parts[3]}
        xs, ys = calculate_xishen_yongshen(d)
        return str(xs or ys or '').strip()
    except Exception:
        return ''


def _signature_lines(e):
    """统一落款：择日师 → 择日依据 → 岁次谨识"""
    lines = []
    a = lines.append
    a(('small', '择日师：廖贵雄'))
    a(('small', f"择日依据：{DIANJI_BANBEN}"))
    now = datetime.now()
    a(('small', f"岁次{e['_nian']}　{_cn_year_num(now.year)}年{_cn_month_num(now.month)}月　谨识"))
    return lines


def compose_engagement_lines(e):
    """订婚/纳采红纸帖：永结同心·订盟纳采（2026-09-06 模板加全：男女四柱分列+三段吉时+评分行）"""
    lines = []
    a = lines.append
    a(('', ''))
    a(('title', '永结同心 · 订盟纳采'))
    a(('', ''))
    groom = e.get('groom') if isinstance(e.get('groom'), dict) else None
    bride = e.get('bride') if isinstance(e.get('bride'), dict) else None
    a(('h2', '【男方】（乾造）'))
    if groom:
        a(('body', f"四柱：{_owner_sizhu_text(groom)}"))
        yq = groom.get('yangqi')
        if yq and yq not in ('未知', ''):
            a(('body', f"阳气：{yq}"))
    else:
        a(('body', '四柱：○○'))
    a(('', ''))
    a(('h2', '【女方】（坤造）'))
    if bride:
        a(('body', f"四柱：{_owner_sizhu_text(bride)}"))
        yt = bride.get('yintai')
        if yt and yt not in ('未知', ''):
            a(('body', f"阴胎：{yt}"))
    else:
        a(('body', '四柱：○○'))
    fu = e.get('fu_xing') or ''
    zi = e.get('zi_xing') or ''
    if fu or zi:
        a(('body', f"夫星：{fu or '○○'}　/　子星：{zi or '○○'}"))
    a(('', ''))
    a(('h2', '● 订盟纳采吉日'))
    a(('body', f"谨择 {e['_nian']}年 {e['_lunar_month']}{e['_lunar_day']} 订盟纳采大利。"))
    a(('body', f"干　支：{e['_nian']}年　{e['_yue']}月　{e['_ri']}日　{e['_shi']}时"))
    sl = _score_line(e)
    if sl:
        a(('body', sl))
    a(('', ''))
    a(('h2', '【　吉　时　】'))
    a(('body', f"{_stage_label(e, 0)}：{_jishi_stage(e, 0)}"))
    a(('body', f"{_stage_label(e, 1)}：{_jishi_stage(e, 1)}"))
    a(('body', f"{_stage_label(e, 2)}：{_jishi_stage(e, 2)}"))
    a(('', ''))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}"))
    a(('small', f"（属{e['_chong_sx']}者及新娘兄弟当日宜避之）"))
    a(('', ''))
    lines.extend(_signature_lines(e))
    return lines


def compose_xiuzao_lines(e):
    """修造/拆舍/作灶/安床 红纸帖：紫微高照·开工修造（2026-09-06 模板加全：坐山+避煞方位+评分行）"""
    lines = []
    a = lines.append
    a(('', ''))
    a(('title', '紫微高照 · 开工修造'))
    a(('', ''))
    owners = e['_owners_map']
    zhu = owners['zhaizhu'] or owners['parents'][0]
    a(('h2', '【主事人】'))
    if zhu:
        g = str(zhu.get('gender') or '')
        _role = '乾造' if g == '男' else ('坤造' if g == '女' else '乾造/坤造')
        a(('body', f"{_role}：{_owner_sizhu_text(zhu)}"))
        xy = _owner_xiyong_text(zhu)
        if xy:
            a(('body', f"喜用神：{xy}"))
    else:
        a(('body', '乾造/坤造：○○'))
    fuzhu = [o for o in owners['list']
             if o is not zhu and o is not owners['xianming'] and o not in owners['zhushi']]
    for o in fuzhu[:3]:
        a(('body', f"福主：{_owner_sizhu_text(o)}"))
    a(('', ''))
    a(('h2', '【坐山朝向】'))
    a(('body', f"坐　{e.get('_shan_line') or '○○山○○向兼○○分金'}"))
    a(('', ''))
    j0 = e['_jishi'][0] if e['_jishi'] else None
    shi0 = j0['ganzhi'] if j0 and isinstance(j0, dict) else '○'
    a(('h2', '● 动土修造吉日'))
    a(('body', f"谨择 {e['_nian']}年 {e['_lunar_month']}{e['_lunar_day']} 动土修造大利。"))
    a(('body', f"干　支：{e['_nian']}年　{e['_yue']}月　{e['_ri']}日　{e['_shi']}时"))
    sl = _score_line(e)
    if sl:
        a(('body', sl))
    a(('', ''))
    a(('h2', '【　吉　时　】'))
    a(('body', f"{_stage_label(e, 0)}：{_jishi_stage(e, 0)}"))
    a(('body', f"{_stage_label(e, 1)}：{_jishi_stage(e, 1)}"))
    a(('body', f"{_stage_label(e, 2)}：{_jishi_stage(e, 2)}"))
    a(('', ''))
    a(('h2', '【避煞方位】'))
    ss = _year_sansha_text(e)
    if ss:
        a(('body', f"⚠ 忌在 {ss} 方（年三煞）动土"))
    wh = _year_wuhuang_text(e)
    if wh:
        a(('body', f"⚠ 忌在 {wh} 方（年五黄）开挖"))
    a(('', ''))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}"))
    a(('small', f"（属{e['_chong_sx']}者及孕妇当日宜远离施工现场）"))
    a(('', ''))
    lines.extend(_signature_lines(e))
    return lines


def compose_dongtu_lines(e):
    """动土红纸帖：紫微高照·兴工动土（2026-09-06 模板加全：与修造款同体系）"""
    lines = []
    a = lines.append
    a(('', ''))
    a(('title', '紫微高照 · 兴工动土'))
    a(('', ''))
    owners = e['_owners_map']
    zhu = owners['zhaizhu'] or owners['parents'][0]
    a(('h2', '【主事人】'))
    if zhu:
        g = str(zhu.get('gender') or '')
        _role = '乾造' if g == '男' else ('坤造' if g == '女' else '乾造/坤造')
        a(('body', f"{_role}：{_owner_sizhu_text(zhu)}"))
        xy = _owner_xiyong_text(zhu)
        if xy:
            a(('body', f"喜用神：{xy}"))
    else:
        a(('body', '乾造/坤造：○○'))
    fuzhu = [o for o in owners['list']
             if o is not zhu and o is not owners['xianming'] and o not in owners['zhushi']]
    for o in fuzhu[:3]:
        a(('body', f"福主：{_owner_sizhu_text(o)}"))
    a(('', ''))
    a(('h2', '【坐山朝向】'))
    a(('body', f"坐　{e.get('_shan_line') or '○○山○○向兼○○分金'}"))
    a(('', ''))
    a(('h2', '● 兴工动土吉日'))
    a(('body', f"谨择 {e['_nian']}年 {e['_lunar_month']}{e['_lunar_day']} 兴工动土大利。"))
    a(('body', f"干　支：{e['_nian']}年　{e['_yue']}月　{e['_ri']}日　{e['_shi']}时"))
    sl = _score_line(e)
    if sl:
        a(('body', sl))
    a(('', ''))
    a(('h2', '【　吉　时　】'))
    a(('body', f"{_stage_label(e, 0)}：{_jishi_stage(e, 0)}"))
    a(('body', f"{_stage_label(e, 1)}：{_jishi_stage(e, 1)}"))
    a(('body', f"{_stage_label(e, 2)}：{_jishi_stage(e, 2)}"))
    a(('', ''))
    a(('h2', '【避煞方位】'))
    ss = _year_sansha_text(e)
    if ss:
        a(('body', f"⚠ 忌在 {ss} 方（年三煞）动土"))
    wh = _year_wuhuang_text(e)
    if wh:
        a(('body', f"⚠ 忌在 {wh} 方（年五黄）开挖"))
    a(('', ''))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}"))
    a(('small', f"（属{e['_chong_sx']}者及孕妇当日宜远离施工现场）"))
    a(('', ''))
    lines.extend(_signature_lines(e))
    return lines


def compose_ruzhai_lines(e):
    """入宅红纸帖：乔迁之喜·入宅大吉（2026-09-06 模板加全：合家成员+四段吉时+评分行）"""
    lines = []
    a = lines.append
    a(('', ''))
    a(('title', '乔迁之喜 · 入宅大吉'))
    a(('', ''))
    owners = e['_owners_map']
    zz = owners['zhaizhu']
    a(('h2', '【宅主】（主人）'))
    if zz:
        g = str(zz.get('gender') or '')
        _role = '乾造' if g == '男' else ('坤造' if g == '女' else '乾造/坤造')
        a(('body', f"{_role}：{_owner_sizhu_text(zz)}"))
    else:
        a(('body', '乾造/坤造：○○'))
    a(('', ''))
    # 合家成员（直系家属）：逐人标注与日课日冲的关系
    a(('h2', '【合家成员】（直系家属）'))
    chong_zhi = (e['_chong_gz'] or '　')[1:2]
    family = [o for o in owners['list']
              if o is not zz and o is not owners['xianming'] and o not in owners['zhushi']]
    if family:
        for o in family[:4]:
            nm = str(o.get('name') or '')
            gz = _owner_year_gz(o)
            _tag = '　⚠ 正冲，宜先行回避' if gz and gz[1:2] == chong_zhi else ''
            a(('body', f"{nm + '：' if nm else ''}{_owner_sizhu_text(o)}{_tag}"))
    else:
        a(('body', '需避忌冲克者：以家人年命与日课日冲核对为准'))
    a(('', ''))
    a(('h2', '● 移居入宅吉日'))
    a(('body', f"谨择 {e['_nian']}年 {e['_lunar_month']}{e['_lunar_day']} 移居入宅大利。"))
    a(('body', f"干　支：{e['_nian']}年　{e['_yue']}月　{e['_ri']}日　{e['_shi']}时"))
    sl = _score_line(e)
    if sl:
        a(('body', sl))
    a(('', ''))
    a(('h2', '【　吉　时　】'))
    a(('body', f"{_stage_label(e, 0)}：{_jishi_stage(e, 0)}"))
    a(('body', f"{_stage_label(e, 1)}：{_jishi_stage(e, 1)}"))
    a(('body', f"{_stage_label(e, 2)}：{_jishi_stage(e, 2)}"))
    a(('body', f"{_stage_label(e, 3)}：{_jishi_stage(e, 3)}"))
    a(('', ''))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}"))
    a(('small', f"（属{e['_chong_sx']}者入宅当日宜先行回避，待吉时过后再入）"))
    a(('', ''))
    lines.extend(_signature_lines(e))
    return lines


def compose_anzhang_lines(e):
    """安葬白纸帖：福荫后人·安葬大吉（2026-09-06 模板加全：仙命/孝眷/避忌实测+四段吉时+评分行）"""
    lines = []
    a = lines.append
    a(('', ''))
    a(('title', '福荫后人 · 安葬大吉'))
    a(('', ''))
    owners = e['_owners_map']
    xian = owners['xianming']
    a(('h2', '【仙命】（逝者）'))
    if xian:
        nm = str(xian.get('name') or '')
        g = str(xian.get('gender') or '')
        _t = '先妣' if g == '女' else '先考'
        a(('body', f"{_t}：{nm}" if nm else f"{_t}：○○公/○○氏"))
        a(('body', f"生年四柱：{_owner_sizhu_text(xian)}"))
    else:
        a(('body', '先考/先妣：○○'))
        a(('body', '生年四柱：○○'))
    a(('', ''))
    a(('h2', '【主事孝眷】（孝子/孝孙）'))
    zhushi = owners['zhushi']
    if zhushi:
        for o in zhushi[:3]:
            nm = str(o.get('name') or '孝子')
            a(('body', f"{nm}：{_owner_sizhu_text(o)}"))
    else:
        a(('body', f"主事人：{_zhushi_line(owners['zhushi'])}"))
    a(('', ''))
    a(('h2', '【墓穴坐向】'))
    a(('body', f"福地坐　{e.get('_shan_line') or '○○山○○向兼○○吉度分金'}"))
    a(('', ''))
    a(('h2', '● 破土安葬吉日'))
    a(('body', f"谨择 {e['_nian']}年 {e['_lunar_month']}{e['_lunar_day']} 破土安葬大利。"))
    a(('body', f"干　支：{e['_nian']}年　{e['_yue']}月　{e['_ri']}日　{e['_shi']}时"))
    sl = _score_line(e)
    if sl:
        a(('body', sl))
    a(('', ''))
    a(('h2', '【　吉　时　】'))
    a(('body', f"{_stage_label(e, 0)}：{_jishi_stage(e, 0)}"))
    a(('body', f"{_stage_label(e, 1)}：{_jishi_stage(e, 1)}"))
    a(('small', '（注：破土与兴工动土不同，宜静默肃穆）'))
    a(('body', f"{_stage_label(e, 2)}：{_jishi_stage(e, 2)}"))
    a(('body', f"{_stage_label(e, 3)}：{_jishi_stage(e, 3)}"))
    a(('', ''))
    a(('h2', '【重要避忌】'))
    hits = _zhongsang_hits(e)
    if hits:
        a(('body', f"⚠ 是日犯 {'、'.join(hits)}，慎用（宜另择）"))
    else:
        a(('body', '重丧日、复日、三丧日：本日均已避开'))
    ss = _year_sansha_text(e)
    if ss:
        a(('body', f"⚠ 岁煞在 {ss} 方，忌其方动锄"))
    a(('small', '（另需复核：入地空亡、冲仙命纳音）'))
    a(('', ''))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}"))
    a(('small', f"（属{e['_chong_sx']}者及生年与仙命相冲者宜暂避）"))
    a(('', ''))
    a(('h2', '呼　龙　文（安葬时诵读）'))
    a(('body', '日吉时良，天地开张，千里来龙，吉人安葬，山环水绕，金玉满堂。'))
    a(('', ''))
    lines.extend(_signature_lines(e))
    return lines


def compose_detail_lines(e):
    """单课详解帖：按 e['_template'] 分派到 6 类专版 + 通用红纸。"""
    t = e.get('_template') or 'common'
    if t == 'marriage':
        return compose_marriage_lines(e)
    if t == 'engagement':
        return compose_engagement_lines(e)
    if t == 'xiuzao':
        return compose_xiuzao_lines(e)
    if t == 'dongtu':
        return compose_dongtu_lines(e)
    if t == 'ruzhai':
        return compose_ruzhai_lines(e)
    if t == 'anzhang':
        return compose_anzhang_lines(e)
    # 其他（开业/出行/...）→ 红纸通用
    return _compose_common_detail_lines(e)


# ---------------- 嫁娶/安葬通用"白底·黑字·楷体居中"A4 打印模板 ----------------

_PRINT_MARRIAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
@page { size: A4 portrait; margin: 12mm 10mm; }
html, body { margin: 0; padding: 0; background: #ffffff; }
.paper {
  background: #ffffff;
  color: #111111;
  font-family: "KaiTi", "楷体", "STKaiti", "FZKai-Z03S", serif;
  width: 190mm;
  box-sizing: border-box;
  min-height: 273mm;
  margin: 0 auto;
  padding: 12mm 14mm;
  text-align: center;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.title { font-size: 34px; font-weight: bold; letter-spacing: 12px; }
.sub   { font-size: 18px; letter-spacing: 4px; }
.diamond { font-size: 16px; letter-spacing: 10px; color: #7a1010; }
.h2    { font-size: 24px; font-weight: bold; letter-spacing: 8px; }
.body  { font-size: 19px; line-height: 2.35; }
.small { font-size: 17px; line-height: 2.1; }
.sep   { font-size: 16px; color: #555; }
.warnhl { background: #FFFF00; color: #000000; }
.blank { font-size: 10px; }
</style>
</head>
<body onload="window.print()">
<div class="paper">
__BODY__
</div>
</body>
</html>
"""

_PRINT_WHITE_TEMPLATE = _PRINT_MARRIAGE_TEMPLATE  # 安葬同用白底


def _open_print_html(lines, title, paper='red'):
    """把行序列生成为 HTML 并用默认浏览器打开（自动弹出打印）。
    paper: 'red' → 红纸通用修造模板；'white' → 白底（嫁娶/安葬）模板。"""
    rows = []
    for style, text in lines:
        if not text:
            rows.append('<div class="blank">&nbsp;</div>')
            continue
        cls = _TAG_CLASS.get(style, 'body')
        if '⚠' in text:
            cls += ' warnhl'  # ⚠ 警告行黄底黑字（2026-09-10 用户要求）
        rows.append(f'<div class="{cls}">{html.escape(text).replace(" ", "&nbsp;")}</div>')
    tpl = _PRINT_WHITE_TEMPLATE if paper == 'white' else _PRINT_TEMPLATE
    doc = tpl.replace('__TITLE__', html.escape(title)).replace('__BODY__', '\n'.join(rows))
    path = os.path.join(tempfile.gettempdir(), '择日贴_打印.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(doc)
    webbrowser.open('file:///' + path.replace('\\', '/'))

def _fmt_owner(owner, role_label_cn):
    """按模板：乾造 辛卯年 历月 日 时 辛卯 甲寅 丙子 戊午 阳气:乙巳 / 坤造 壬辰年 历月 日 时 壬辰 甲寅 丙子 戊午 阴胎:乙巳
    其中年干支/四柱/阴阳胎来自 owner dict；'历月 日'模板图为占位形式，保持该书法风格。"""
    if not isinstance(owner, dict):
        owner = {}
    year_gz = owner.get('year_gz') or ''     # 如 辛卯
    # 月日时按模板风格仅显示占位（"历月 日 时"对应农历月/日/时；若无具体农历输入则留空占位）
    lm = str(owner.get('lunar_month') or '') or ''
    ld = str(owner.get('lunar_day') or '') or ''
    lh = str(owner.get('lunar_hour') or '') or ''
    # 若没显式给农历月日，则用输入变量再拼（或直接退化为占位空字符串）
    if not (lm and ld):
        try:
            ys = str(owner.get('year') or '')
            ms = str(owner.get('month') or '')
            ds = str(owner.get('day') or '')
            hs = str(owner.get('hour') or '')
            if ys and ms and ds:
                try:
                    from .高精度农历转换 import HighPrecisionLunar
                    _hp = HighPrecisionLunar()
                    try:
                        l = _hp.solar_to_lunar_with_check(int(ys), int(ms), int(ds))
                        if isinstance(l, dict):
                            m_ = l.get('month')
                            d_ = l.get('day')
                            leap_ = l.get('is_leap', False)
                            if m_:
                                lm = ('闰' if leap_ else '') + _CN_MONTHS[int(m_) - 1]
                            if d_:
                                ld = _lunar_day_str(int(d_))
                            # 时
                            h_ = int(hs) if hs else 12
                            from .今日黄历 import DI_ZHI_ORDER
                            shi_gz_zhi = DI_ZHI_ORDER[(h_ + 1) // 2 % 12] if (h_ is not None) else ''
                            if shi_gz_zhi:
                                lh = {'子': '子', '丑': '丑', '寅': '寅', '卯': '卯', '辰': '辰', '巳': '巳',
                                      '午': '午', '未': '未', '申': '申', '酉': '酉', '戌': '戌', '亥': '亥'}.get(shi_gz_zhi, '')
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception:
            pass
    sizhu = owner.get('sizhu') or ''    # "辛卯 甲寅 丙子 戊午"
    # 阳气/阴胎
    extra = owner.get('yangqi') if role_label_cn == '乾造' else owner.get('yintai')
    extra_label = '阳气' if role_label_cn == '乾造' else '阴胎'
    # 组合：乾造 辛卯年 历月 日 时 辛卯 甲寅 丙子 戊午 阳气:乙巳
    parts = [role_label_cn]
    if year_gz:
        parts.append(f'{year_gz}年')
    # 农历月日时（若已解析）
    if lm:
        parts.append(f'{lm}')
    if ld:
        parts.append(f'{ld}日')
    if lh:
        parts.append(f'{lh}时')
    elif lm or ld:
        # 只要写了月日就加占位"时"对齐模板
        pass
    if sizhu:
        parts.append(sizhu)
    if extra and extra not in ('未知', ''):
        parts.append(f'{extra_label}:{extra}')
    # 去掉空串
    parts = [p for p in parts if p]
    return ' '.join(parts)


# 择日依据典籍版本（2026-09-06用户确认；与统一版主程序 APP_VERSION 口径一致）
DIANJI_BANBEN = '协纪辨方书'

# 嫁娶吉帖关键吉神关键词（长词在前，防止"天德"抢先匹配"天德贵人"）
_KEY_GOD_KWS = ['不将日', '天德贵人', '月德贵人', '天德合', '月德合', '天乙贵人',
                '天赦', '天愿', '天喜', '天恩', '月恩', '天德', '月德']


def _extract_key_gods(e):
    """从 reason（嫁娶要点等）+ 结果表吉神列提取关键吉神，'、'连接（最多4个），无则返回''"""
    text = str(e.get('reason') or '')
    jcol = str(e.get('jishen') or '').strip()
    if jcol and jcol != '-':
        text += '；' + jcol
    found = []
    for kw in _KEY_GOD_KWS:
        if kw in text:
            found.append(kw)
            text = text.replace(kw, '')
    if not found:
        return ''
    return '吉　神：' + '、'.join(found[:4])


def compose_marriage_lines(e):
    """嫁娶吉帖行序列（[(样式, 文本)]）：白底传统吉帖风格，结构：
    标题 → 乾造 → 坤造 → 夫星子星 → 嫁娶结婚吉日 → 谨择××年嫁娶结婚大利 → 干支/评分 →
    【吉时】发轿/回轿/拜堂 → 冲·煞 → 吉神 → 择日师/择日依据 → 岁次××年 月 谨识"""
    lines = []
    a = lines.append
    groom = e.get('groom') if isinstance(e.get('groom'), dict) else {}
    bride = e.get('bride') if isinstance(e.get('bride'), dict) else {}

    a(('', ''))
    a(('title', '天　配　良　缘　百　年　好　合'))
    a(('', ''))
    a(('body', _fmt_owner(groom, '乾造')))
    a(('', ''))
    a(('body', _fmt_owner(bride, '坤造')))
    a(('', ''))
    # 夫星：子星：
    fu = e.get('fu_xing') or ''
    zi = e.get('zi_xing') or ''
    fu_str = f"夫星：{fu}" if fu else "夫星："
    zi_str = f"子星：{zi}" if zi else "子星："
    a(('h2', f"{fu_str}　　　{zi_str}"))
    a(('', ''))
    a(('h2', '嫁　娶　结　婚　吉　日'))
    a(('', ''))
    # 谨择辛卯年 历月 日 嫁娶结婚大利。
    # 年月以当年农历干支年（日课年柱）、择日农历月日
    ln_year = e.get('_lunar_year') or e['_nian']   # 辛卯
    a(('body', f"谨择{ln_year}年{e['_lunar_month']}{e['_lunar_day']}嫁娶结婚大利。"))
    a(('', ''))
    # 干支：
    a(('body', f"干　支：{e['_nian']}年　{e['_yue']}月　{e['_ri']}日　{e['_shi']}时"))
    a(('', ''))
    # 评分行（2026-09-06用户建议：结论更有数据支撑）
    _sc = str(e.get('score') or '').strip()
    _lv = str(e.get('level') or '').strip()
    if _sc or _lv:
        if _sc and _lv:
            a(('body', f"评　分：{_sc}分　{_lv}"))
        elif _sc:
            a(('body', f"评　分：{_sc}分"))
        else:
            a(('body', f"评　分：{_lv}"))
        a(('', ''))
    a(('h2', '【　吉　时　】'))
    a(('', ''))
    # 发轿/回轿/拜堂：按当日实际可用吉时逐条输出（001 §194 挂账4，2026-10-28
    # 拍板）。原实现不足 3 条时用固定「辰/寅/酉」占位补齐，可能正好撞上新人
    # 年命（把凶时印成大吉吉时）；现一律按实际条数输出，绝不拉凶时充数，
    # 当日无可用吉时时提示谨慎择时。
    jishi = e.get('_jishi', []) or []
    def _jishi_str(j):
        return f"{j['ganzhi']}时（{j['range']}）　{j['grade']}"
    if jishi:
        for _i, _j in enumerate(jishi[:3]):
            a(('body', f"{_stage_label(e, _i)}：{_jishi_str(_j)}"))
            a(('', ''))
    else:
        a(('body', '今日吉时有限，请谨慎选择。'))
        a(('', ''))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}　（属{e['_chong_sx']}者当日宜避之）"))
    a(('', ''))
    # 关键吉神行（2026-09-06用户建议：不将日/天德/月德等单独一行说明）
    _god_line = _extract_key_gods(e)
    if _god_line:
        a(('body', _god_line))
        a(('', ''))
    a(('body', "择日师：廖贵雄"))
    a(('', ''))
    # 择日依据（2026-09-06用户建议：标注所用典籍版本）
    a(('small', f"择日依据：{DIANJI_BANBEN}"))
    a(('', ''))
    now = datetime.now()
    # 岁次辛丑  年 月 谨识（年月日干支采用当年+择日当日年柱）
    nian = e.get('_nian') or ''
    a(('small', f"岁次{nian}　{_cn_year_num(now.year)}年{_cn_month_num(now.month)}月　谨识"))
    return lines


def compose_marriage(e):
    """纯文本版嫁娶帖（复制/导出）"""
    return '\n'.join(t for _, t in compose_marriage_lines(e))


def _compose_common_detail_lines(e):
    """红纸通用帖：择吉选日（修造/动土/安葬/开业/其他通用用事）"""
    lines = []
    a = lines.append
    a(('dia', '◆　◆　◆'))
    a(('', ''))
    a(('title', '择　吉　选　日'))
    a(('sub', '─ 黄道吉日通书 ─'))
    a(('', ''))
    a(('dia', '◆　◆　◆'))
    a(('', ''))
    a(('h2', '谨　择'))
    a(('', ''))
    a(('body', f"公　　元：{e['_dt'].year}年{e['_dt'].month:02d}月{e['_dt'].day:02d}日"))
    a(('body', f"岁　　次：{e['_nian']}　肖{e['_shengxiao']}"))
    a(('body', f"农　　历：{e['_lunar_str']}"))
    a(('body', f"干　　支：{e['_nian']}年 {e['_yue']}月 {e['_ri']}日 {e['_shi']}时"))
    a(('body', f"星　　期：{e['_week']}"))
    a(('sep', '─' * 30))
    a(('h2', '【 吉　时 】'))
    if e['_jishi']:
        labels = ['首选', '次选', '备选', '又备']
        for i, h in enumerate(e['_jishi']):
            tags = f"（{h['tags']}）" if h['tags'] else ''
            a(('body', f"{labels[i]}：{h['ganzhi']}时（{h['range']}）　{h['grade']}{tags}"))
    else:
        a(('body', '本日无特吉时辰，酌情取用'))
    a(('sep', '─' * 30))
    yi = '　'.join(e['_yi']) if e['_yi'] else '—'
    ji = '　'.join(e['_ji']) if e['_ji'] else '—'
    a(('body', f"【 宜 】{yi}"))
    a(('body', f"【 忌 】{ji}"))
    a(('sep', '─' * 30))
    a(('h2', '【 吉神方位 】'))
    a(('body', f"财神：{e['_cai']}"))
    a(('body', f"喜神：{e['_xi']}"))
    a(('body', f"福神：{e['_fu']}"))
    a(('body', f"贵神：{e['_gui']}"))
    a(('sep', '─' * 30))
    a(('body', f"冲：{e['_chong_gz']}{e['_chong_sx']}　煞：{e['_sha']}　（属{e['_chong_sx']}者当日宜避之）"))
    a(('sep', '─' * 30))
    event = e.get('event_type') or '—'
    owners = e.get('owners') or '—'
    if owners in ('-', '无', ''):
        owners = '—'
    a(('body', f"用事：{event}　　　事主：{owners}"))
    level = e.get('level') or '—'
    score = str(e.get('score') or '')
    score_part = f"　{score}分" if score else ''
    a(('body', f"评级：{level}{score_part}"))
    a(('sep', '─' * 30))
    now = datetime.now()
    a(('small', '择日师：廖贵雄'))
    a(('small', f"岁次{e['_nian']}　{_cn_year_num(now.year)}年{_cn_month_num(now.month)}月　谨识"))
    return lines


def compose_summary_lines(entries):
    """择日总录行序列 [(样式, 文本)]——多课汇总 + 自动择定首选/备选 + 评语。
    婚嫁类多课：每课标题已自动按嫁娶模板排版；总录保留红纸通用表头。"""
    if not entries:
        return [('body', '（择日贴为空——在择日结果中右键日课即可加入）')]
    ordered = sorted(entries, key=lambda x: _score_num(x.get('score')), reverse=True)
    first = ordered[0]
    second = ordered[1] if len(ordered) > 1 else None

    event_types = {e.get('event_type') or '—' for e in entries}
    owners_set = {str(e.get('owners') or '—').replace('无', '—') for e in entries} - {'—'}
    event_str = '、'.join(sorted(event_types))
    owners_str = '、'.join(sorted(owners_set)) if owners_set else '—'

    lines = []
    a = lines.append
    a(('dia', '◆　◆　◆'))
    a(('', ''))
    a(('title', '择　日　总　录'))
    a(('sub', '─ 候选吉日一览 ─'))
    a(('', ''))
    a(('dia', '◆　◆　◆'))
    a(('', ''))
    a(('body', f"用事类别：{event_str}　　　事主/命主：{owners_str}"))
    a(('', ''))
    a(('body', '序　公历日期　　　干支日　星期　吉时首选　　　　　　评级'))
    for i, e in enumerate(ordered):
        num = '〇一二三四五六七八九十'[i] if i < 11 else str(i + 1)
        js = e['_jishi'][0] if e['_jishi'] else None
        jishi_str = f"{js['ganzhi']}时 {js['grade']}" if js else '—'
        level = e.get('level') or ''
        score = str(e.get('score') or '')
        rating = ' '.join(x for x in (level, f"{score}分" if score else '') if x).strip() or '—'
        a(('body', f"{num}　{e['date']}　{e['_ri']}　　{e['_week'][2]}　　{jishi_str}　　　{rating}".rstrip()))
    a(('', ''))
    a(('sep', '─' * 40))
    a(('h2', '【 最终择定 】'))

    def _fmt_choice(e):
        js = e['_jishi'][0] if e['_jishi'] else None
        jishi_str = f"　吉时：{js['ganzhi']}时" if js else ''
        return f"农历{e['_lunar_str']}（公历{e['date']}）　{e['_ri']}日{jishi_str}"

    a(('body', f"首选吉日：{_fmt_choice(first)}"))
    if second:
        a(('body', f"备选吉日：{_fmt_choice(second)}"))
    a(('', ''))
    a(('h2', '【 择日评语 】'))
    first_desc = f"{first['date']}（{first['_ri']}日，{first.get('score') or '—'}分）"
    if second:
        a(('body', f"兹选得吉课二则：首选{first_desc}，备选{second['date']}（{second['_ri']}日，"
                   f"{second.get('score') or '—'}分）。"))
    else:
        a(('body', f"兹选得吉课一则：{first_desc}。"))
    a(('body', '诸课四柱纯清、用事相宜，吉时已列，依时行事，百事亨通。'))
    a(('small', '（本评语由软件自动生成，仅供参考）'))
    a(('', ''))
    now = datetime.now()
    nian = first['_nian']
    a(('small', '择日师：廖贵雄'))
    a(('small', f"岁次{nian}　{_cn_year_num(now.year)}年{_cn_month_num(now.month)}月　谨识"))
    return lines


def compose_summary(entries):
    """纯文本版总录（复制/导出用）"""
    return '\n'.join(t for _, t in compose_summary_lines(entries))


def _score_num(score):
    """评分转数值（排序用，非数字按0）"""
    try:
        return float(str(score).replace('分', ''))
    except (ValueError, TypeError):
        return 0.0


# ---------------- 红纸日课单打印（传统红纸黑字、居中、A4直打） ----------------
RED_PAPER = '#C11B17'

_TAG_CLASS = {'title': 'title', 'sub': 'sub', 'h2': 'h2', 'body': 'body',
              'small': 'small', 'dia': 'diamond', 'sep': 'sep'}

_PRINT_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
@page { size: A4 portrait; margin: 8mm; }
html, body { margin: 0; padding: 0; background: #C11B17; }
.paper {
  background: #C11B17;
  color: #1a1a1a;
  font-family: "KaiTi", "楷体", "STKaiti", "FZKai-Z03S", serif;
  width: 190mm;
  box-sizing: border-box;
  min-height: 276mm;
  margin: 0 auto;
  padding: 10mm 6mm;
  text-align: center;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.title { font-size: 38px; font-weight: bold; letter-spacing: 14px; }
.sub { font-size: 19px; letter-spacing: 4px; }
.diamond { font-size: 17px; letter-spacing: 10px; }
.h2 { font-size: 25px; font-weight: bold; letter-spacing: 8px; }
.body { font-size: 19px; line-height: 2.2; }
.small { font-size: 17px; line-height: 2.05; }
.sep { font-size: 16px; }
.warnhl { background: #FFFF00; color: #000000; }
.blank { font-size: 10px; }
</style>
</head>
<body onload="window.print()">
<div class="paper">
__BODY__
</div>
</body>
</html>
"""


class ZeriTieWindow:
    """择日贴窗口"""

    def __init__(self, parent):
        self.parent = parent
        self.entries = []

        self.window = tk.Toplevel(parent)
        self.window.title("择日贴")
        self.window.geometry("880x720")
        self.window.minsize(720, 560)
        self.window.transient(parent)

        # ---- 工具栏 ----
        bar = ttk.Frame(self.window, padding="6")
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="手动加课", command=self.manual_add).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="改吉时", command=self.edit_jishi).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="打印本课", command=self.print_detail).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="打印总录", command=self.print_summary).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="复制本课", command=self.copy_detail).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="复制总录", command=self.copy_summary).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="导出TXT", command=self.export_txt).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="删除选中", command=self.remove_selected).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="清空", command=self.clear_all).pack(side=tk.LEFT, padx=3)
        self.count_var = tk.StringVar(value="共 0 课")
        ttk.Label(bar, textvariable=self.count_var).pack(side=tk.RIGHT, padx=6)

        # ---- 选项卡 ----
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        # 单课详解
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text=" 单课详解（择吉选日帖） ")
        left = ttk.Frame(tab1, padding="4")
        left.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(left, text="已收日课").pack(anchor=tk.W)
        self.listbox = tk.Listbox(left, width=26, exportselection=False)
        self.listbox.pack(fill=tk.Y, expand=True, side=tk.TOP)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.show_detail())
        right = ttk.Frame(tab1, padding="4")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 红纸日课单：红底黑字、楷体、居中
        self.detail_text = tk.Text(right, wrap=tk.WORD, font=("楷体", 17),
                                   bg=RED_PAPER, fg='#1a1a1a', padx=14, pady=12,
                                   state=tk.DISABLED)
        dsb = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=dsb.set)
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_text.bind('<Double-1>', self._on_detail_dclick)
        for name, kw in (('ctr', {'justify': tk.CENTER}),
                         ('title', {'justify': tk.CENTER, 'font': ("楷体", 24, 'bold')}),
                         ('sub', {'justify': tk.CENTER, 'font': ("楷体", 15)}),
                         ('h2', {'justify': tk.CENTER, 'font': ("楷体", 18, 'bold')}),
                         ('body', {'justify': tk.CENTER, 'font': ("楷体", 16)}),
                         ('small', {'justify': tk.CENTER, 'font': ("楷体", 15)}),
                         ('dia', {'justify': tk.CENTER, 'font': ("楷体", 15)}),
                         ('warnhl', {'justify': tk.CENTER, 'background': '#FFFF00', 'foreground': '#000000'}),
                         ('sep', {'justify': tk.CENTER, 'font': ("楷体", 14), 'foreground': '#7a1010'})):
            self.detail_text.tag_configure(name, **kw)

        # 择日总录（红纸样式）
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text=" 择日总录 ")
        self.summary_text = tk.Text(tab2, wrap=tk.WORD, font=("楷体", 17),
                                    bg=RED_PAPER, fg='#1a1a1a', padx=14, pady=12,
                                    state=tk.DISABLED)
        ssb = ttk.Scrollbar(tab2, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=ssb.set)
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ssb.pack(side=tk.RIGHT, fill=tk.Y)
        for name, kw in (('ctr', {'justify': tk.CENTER}),
                         ('title', {'justify': tk.CENTER, 'font': ("楷体", 24, 'bold')}),
                         ('sub', {'justify': tk.CENTER, 'font': ("楷体", 15)}),
                         ('h2', {'justify': tk.CENTER, 'font': ("楷体", 18, 'bold')}),
                         ('body', {'justify': tk.CENTER, 'font': ("楷体", 16)}),
                         ('small', {'justify': tk.CENTER, 'font': ("楷体", 15)}),
                         ('dia', {'justify': tk.CENTER, 'font': ("楷体", 15)}),
                         ('warnhl', {'justify': tk.CENTER, 'background': '#FFFF00', 'foreground': '#000000'}),
                         ('sep', {'justify': tk.CENTER, 'font': ("楷体", 14), 'foreground': '#7a1010'})):
            self.summary_text.tag_configure(name, **kw)

    # ---------- 数据 ----------
    def add_entry(self, entry):
        """加入/更新一课（同日期同用事自动覆盖）"""
        try:
            e = prepare_entry(entry)
        except Exception as ex:
            messagebox.showerror("错误", f"日课数据无效：{ex}")
            return
        key = (e['date'], e.get('event_type') or '')
        self.entries = [x for x in self.entries if (x['date'], x.get('event_type') or '') != key]
        self.entries.append(e)
        self.refresh()
        # 定位到新课
        self.notebook.select(0)
        dates = [x['date'] for x in self.entries]
        if e['date'] in dates:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(dates.index(e['date']))
            self.show_detail()
        self.window.deiconify()
        self.window.lift()

    def refresh(self):
        ordered = sorted(self.entries, key=lambda x: x['date'])
        self.entries = ordered
        self.listbox.delete(0, tk.END)
        for e in ordered:
            js = e['_jishi'][0] if e['_jishi'] else None
            jishi_str = f" {js['ganzhi']}时{js['grade']}" if js else ''
            self.listbox.insert(tk.END, f"{e['date']}　{e['_ri']}日{jishi_str}")
        self.count_var.set(f"共 {len(self.entries)} 课")
        self.render_summary()

    def _current(self):
        sel = self.listbox.curselection()
        if sel and 0 <= sel[0] < len(self.entries):
            return self.entries[sel[0]]
        return None

    # ---------- 视图 ----------
    def _fill_text(self, widget, lines):
        """红纸居中渲染行序列"""
        widget.configure(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        for style, text in lines:
            if text:
                if '⚠' in text:
                    # ⚠ 警告行黄底黑字（2026-09-10 用户要求）
                    widget.insert(tk.END, text + '\n', ('ctr', style, 'warnhl'))
                else:
                    widget.insert(tk.END, text + '\n', ('ctr', style))
            else:
                widget.insert(tk.END, '\n', ('ctr',))
        widget.configure(state=tk.DISABLED)

    def show_detail(self):
        e = self._current()
        lines = compose_detail_lines(e) if e else []
        # 只有安葬用白纸（黑字）；其他（嫁娶/订婚/修造/动土/入宅/通用）全部红纸
        tpl = (e.get('_template') or '') if e else ''
        is_white = (tpl == 'anzhang')
        bg = '#ffffff' if is_white else RED_PAPER
        fg = '#111111' if is_white else '#1a1a1a'
        self.detail_text.configure(bg=bg, fg=fg)
        self._fill_text(self.detail_text, lines)

    def render_summary(self):
        self._fill_text(self.summary_text, compose_summary_lines(self.entries))

    # ---------- 打印 ----------
    def print_detail(self):
        """打印当前日课单：按 template 分派 → 嫁娶/安葬=白底；其余红纸。"""
        e = self._current()
        if not e:
            messagebox.showinfo("提示", "请先在左侧选择一课")
            return
        tpl = e.get('_template') or ''
        paper = 'white' if tpl == 'anzhang' else 'red'
        title_map = {
            'marriage':   f"嫁娶结婚吉日 {e['date']}",
            'engagement': f"订婚纳彩请期吉课 {e['date']}",
            'xiuzao':     f"兴工修造吉课 {e['date']}",
            'dongtu':     f"兴工动土吉课 {e['date']}",
            'ruzhai':     f"乔迁入宅吉课 {e['date']}",
            'anzhang':    f"福地进金安葬吉课 {e['date']}",
            'common':     f"择吉选日 {e['date']}",
        }
        title = title_map.get(tpl, title_map['common'])
        _open_print_html(compose_detail_lines(e), title, paper=paper)

    def print_summary(self):
        """打印择日总录（红纸A4，浏览器自动弹出打印）"""
        if not self.entries:
            messagebox.showinfo("提示", "择日贴为空")
            return
        _open_print_html(compose_summary_lines(self.entries), "择日总录")

    # ---------- 操作 ----------
    def manual_add(self):
        win = tk.Toplevel(self.window)
        win.title("手动加课")
        win.geometry("300x170")
        win.transient(self.window)
        win.grab_set()
        ttk.Label(win, text="公历日期(YYYY-MM-DD)：").grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(win, textvariable=date_var, width=14).grid(row=0, column=1, pady=8)
        ttk.Label(win, text="时辰：").grid(row=1, column=0, padx=8, sticky=tk.W)
        shichen_var = tk.StringVar(value='午时(11-13)')
        ttk.Combobox(win, textvariable=shichen_var, values=list(SHICHEN_HOURS.keys()),
                     width=12, state='readonly').grid(row=1, column=1)
        ttk.Label(win, text="用事：").grid(row=2, column=0, padx=8, sticky=tk.W)
        event_var = tk.StringVar(value='')
        ttk.Entry(win, textvariable=event_var, width=14).grid(row=2, column=1)

        def _ok():
            entry = {'date': date_var.get().strip(),
                     'event_type': event_var.get().strip() or None,
                     'sizhu': ''}
            self.add_entry(entry)
            win.destroy()

        ttk.Button(win, text="加入", command=_ok).grid(row=3, column=0, columnspan=2, pady=10)

    # ---------- 吉时手动修改（2026-09-07） ----------
    def _on_detail_dclick(self, ev):
        """双击详情帖吉时行 → 打开修改对话框"""
        e = self._current()
        if not e:
            return
        try:
            idx = self.detail_text.index(f"@{ev.x},{ev.y}")
            line = self.detail_text.get(f"{idx} linestart", f"{idx} lineend").strip()
        except Exception:
            return
        if any(line.startswith(lab) for lab in _stage_labels_effective(e)):
            self.edit_jishi()

    def edit_jishi(self):
        """手动修改本课吉时：按模板分段，每段可任选当日十二时辰（下拉含吉凶等级与吉神标注），或恢复自动。"""
        e = self._current()
        if not e:
            messagebox.showinfo("提示", "请先在左侧选择一课")
            return
        labels = _jishi_stage_labels(e.get('_template') or '')
        hours = calc_shichen_jixiong(e['_ri'][0], e['_ri'][1], e['_nian'][1], e['_yue'][1])
        hours = sorted(hours, key=lambda x: -x['score'])
        opts = ['（自动）']
        opt_zhi = [None]
        for h in hours:
            tags = '/'.join(h['tags'][:2]) if h.get('tags') else ''
            opts.append(f"{h['ganzhi']}时 {h.get('level') or '平'} {_SHICHEN_RANGE.get(h['zhi'], '')}"
                        + (f" {tags}" if tags else ''))
            opt_zhi.append(h['zhi'])
        js = e.get('_jishi') or []
        ov_cur = e.get('jishi_override') or {}

        win = tk.Toplevel(self.window)
        win.title("修改吉时")
        win.transient(self.window)
        win.grab_set()
        frm = ttk.Frame(win, padding="10")
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text=f"{e['date']}　{e.get('event_type') or '通用'}　—　吉时可手动指定（选“（自动）”恢复推荐）；“事项文字”可自由修改，清空或改回默认即恢复"
                  ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
        rows = []
        lab_vars = []
        for i, lab in enumerate(labels):
            cur_txt = '—'
            if i < len(js):
                j = js[i]
                cur_txt = f"{j['ganzhi']}时（{j['range']}）{j['grade']}" + ('〔手动〕' if j.get('manual') else '')
            r1 = i * 2 + 1
            ttk.Label(frm, text=lab).grid(row=r1, column=0, sticky=tk.W, padx=(0, 12), pady=2)
            ttk.Label(frm, text=f"当前：{cur_txt}").grid(row=r1, column=1, sticky=tk.W, padx=(0, 12), pady=2)
            var = tk.StringVar(value='（自动）')
            _set = ov_cur.get(str(i)) or ov_cur.get(i)
            if _set and _set in opt_zhi:
                var.set(opts[opt_zhi.index(_set)])
            ttk.Combobox(frm, textvariable=var, values=opts, width=38,
                         state='readonly').grid(row=r1, column=2, sticky=tk.W, pady=2)
            rows.append(var)
            lvar = tk.StringVar(value=_stage_label(e, i))
            ttk.Label(frm, text="事项文字：").grid(row=r1 + 1, column=1, sticky=tk.E, padx=(0, 4), pady=(0, 4))
            ttk.Entry(frm, textvariable=lvar, width=40).grid(row=r1 + 1, column=2, sticky=tk.W, pady=(0, 4))
            lab_vars.append(lvar)

        def _apply(override, label_ov=None):
            raw = {k: v for k, v in e.items() if not str(k).startswith('_')}
            if override:
                raw['jishi_override'] = override
            else:
                raw.pop('jishi_override', None)
            if label_ov:
                raw['jishi_labels'] = label_ov
            else:
                raw.pop('jishi_labels', None)
            self.add_entry(raw)
            win.destroy()

        def _ok():
            new_ov = {}
            for i, var in enumerate(rows):
                v = var.get()
                if v in opts:
                    z = opt_zhi[opts.index(v)]
                    if z:
                        new_ov[str(i)] = z
            new_lab = {}
            for i, lv in enumerate(lab_vars):
                txt = (lv.get() or '').strip()
                default = labels[i] if i < len(labels) else ''
                if txt and txt != default:
                    new_lab[str(i)] = txt
            _apply(new_ov, new_lab)

        btns = ttk.Frame(frm)
        btns.grid(row=len(labels) * 2 + 1, column=0, columnspan=3, pady=(12, 0))
        ttk.Button(btns, text="确定", command=_ok).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="全部恢复自动", command=lambda: _apply({}, {})).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="取消", command=win.destroy).pack(side=tk.LEFT, padx=6)

    def copy_detail(self):
        e = self._current()
        if not e:
            messagebox.showinfo("提示", "请先在左侧选择一课")
            return
        self.window.clipboard_clear()
        self.window.clipboard_append(compose_detail(e))
        messagebox.showinfo("完成", "本课已复制到剪贴板")

    def copy_summary(self):
        if not self.entries:
            messagebox.showinfo("提示", "择日贴为空")
            return
        self.window.clipboard_clear()
        self.window.clipboard_append(compose_summary(self.entries))
        messagebox.showinfo("完成", "总录已复制到剪贴板")

    def export_txt(self):
        if not self.entries:
            messagebox.showinfo("提示", "择日贴为空")
            return
        fname = filedialog.asksaveasfilename(
            title="导出择日贴", defaultextension=".txt",
            initialfile=f"择日贴_{datetime.now().strftime('%Y%m%d')}.txt",
            filetypes=[("文本文件", "*.txt")])
        if not fname:
            return
        content = ''
        for e in self.entries:
            content += compose_detail(e) + '\n\n' + '=' * 46 + '\n\n'
        content += '\n\n' + compose_summary(self.entries) + '\n'
        with open(fname, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        messagebox.showinfo("完成", f"已导出：{fname}")

    def remove_selected(self):
        e = self._current()
        if not e:
            messagebox.showinfo("提示", "请先在左侧选择一课")
            return
        self.entries = [x for x in self.entries if x['date'] != e['date']]
        self.refresh()
        self.show_detail()

    def clear_all(self):
        if not self.entries:
            return
        if messagebox.askyesno("确认", f"确定清空全部 {len(self.entries)} 课吗？"):
            self.entries = []
            self.refresh()
            self.show_detail()


def show_zeri_tie(parent):
    """打开（或置顶已打开的）择日贴窗口"""
    win = getattr(parent, '_zeri_tie_window', None)
    if win is None or not tk.Toplevel.winfo_exists(win.window):
        win = ZeriTieWindow(parent)
        parent._zeri_tie_window = win
    else:
        win.window.deiconify()
        win.window.lift()
    return win
