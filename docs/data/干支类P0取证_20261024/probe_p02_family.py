# -*- coding: utf-8 -*-
"""P0-2 年家族 16 项：软件起例 vs 主锚（协纪卷三·义例一）逐支对勘（只读）

判据：五档四分法（✅全等 / ⚠️语义等价 / ⚠️部分匹配 / ❌不符 / —无载）。
      主锚值取自《协纪辨方书》卷三 义例一（C:\\Temp\\xj_full\\279221.txt），
      与《御定星历考原》359077 逐字互校（黄幡/豹尾/大耗/小耗四神两库同文）。

输出：p02_family.json（软件 12 年支实际取值 + 主锚取值 + 2026 天次/分值）
用法：python probe_p02_family.py
"""
import datetime as dt
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu                      # noqa: E402
from modules.事项标准 import get_shensha_checker, shensha_score      # noqa: E402

ZH = '子丑寅卯辰巳午未申酉戌亥'
EVENTS = ['嫁娶', '修造', '动土', '拆舍', '入宅', '移徙', '作灶', '安床',
          '开业', '出行', '安葬', '入学', '求医', '签约', '通用']

# 主锚（协纪卷三·义例一）逐神起例，返回 {年支: 值}；
# '维' 表示主锚取四维方位（艮巽坤乾），与地支值域不同域 → 不可直接对等。
def anchor_table(kind):
    t = {}
    for i, y in enumerate(ZH):
        if kind == 'huangfan':      # 三合墓辰
            t[y] = ['戌', '未', '辰', '丑'][i % 4] if False else {
                '寅': '戌', '午': '戌', '戌': '戌',
                '亥': '未', '卯': '未', '未': '未',
                '申': '辰', '子': '辰', '辰': '辰',
                '巳': '丑', '酉': '丑', '丑': '丑'}[y]
        elif kind == 'baowei':      # 黄幡对冲
            t[y] = ZH[(ZH.index(anchor_table('huangfan')[y]) + 6) % 12]
        elif kind == 'sangmen':     # 岁前二辰
            t[y] = ZH[(i + 2) % 12]
        elif kind == 'diaoke':      # 岁后二辰（协纪：子年在戌）
            t[y] = ZH[(i - 2) % 12]
        elif kind == 'guanfu':      # 岁前四辰（协纪：子年在辰）
            t[y] = ZH[(i + 4) % 12]
        elif kind == 'chuguan':     # 与官符同位
            t[y] = anchor_table('guanfu')[y]
        elif kind == 'canguan':     # 岁方墓库：东→戌 南→丑 西→辰 北→未
            t[y] = {'寅': '戌', '卯': '戌', '辰': '戌',
                    '巳': '丑', '午': '丑', '未': '丑',
                    '申': '辰', '酉': '辰', '戌': '辰',
                    '亥': '未', '子': '未', '丑': '未'}[y]
        elif kind == 'wugui':       # 子年在辰，逆行十二辰
            t[y] = ZH[(4 - i) % 12]
        elif kind == 'suixing':     # 三刑（曾门经：申子辰刑寅卯辰）
            t[y] = {'申': '寅', '子': '卯', '辰': '辰',
                    '寅': '巳', '午': '午', '戌': '未',
                    '巳': '申', '酉': '酉', '丑': '戌',
                    '亥': '亥', '卯': '子', '未': '丑'}[y]
        elif kind == 'lishi':       # 力士取四维（东→东南/巽…），与地支不同域
            t[y] = {'寅': '巽', '卯': '巽', '辰': '巽',
                    '巳': '坤', '午': '坤', '未': '坤',
                    '申': '乾', '酉': '乾', '戌': '乾',
                    '亥': '艮', '子': '艮', '丑': '艮'}[y]
        elif kind == 'dahuo':       # 伏兵/大祸取天干（黎干：寅午戌大祸癸…）
            t[y] = {'寅': '癸', '午': '癸', '戌': '癸',
                    '申': '丁', '子': '丁', '辰': '丁',
                    '亥': '辛', '卯': '辛', '未': '辛',
                    '巳': '乙', '酉': '乙', '丑': '乙'}[y]
    return t


