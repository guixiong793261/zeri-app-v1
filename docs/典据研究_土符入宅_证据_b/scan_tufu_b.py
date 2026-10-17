# -*- coding: utf-8 -*-
"""
判据 (b) 所忌事项范围——三库穷尽扫描（词表冻结 v1.0，全卷扫，无抽样）
语料：协纪 C:\\Temp\\xj_full\\279216-279254（36卷+前料）
      考原 C:\\Temp\\xl_full\\359075-359081（提要+卷一~六）
      陈书 C:\\Temp\\czx_full\\czx_pages.json（1130页）
输出：scan_results_b.json（hits+全文计数）＋ manifest 段（语料 SHA256）
确定性：无随机、无抽样，同一语料复跑结果逐字节一致。
"""
import json, os, re, hashlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scan_results_b.json')

# ---- 词表冻结 v1.0（§9.2，含繁简变体；新增变体仅展开同词，不增词族） ----
MAIN = ['土符']
CONFUSE = ['土府', '土王用事']
FAMILIES = {
    '动土族': ['动土', '動土', '興工', '兴工', '穿凿', '穿鑿', '掘',
               '破土', '穿井', '开渠', '開渠', '筑墙', '築牆', '筑牆'],
    '修造族': ['修造', '興造', '兴造', '营造', '營造', '修葺'],
    '拆舍族': ['拆舍', '毁拆', '毀拆', '拆卸'],
    '入宅族': ['入宅', '归宅', '歸宅'],
    '移徙族': ['移徙', '迁徙', '遷徙'],
    '交易族': ['立券', '交易'],
    '入学族': ['入学', '入學', '就学', '就學'],
    '求医族': ['求医', '求醫', '疗病', '療病'],
}
WEIGHT = ['大忌', '勿用', '不宜', '小忌', '制', '化', '解', '忌']
# 待议词表（§9.1-7：新词只记录，不直接影响判据）
PENDING = ['行墙', '行牆', '搬移', '移徙入宅', '入宅移居']

WIN = 150  # 共现窗口（±字符）

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def load_corpora():
    corp = []
    counts = json.load(open(os.path.join(XJ, 'counts.json'), encoding='utf-8'))
    for n in range(279216, 279255):
        p = os.path.join(XJ, '%d.txt' % n)
        txt = open(p, encoding='utf-8').read()
        corp.append({'book': '协纪辨方书', 'chap': str(n), 'juan': counts[str(n)]['juan'],
                     'text': txt, 'path': p})
    for n in range(359075, 359082):
        p = os.path.join(XL, '%d.txt' % n)
        txt = open(p, encoding='utf-8').read()
        first = txt.split('\n', 1)[0]
        m = re.search(r'卷([一二三四五六])', first)
        corp.append({'book': '御定星历考原', 'chap': str(n),
                     'juan': ('卷' + m.group(1)) if m else '提要', 'text': txt, 'path': p})
    pages = json.load(open(CZX, encoding='utf-8'))
    for pg, txt in pages:
        corp.append({'book': '陈子性藏书', 'chap': 'p%s' % pg, 'juan': '',
                     'text': txt or '', 'path': CZX})
    return corp

def line_of(text, idx):
    return text.count('\n', 0, idx) + 1

def scan():
    corp = load_corpora()
    manifest = []
    hits, conf_hits, pend_hits = [], [], []
    totals = {}       # book -> term -> count（全文穷尽计数）
    tufu_totals = {}
    for c in corp:
        book, txt = c['book'], c['text']
        manifest.append({'book': book, 'chap': c['chap'], 'juan': c['juan'],
                         'sha256': sha(c['path']) if c['path'].endswith('.txt') else None,
                         'chars': len(txt)})
        totals.setdefault(book, {})
        for w in MAIN:
            totals[book][w] = totals[book].get(w, 0) + txt.count(w)
        for fam, ws in FAMILIES.items():
            for w in ws:
                totals[book][w] = totals[book].get(w, 0) + txt.count(w)
        for w in CONFUSE + PENDING:
            totals[book][w] = totals[book].get(w, 0) + txt.count(w)
        for m in re.finditer('土符', txt):
            s, e = max(0, m.start() - WIN), min(len(txt), m.end() + WIN)
            ctx = txt[s:e].replace('\n', ' ')
            fams = {f: [w for w in ws if w in ctx] for f, ws in FAMILIES.items()}
            fams = {f: v for f, v in fams.items() if v}
            wts = [w for w in WEIGHT if w in ctx]
            hits.append({'book': book, 'chap': c['chap'], 'juan': c['juan'],
                         'line': line_of(txt, m.start()), 'ctx': ctx,
                         'families': fams, 'weight': wts})
        for w in CONFUSE:
            for m in re.finditer(re.escape(w), txt):
                s, e = max(0, m.start() - 60), min(len(txt), m.end() + 60)
                conf_hits.append({'book': book, 'chap': c['chap'], 'juan': c['juan'],
                                  'term': w, 'line': line_of(txt, m.start()),
                                  'ctx': txt[s:e].replace('\n', ' ')})
        for w in PENDING:
            for m in re.finditer(re.escape(w), txt):
                s, e = max(0, m.start() - 60), min(len(txt), m.end() + 60)
                pend_hits.append({'book': book, 'chap': c['chap'], 'term': w,
                                  'line': line_of(txt, m.start()),
                                  'ctx': txt[s:e].replace('\n', ' ')})
        tufu_totals[book] = tufu_totals.get(book, 0) + txt.count('土符')
    # 去重 manifest（陈书 1130 页同一文件只记一次 SHA）
    seen, man2 = set(), []
    for m in manifest:
        k = (m['book'], m['chap'])
        if m['book'] == '陈子性藏书':
            if 'czx' not in seen:
                m['sha256'] = sha(CZX); seen.add('czx'); man2.append(m)
            continue
        man2.append(m)
    res = {'meta': {'purpose': '判据(b) 所忌事项范围穷尽扫描', 'wordlist': 'v1.0 冻结',
                    'window': WIN, 'corpus_note': '协纪36卷+前料39章/考原提要+6卷/陈书1130页，全卷扫无抽样'},
           'corpus_manifest': man2,
           'tufu_totals': tufu_totals,
           'term_totals': totals,
           'tufu_hits': hits,
           'confusion_hits': conf_hits,
           'pending_hits': pend_hits}
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('土符命中：协纪 %d / 考原 %d / 陈书 %d' % tuple(tufu_totals[b] for b in tufu_totals))
    print('hits 记录数:', len(hits), ' 防混淆记录:', len(conf_hits), ' 待议词记录:', len(pend_hits))
    print('输出:', OUT)
    return 0

if __name__ == '__main__':
    sys.exit(scan())
