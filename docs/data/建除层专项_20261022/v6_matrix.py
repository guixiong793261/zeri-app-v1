# -*- coding: utf-8 -*-
"""T6 卷十建除事项矩阵 + T7 影响面摘要（只读）。"""
import io, os, sys, json, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'd:\自编择日软件\专业级正五行择日软件\docs\data\建除层专项_20261022'
XJ = r'C:\Temp\xj_full\279229.txt'
EV_KEYS = ['嫁娶', '入学', '求医', '出行', '安葬', '开市', '交易', '修造', '动土',
           '入宅', '移徙', '安床', '作灶', '立券', '祭祀', '上官', '赴任', '求财']
STAR_RE = re.compile(r'(建日|除日|满日|平日|定日|执日|破日|危日|成日|收日|开日|闭日)')

mat = collections.defaultdict(lambda: {'yi': set(), 'ji': set(), 'lines': set(), 'head': ''})
with io.open(XJ, encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    s = line.strip()
    if not s:
        continue
    stars = STAR_RE.findall(s)
    if not stars:
        continue
    evs = [k for k in EV_KEYS if k in s]
    if not evs:
        continue
    # 句内定位 宜/忌 段
    for ev in evs:
        seg_yi = seg_ji = ''
        if '宜' in s:
            seg_yi = s.split('宜', 1)[1]
        if '忌' in s:
            seg_ji = s.split('忌', 1)[1]
        for st in stars:
            if st in seg_yi:
                mat[ev]['yi'].add(st)
            if st in seg_ji:
                mat[ev]['ji'].add(st)
        mat[ev]['lines'].add(i)
        if not mat[ev]['head']:
            mat[ev]['head'] = s[:90]

out = {}
print('=== T6 卷十 事项×建除（宜/忌 同句判定）===')
for ev in EV_KEYS:
    if ev not in mat:
        continue
    d = mat[ev]
    out[ev] = {'yi': sorted(d['yi']), 'ji': sorted(d['ji']),
               'lines': sorted(d['lines']), 'sample': d['head']}
    print('  %-3s 宜=%s 忌=%s 行=%s' % (ev, ''.join(sorted(d['yi'])) or '-',
                                        ''.join(sorted(d['ji'])) or '-',
                                        ','.join(map(str, sorted(d['lines'])))[:60]))
with io.open(os.path.join(OUT, 'v6_event_matrix.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=list)

print('\n=== T7 影响面（文件:调用点数）===')
v7 = json.load(io.open(os.path.join(OUT, 'v7_predicates.json'), encoding='utf-8'))
for k, items in v7['callers'].items():
    c = collections.Counter(x['file'] for x in items)
    print('  %s = %d 处 / %d 文件' % (k, len(items), len(c)))
    for f, n in c.most_common(8):
        print('      %-42s %d' % (f, n))
print('\n已写 v6_event_matrix.json')