SOFTWARE = [
    ('黄幡', '_is_huangfan', 'huangfan'),
    ('豹尾', '_is_baowei', 'baowei'),
    ('丧门', '_is_sangmen', 'sangmen'),
    ('吊客', '_is_diaoke', 'diaoke'),
    ('官符', '_is_guanfu', 'guanfu'),
    ('畜官', '_is_chuguansheng', 'chuguan'),
    ('蚕官', '_is_canguan', 'canguan'),
    ('五鬼', '_is_wugui', 'wugui'),
    ('岁刑', '_is_suixing', 'suixing'),
    ('力士', '_is_lishi', 'lishi'),
    ('大祸', '_is_dahuo', 'dahuo'),
    ('岁害', '_is_suihai', None),
    ('天耗', '_is_tianhao', None),
    ('地耗', '_is_dihao', None),
]
NOCANON = ['岁害', '天耗', '地耗']
NOT_IMPL = ['蚕命', '死符', '白虎']
# 破败（年干纳甲卦位）与 软件「年月冲」不同域，另见报告 §2.4，不参与逐支对勘


def sw_values():
    """用各通道 checker 的谓词实测：每个年支命中哪个日支。"""
    ck = get_shensha_checker('通用')
    out = {}
    for name, meth, _ in SOFTWARE:
        fn = getattr(ck, meth, None)
        vals = []
        for y in ZH:
            sz = {'year_gan': '甲', 'year_zhi': y, 'month_zhi': '寅',
                  'day_gan': '甲', 'day_zhi': '', 'day_pillar': '', 'hour_zhi': ''}
            hit = None
            for d in ZH:
                sz['day_zhi'] = d
                sz['day_pillar'] = '甲' + d
                try:
                    if fn and fn(sz):
                        hit = d
                        break
                except Exception as e:                       # noqa: BLE001
                    hit = 'ERR:%s' % e
                    break
            vals.append(hit)
        out[name] = dict(zip(ZH, vals))
    return out


def days_2026():
    cnt = {}
    d = dt.date(2026, 1, 1)
    while d <= dt.date(2026, 12, 31):
        dz = calculate_sizhu(d, 10, 0)['day_zhi']
        cnt[dz] = cnt.get(dz, 0) + 1
        d += dt.timedelta(days=1)
    return cnt


def main():
    sw = sw_values()
    d26 = days_2026()
    rows = []
    for name, _, kind in SOFTWARE:
        anc = anchor_table(kind) if kind else {y: None for y in ZH}
        same = [y for y in ZH if sw[name][y] == anc[y]]
        rows.append({
            'name': name,
            'domain': ('地支' if kind not in ('lishi', 'dahuo') else
                       ('四维' if kind == 'lishi' else '天干')),
            'soft_2026': sw[name]['午'],
            'anchor_2026': anc['午'],
            'match_12zhi': len(same),
            'mismatch_zhi': [y for y in ZH if sw[name][y] != anc[y]],
            'soft_table': sw[name],
            'anchor_table': anc,
            'days_2026': d26.get(sw[name]['午'], 0),
            'scores_2026': {ev: shensha_score(ev, name, None) for ev in EVENTS},
        })
    payload = {
        'anchor': '协纪辨方书 卷三 义例一（279221）+ 考原 359077 互校',
        'year_2026_zhi': '午',
        'items': rows,
        'no_canon': NOCANON,
        'not_implemented': NOT_IMPL,
    }
    fn = os.path.join(os.path.dirname(__file__), 'p02_family.json')
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print('%-6s %-6s %-6s %-6s %-8s %s' % ('神煞', '软件2026', '主锚2026', '12支同', '2026天次', '不符年支(部分)'))
    for r in rows:
        print('%-6s %-8s %-8s %-6d %-8d %s' % (
            r['name'], r['soft_2026'], r['anchor_2026'],
            r['match_12zhi'], r['days_2026'], ''.join(r['mismatch_zhi'])))
    print('无载（协纪0命中）:', '/'.join(NOCANON))
    print('未实现:', '/'.join(NOT_IMPL))
    print('写入:', fn)


if __name__ == '__main__':
    main()
