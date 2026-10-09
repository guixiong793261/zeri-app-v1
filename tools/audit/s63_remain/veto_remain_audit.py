# -*- coding: utf-8 -*-
"""§63 剩余门槛专项审计（2026-10-09 拍板指令，只读分析，不改产品码）。

目标：把 §63 降级后剩余否决来源逐条拆解（岁破/太岁/相主/月家飞星/五行兜底/
规则通道等），产出每条门槛的否决贡献占比与"仅因该条被否"天数。

口径纪律：
- veto_reasons 权威口径：否决判定 = Scorer.score() 返回 veto_reasons 非空；
  细分类按权威文案前缀/关键词映射，不另造口径；
- 走产品真实管线：calculate_sizhu + Scorer.score（zeli_mode='feixing'，12:00）；
- 数据落盘 tools/audit/s63_remain/（raw JSON + 聚合 JSON + manifest）；
- 校准：--calibrate 与 tools/audit/s63_veto_tuning/veto_audit_new.json 逐日
  否决集对齐（§63 基线复现），对不齐即 EXIT 1，禁止带病出数。

用法：
    python tools/audit/s63_remain/veto_remain_audit.py                 # 全量 2024-2027
    python tools/audit/s63_remain/veto_remain_audit.py --years 2024    # 单年
    python tools/audit/s63_remain/veto_remain_audit.py --calibrate     # 跑完自动校准
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import Scorer

# ==================== SEED（复现锚点，改任何一项即破坏可复现性） ====================
SEED = {
    'date_range': ['2024-01-01', '2027-12-31'],
    'hour': '12:00',
    'zeli_mode': 'feixing',
    'events': ['嫁娶', '订婚', '纳采', '修造', '装修', '动土', '拆舍', '入宅',
               '作灶', '安床', '安葬', '开业', '出行', '签约', '入学', '求医'],
    # 山向 8 事项传坤山艮向兼未（§63 对照表口径）；其余不传
    'shan_xiang_events': ['修造', '装修', '动土', '拆舍', '入宅', '作灶', '安床', '安葬'],
    'shan_xiang': '坤山艮向兼未',
    # 人口档：1/2/3/4 逐级叠加；全员 role=事主（校准实测：新娘/新郎/亡命角色均与基线残差更大）
    'owners_pool': [
        {'name': '主', 'birth_date': '1972-01-08', '生肖': '亥'},
        {'name': '次', 'birth_date': '1971-05-11', '生肖': '亥'},
        {'name': '眷三', 'birth_date': '1994-10-28', '生肖': '戌'},
        {'name': '眷四', 'birth_date': '1998-10-13', '生肖': '寅'},
    ],
}
SHAN_XIANG = SEED['shan_xiang']

S63_BASELINE = os.path.join(_ROOT, 'tools', 'audit', 's63_veto_tuning', 'veto_audit_new.json')
OUT_DIR = os.path.join(_ROOT, 'tools', 'audit', 's63_remain')


def build_owners(event_type, pop):
    """按事项与人口档构造事主列表（SEED 锚定）。

    校准实测：全员 role=事主 与 §63 基线残差最小（订婚/纳采/修造/作灶/出行
    pop1 精确对齐）；新娘/新郎/亡命角色均实测更差，故不再按事项区分角色。
    """
    pool = [dict(o) for o in SEED['owners_pool'][:pop]]
    for o in pool:
        o['role'] = '事主'
    return pool


# ==================== 细分类（veto_reasons 权威文案 → 细类） ====================
def _split_rule_tokens(text):
    """规则通道否决文案以 '、' 连接多条，逐 token 归类。"""
    return [t for t in text.split('、') if t]


_RULE_TOKEN_RULES = [
    ('规则·岁破日', lambda t: '岁破日' in t),
    ('规则·月破日', lambda t: '月破日' in t),
    ('规则·四离四绝', lambda t: ('四离' in t or '四绝' in t)),
    ('规则·往亡', lambda t: '往亡' in t),
    ('规则·天火日', lambda t: '天火日' in t),
    ('规则·地火日', lambda t: '地火日' in t),
    ('规则·灶君忌', lambda t: ('灶君忌日' in t or '灶君朝天' in t or '逐月作灶忌日' in t)),
    ('规则·土府日', lambda t: '土府日' in t),
    ('规则·冲主妇', lambda t: '冲主妇' in t),
    ('规则·冲宅主', lambda t: '冲宅主' in t),
    ('规则·克山运', lambda t: '克山运' in t),
    # 嫁娶规则._check_veto_items 关键词（嫁娶/订婚/纳采经 canonical → 嫁娶规则）
    ('规则·禁婚年', lambda t: '禁婚年' in t),
    ('规则·红纱日', lambda t: '红纱' in t),
    ('规则·杨公忌', lambda t: '杨公忌' in t),
    ('规则·重丧日', lambda t: '重丧' in t),
    ('规则·三娘煞', lambda t: '三娘煞' in t),
    ('规则·阴阳差错', lambda t: '阴阳差错' in t),
    ('规则·女命忌嫁', lambda t: '女命忌嫁' in t),
    ('规则·冲新娘', lambda t: '冲新娘' in t),
]


def classify_text(text):
    """单条否决文案 → 细类列表（一条文案可属多细类，如年三煞+岁破叠加）。"""
    cats = []
    if not text:
        return cats
    # ── 年层（analyze_year suitable=False）──
    if text.startswith('年份不宜'):
        if '冲流年太岁' in text:
            cats.append('年·仙命冲流年太岁')
        if '犯年三煞' in text:
            cats.append('年·山向犯年三煞')
        if '向首正对太岁' in text:
            cats.append('年·向首犯太岁')
        if '犯岁破' in text:
            cats.append('年·山向犯岁破')
        if '年家五黄到坐山' in text:
            cats.append('年·年家五黄到坐山')
        if '年家二黑到坐山' in text:
            cats.append('年·年家二黑到坐山')
        if not cats:
            cats.append('年·分数兜底(<50)')
        return cats
    # ── 月层（analyze_month suitable=False）──
    if text.startswith('月份不宜'):
        if '五黄到坐山' in text:
            cats.append('月·五黄到坐山')
        if '二黑到坐山' in text:
            cats.append('月·二黑到坐山')
        if not cats:
            cats.append('月·分数兜底(<50)')
        return cats
    # ── 五行严重不合格兜底 ──
    if text.startswith('五行严重不合格'):
        cats.append('五行·严重不合格兜底')
        # 兜底评语括号内列真实硬煞项，逐项二次归类（交叉归因，不计入"仅因"主类）
        inner = text.split('（大忌：', 1)[1].rstrip('）') if '（大忌：' in text else ''
        for token in _split_rule_tokens(inner):
            if '年三煞' in token:
                cats.append('五行兜底·内含年三煞')
            elif '月三煞' in token:
                cats.append('五行兜底·内含月三煞')
            elif '岁破' in token:
                cats.append('五行兜底·内含岁破')
            elif '五黄' in token:
                cats.append('五行兜底·内含五黄')
            elif '二黑' in token:
                cats.append('五行兜底·内含二黑')
            elif '阴府' in token:
                cats.append('五行兜底·内含正阴府')
            elif '克山运' in token:
                cats.append('五行兜底·内含克山运')
            else:
                cats.append('五行兜底·内含其他')
        return cats
    # ── 日课层一票否决通道 ──
    if '三煞大忌' in text:
        if '(山向)' in text or '山向' in text:
            cats.append('日课·三煞大忌年三煞(山向)')
        if '(日柱)' in text or '(月柱)' in text or '(时柱)' in text:
            cats.append('日课·三煞大忌四柱临方')
        if not cats:
            cats.append('日课·三煞大忌其他')
        return cats
    if '相主硬门槛' in text:
        if '自刑' in text:
            cats.append('相主·硬门槛自刑')
        elif '仙命' in text:
            cats.append('相主·硬门槛仙命六冲')
        else:
            cats.append('相主·硬门槛生肖六冲')
        return cats
    if '山家封禁' in text:
        if '二黑' in text:
            cats.append('山家封禁·二黑')
        else:
            cats.append('山家封禁·五黄')
        return cats
    if '【仙命双凶叠加】' in text:
        cats.append('仙命·双凶叠加')
        return cats
    if '仙命真冲' in text:
        cats.append('仙命·真冲')
        cats.append('仙命·叠大忌' if '叠大忌' in text else '仙命·无制化')
        return cats
    if '主兼双坐山克' in text:
        cats.append('仙命·主兼双坐山克')
        return cats
    if '兼向独立否决' in text:
        cats.append('仙命·兼向独立否决')
        return cats
    if '坐山克仙命' in text:
        cats.append('仙命·坐山克仙命')
        cats.append('仙命·叠大忌' if '叠大忌' in text else '仙命·无制化')
        return cats
    if '玄空飞星大忌' in text:
        cats.append('日课·玄空飞星大凶')
        return cats
    if '婚嫁大忌' in text:
        cats.append('婚嫁·大忌')
        return cats
    if text.startswith('当日忌') and '一票否决' in text:
        cats.append('忌事·精确匹配')
        return cats
    # ── 规则通道（rule_checker veto，多条以 '、' 连接）──
    for token in _split_rule_tokens(text):
        hit = False
        for cat, fn in _RULE_TOKEN_RULES:
            if fn(token):
                cats.append(cat)
                hit = True
        if not hit:
            cats.append('规则·其他:' + token[:24])
    if not cats:
        cats.append('未归类:' + text[:24])
    return cats


COARSE_MAP = {
    # 细类 → §63 对照表粗分类（对账用）
    '年·仙命冲流年太岁': 'year_veto',
    '年·山向犯年三煞': 'year_veto',
    '年·向首犯太岁': 'year_veto',
    '年·山向犯岁破': 'year_veto',
    '年·年家五黄到坐山': 'year_veto',
    '年·年家二黑到坐山': 'year_veto',
    '年·分数兜底(<50)': 'year_veto',
    '月·五黄到坐山': 'month_veto',
    '月·二黑到坐山': 'month_veto',
    '月·分数兜底(<50)': 'month_veto',
    '日课·三煞大忌年三煞(山向)': 'sansha_year',
    '日课·三煞大忌四柱临方': 'sansha_pillar',
    '日课·三煞大忌其他': 'sansha_other',
    '相主·硬门槛生肖六冲': 'xiangzhu',
    '相主·硬门槛自刑': 'xiangzhu',
    '相主·硬门槛仙命六冲': 'xiangzhu',
    '婚嫁·大忌': 'marriage',
}


def to_channel(fine_cat):
    """细类 → 通道（"仅因该通道被否"聚合口径）。"""
    if fine_cat.startswith('年·'):
        return '年层'
    if fine_cat.startswith('月·'):
        return '月层'
    if fine_cat.startswith('日课·三煞'):
        return '三煞日课层'
    if fine_cat.startswith('相主·'):
        return '相主硬门槛'
    if fine_cat.startswith('山家封禁'):
        return '山家封禁'
    if fine_cat.startswith('仙命·'):
        return '仙命系'
    if fine_cat == '日课·玄空飞星大凶':
        return '飞星日课层'
    if fine_cat.startswith('婚嫁'):
        return '婚嫁大忌'
    if fine_cat.startswith('忌事'):
        return '忌事精确匹配'
    if fine_cat.startswith('五行·'):
        return '五行兜底'
    if fine_cat.startswith('规则·'):
        return '规则通道'
    return '其他'


def to_coarse(fine_cats):
    """细类 → §63 粗分类集合（feixing/month_veto 双标签口径与 §63 对齐）。"""
    coarse = set()
    for c in fine_cats:
        if c in COARSE_MAP:
            coarse.add(COARSE_MAP[c])
        elif c.startswith('月·') and ('五黄' in c or '二黑' in c):
            coarse.update(('month_veto', 'feixing'))
        elif c == '日课·玄空飞星大凶':
            coarse.add('feixing')
        else:
            coarse.add('other')
    return coarse


# ==================== 主流程 ====================
def iter_dates(years):
    d = dt.date(int(years[0]), 1, 1)
    end = dt.date(int(years[-1]), 12, 31)
    while d <= end:
        yield d
        d += dt.timedelta(days=1)


def run_audit(years, events, pops, log_every=30):
    """跑真实管线，返回 {year: {event: {pop: {date_iso: [veto原文]}}}}。"""
    raw = {str(y): {} for y in years}
    scorer = Scorer()
    dates = list(iter_dates(years))
    sizhu_cache = {}
    n_total = len(dates) * len(events) * len(pops)
    n_done = 0
    t0 = time.time()
    for d in dates:
        if d not in sizhu_cache:
            sz = calculate_sizhu(d, 12, 0)
            sz['date'] = d
            sz['year'] = d.year
            sz['month'] = d.month
            sz['day'] = d.day
            sizhu_cache[d] = sz
        base_sz = sizhu_cache[d]
        # 人口档共享同一四柱；评分随 owners 变（婚嫁类全员参与、非婚嫁类 §62
        # 半权重打标随人数变化），故逐档独立评分，与 §63 四档口径一致
        for ev in events:
            for pop in pops:
                owners_p = build_owners(ev, pop)
                r_p = scorer.score(dict(base_sz), ev, owners=owners_p,
                                   shan_xiang=(SHAN_XIANG if ev in SEED['shan_xiang_events'] else None))
                vr_p = r_p.get('veto_reasons') or []
                if vr_p:
                    raw[str(d.year)].setdefault(ev, {}).setdefault(str(pop), {})[d.isoformat()] = vr_p
                n_done += 1
        if (n_done // (len(events) * len(pops))) % log_every == 0:
            el = time.time() - t0
            print(f'[progress] {d} done={n_done}/{n_total} elapsed={el:.0f}s eta={el/max(n_done,1)*(n_total-n_done):.0f}s',
                  flush=True)
    return raw


def aggregate(raw):
    """细分类聚合：各细类天数、占比、仅因该细类/通道被否天数。

    口径：solo = 当日全部主类（剔除五行兜底·内含*交叉项与仙命子标签）都属
    同一细类/通道才计入，即"仅因该条被否"。
    """
    fine_days = {}
    fine_main = {}      # 主类命中天数（剔除交叉项后的细类口径）
    solo_days = {}      # 仅因该细类（当日主类唯一且等于该类）
    chan_days = {}      # 通道命中天数
    solo_chan = {}      # 仅因该通道被否
    vetoed = 0
    for y, yd in raw.items():
        for ev, pd in yd.items():
            for pop, days in pd.items():
                for dateiso, texts in days.items():
                    vetoed += 1
                    cats = []
                    for t in texts:
                        for c in classify_text(t):
                            if c not in cats:
                                cats.append(c)
                    key = (y, ev, pop)
                    for c in cats:
                        fine_days.setdefault(c, set()).add((key, dateiso))
                    # 主类 = 剔除五行兜底·内含*交叉项与仙命·叠大忌/无制化子标签
                    main_cats = [c for c in cats if not c.startswith('五行兜底·内含')
                                 and c not in ('仙命·叠大忌', '仙命·无制化')]
                    uniq = set(main_cats)
                    for c in uniq:
                        fine_main.setdefault(c, set()).add((key, dateiso))
                    if len(uniq) == 1:
                        solo_days.setdefault(next(iter(uniq)), set()).add((key, dateiso))
                    chans = {to_channel(c) for c in main_cats}
                    for ch in chans:
                        chan_days.setdefault(ch, set()).add((key, dateiso))
                    if len(chans) == 1:
                        solo_chan.setdefault(next(iter(chans)), set()).add((key, dateiso))
    return fine_days, fine_main, solo_days, chan_days, solo_chan, vetoed


def _set_size(s):
    return len(s)


def calibrate(raw, baseline_path):
    """与 §63 基线逐日否决集对齐：基线有而新算无（或反之）即记差异。"""
    base = json.load(open(baseline_path, encoding='utf-8'))
    mism = []
    n_cmp = 0
    for y, yd in base.items():
        if y not in raw:
            continue
        for ev, pd in yd.items():
            for pop, days in pd.items():
                n_cmp += 1
                b = set(days.keys())
                n = set(raw.get(y, {}).get(ev, {}).get(pop, {}).keys())
                if b != n:
                    mism.append((y, ev, pop, len(b), len(n),
                                 sorted(b - n)[:3], sorted(n - b)[:3]))
    return n_cmp, mism


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--years', default='2024,2025,2026,2027')
    ap.add_argument('--events', default='')
    ap.add_argument('--pops', default='1,2,3,4')
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--reagg', action='store_true',
                    help='不重跑评分，从已存 raw JSON 重聚合')
    ap.add_argument('--no-save', action='store_true')
    args = ap.parse_args()

    years = [y.strip() for y in args.years.split(',') if y.strip()]
    events = [e for e in SEED['events'] if not args.events
              or e in [x.strip() for x in args.events.split(',')]]
    pops = [int(p) for p in args.pops.split(',') if p.strip()]

    print(f'[config] years={years} events={len(events)} pops={pops}', flush=True)
    t0 = time.time()
    if args.reagg:
        tag_in = f"{years[0]}-{years[-1]}"
        raw_path = os.path.join(OUT_DIR, f'veto_remain_raw_{tag_in}.json')
        raw = json.load(open(raw_path, encoding='utf-8'))
        print(f'[reagg] loaded {raw_path}', flush=True)
    else:
        raw = run_audit(years, events, pops)
    print(f'[run] elapsed={time.time()-t0:.0f}s', flush=True)

    n_cmp, mism = (0, [])
    if args.calibrate and os.path.exists(S63_BASELINE):
        n_cmp, mism = calibrate(raw, S63_BASELINE)
        print(f'[calibrate] compared={n_cmp} mismatch={len(mism)}', flush=True)
        for m in mism[:10]:
            print('  MISMATCH:', m, flush=True)

    fine_days, fine_main, solo_days, chan_days, solo_chan, vetoed = aggregate(raw)
    print(f'[agg] vetoed_day_cells={vetoed} fine_categories={len(fine_days)}', flush=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    tag = f"{years[0]}-{years[-1]}"
    if not args.no_save:
        raw_path = os.path.join(OUT_DIR, f'veto_remain_raw_{tag}.json')
        json.dump(raw, open(raw_path, 'w', encoding='utf-8'), ensure_ascii=False)
        agg = {
            'vetoed_day_cells': vetoed,
            'fine_days': {c: _set_size(s) for c, s in
                          sorted(fine_days.items(), key=lambda kv: -_set_size(kv[1]))},
            'fine_main_days': {c: _set_size(s) for c, s in
                               sorted(fine_main.items(), key=lambda kv: -_set_size(kv[1]))},
            'solo_days': {c: _set_size(s) for c, s in
                          sorted(solo_days.items(), key=lambda kv: -_set_size(kv[1]))},
            'channel_days': {c: _set_size(s) for c, s in
                             sorted(chan_days.items(), key=lambda kv: -_set_size(kv[1]))},
            'solo_channel_days': {c: _set_size(s) for c, s in
                                  sorted(solo_chan.items(), key=lambda kv: -_set_size(kv[1]))},
        }
        agg_path = os.path.join(OUT_DIR, f'veto_remain_agg_{tag}.json')
        json.dump(agg, open(agg_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        scorer_sha = sha256(os.path.join(_ROOT, 'modules', '评分器.py'))
        manifest = {
            'seed': SEED,
            'years': years,
            'events': events,
            'pops': pops,
            'scorer_sha256_16': scorer_sha,
            'raw': os.path.basename(raw_path),
            'agg': os.path.basename(agg_path),
            'calibrate_compared': n_cmp,
            'calibrate_mismatch': len(mism),
            'generated_at': dt.datetime.now().isoformat(timespec='seconds'),
        }
        with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1)
        print(f'[save] {raw_path}', flush=True)
        print(f'[save] {agg_path}', flush=True)

    # 摘要（完整输出到 stdout）
    print('\n===== 细分类天数（全量合并）=====', flush=True)
    for c, s in sorted(fine_days.items(), key=lambda kv: -_set_size(kv[1])):
        print(f'{c}: {_set_size(s)}')
    print('\n===== 主类命中天数（剔除交叉项）=====', flush=True)
    for c, s in sorted(fine_main.items(), key=lambda kv: -_set_size(kv[1])):
        print(f'{c}: {_set_size(s)}')
    print('\n===== 仅因该类被否（细类口径，主类唯一）=====', flush=True)
    for c, s in sorted(solo_days.items(), key=lambda kv: -_set_size(kv[1])):
        print(f'{c}: {_set_size(s)}')
    print('\n===== 通道命中天数（全量合并）=====', flush=True)
    for c, s in sorted(chan_days.items(), key=lambda kv: -_set_size(kv[1])):
        print(f'{c}: {_set_size(s)}')
    print('\n===== 仅因该通道被否（通道口径）=====', flush=True)
    for c, s in sorted(solo_chan.items(), key=lambda kv: -_set_size(kv[1])):
        print(f'{c}: {_set_size(s)}')

    if args.calibrate:
        sys.exit(1 if mism else 0)
    sys.exit(0)


if __name__ == '__main__':
    main()
