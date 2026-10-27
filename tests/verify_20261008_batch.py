# -*- coding: utf-8 -*-
"""2026-10-08 批量抽查拍板批次 verify（合并）

覆盖：
  Q4 制化分离（已制化不入忌项/不扣分 + 已制化区块 + 规则层静态阴府忌项清理）
  Q5 地支关系 0 分透明展示、时柱措辞
  Q2 地支关系并列计分（冲/害/刑/破不互斥，全局明细与时柱块）
  宜忌并存硬门槛优先说明
  忌项长句逐句拆分
  临三煞“上管下、下不犯上”反向枚举提示
  空名事主角色标识
  E207 时柱自述与恒等式一致校验

运行：python tests/verify_20261008_batch.py   （退出码 0 = 全部通过）
"""
import sys
import os
import json
import copy
import subprocess
import tempfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
from modules.喜用神计算器 import calculate_xishen_yongshen
from modules.日课校验器 import lint_lesson

BATCH = os.path.join(ROOT, '审查结果', '_batch')
SANDBOX = os.path.join(
    ROOT, '.trae', 'skills', 'zeri-detail-sandbox', 'scripts', 'run_detail_sandbox.py')
SHAN = '坤山艮向兼未'
TMP = tempfile.mkdtemp(prefix='_verify_20261008_')

_owners = json.load(open(os.path.join(BATCH, 'owners.json'), encoding='utf-8'))
NORM = []
for o in _owners:
    bd = date(int(o['y']), int(o['m']), int(o['d']))
    hh = int(o.get('hh', 12))
    xy = calculate_xishen_yongshen(calculate_sizhu(bd, hh, int(o.get('mm', 0))))
    NORM.append({'role': o.get('role', ''), '性别': o.get('gender', ''),
                 'name': o.get('name', ''), 'birth_date': bd,
                 'birth_hour': hh, 'birth_minute': int(o.get('mm', 0)),
                 'xishen': xy[0], 'yongshen': xy[1]})


def score(event, dt, hour, shan=None):
    y, m, d = map(int, dt.split('-'))
    sz = calculate_sizhu(date(y, m, d), hour, 0)
    r = calculate_score(sz, event, NORM, '阳宅', shan,
                        None, None, None, None, None, zeli_mode='pure')
    r['sizhu'] = {'年柱': sz['年柱'], '月柱': sz['月柱'],
                  '日柱': sz['日柱'], '时柱': sz['时柱']}
    return r


def render(event, dt, hour, shan=None):
    out = os.path.join(TMP, f'{event}_{dt}_{hour}.txt')
    cmd = [sys.executable, SANDBOX, '--event', event, '--date', dt,
           '--hour', str(hour), '--owners-file',
           os.path.join(BATCH, 'owners.json'), '--out', out]
    if shan:
        cmd += ['--shan', shan]
    subprocess.run(cmd, check=True, capture_output=True)
    return open(out, encoding='utf-8').read()


def check(name, cond):
    if not cond:
        raise AssertionError(name)
    print('  OK  ' + name)


def main():
    print('[Q4] 制化分离 / 已制化区块 / 静态忌项清理')
    r = score('拆舍', '2026-10-11', 14, SHAN)
    mit = (r.get('sansha_info') or {}).get('mountain_warnings_mitigated') or []
    check('已制化列表含正阴府项',
          any('正阴府' in m and '有制化' in m for m in mit))
    check('拆舍忌项无阴府残留',
          not any('阴府' in str(j) for j in r.get('ji_list') or []))
    c = render('拆舍', '2026-10-11', 14, SHAN)
    check('渲染含【山家警告 · 已制化】区块', '山家警告 · 已制化' in c)
    rb = score('安葬', '2025-05-25', 14, SHAN)
    check('无制化安葬阴府忌项保留',
          any('阴府' in str(j) and '无制化' in str(j)
              for j in rb.get('ji_list') or []))

    print('[d7] 年运长句逐句拆分（宜入宜项 / 否定句入参考块）')
    rz = score('修造', '2024-10-02', 14, SHAN)
    check('宜：甲辰年利', '坤山艮向兼未甲辰年利' in rz.get('yi_list'))
    check('宜：甲辰年兼申大利',
          '坤山艮向兼未甲辰年兼申：大利' in rz.get('yi_list'))
    # §189 P2（2026-10-27 拍板·方案A）：年运表否定句移出忌项，改入
    # mountain_year_ref（未计分参考块），忌事通道不再隐性 -15/条。
    check('参考：甲辰年兼末不利犯三煞（未计分）',
          '坤山艮向兼未甲辰年兼末：不利，犯三煞'
          in (rz.get('mountain_year_ref') or []))
    check('忌：年运否定句不再入忌项',
          not any('兼末：不利' in str(j) for j in rz.get('ji_list') or []))
    check('忌项无混合长句（年利。）',
          not any('年利。' in str(j) for j in rz.get('ji_list') or []))

    print('[d8] 临三煞单向口径提示')
    ac = render('安床', '2026-10-12', 6, SHAN)
    check('安床：月柱戌临日柱三煞方',
          '月柱戌临日柱三煞方（申酉戌）' in ac)
    check('含“上管下、下不犯上”口径', '上管下、下不犯上' in ac)
    qy = render('签约', '2024-01-25', 2)
    check('签约：年柱卯临月柱三煞方',
          '年柱卯临月柱三煞方（寅卯辰）' in qy)

    print('[d6] 宜忌并存硬门槛优先说明')
    check('含硬门槛优先口径', '硬门槛优先' in ac)

    print('[事主标识] 空名事主角色区分')
    mr = render('嫁娶', '2025-07-27', 18)
    check('嫁娶：年柱巳冲（事主1）', '年柱巳冲（事主1）' in mr)
    check('嫁娶：年柱巳冲（事主2）', '年柱巳冲（事主2）' in mr)
    rzz = score('入宅', '2025-08-01', 6, SHAN)
    xq = str((rzz.get('score_details') or {}).get('相主详情'))
    check('相主明细：事主1生肖亥', '事主1生肖亥' in xq)
    check('相主明细：事主2生肖亥', '事主2生肖亥' in xq)

    print('[Q5] 0 分透明展示与措辞')
    rq = score('签约', '2026-06-13', 14)
    check('地支关系恒等式=0',
          (rq.get('wu_xing_result') or {}).get('score_breakdown', {})
          .get('地支关系得分') == 0)
    cq = render('签约', '2026-06-13', 14)
    check('0 分总分行仍显示', '地支关系得分（四柱六对合计）：+0 分' in cq)
    check('旧措辞“已含于上方”已消除', '已含于上方' not in cq)
    check('新措辞“时柱关系已计入五行评分”',
          '时柱关系已计入五行评分·地支关系得分' in cq)

    print('[E207] 时柱自述与恒等式一致')
    res = lint_lesson(rq, rendered_content=cq)
    check('真实 detail 不报 E207',
          not [i for i in res.issues if i.rule_id == 'E207'])
    bad = copy.deepcopy(rq)
    bad['wu_xing_result']['score_breakdown']['地支关系得分'] = 24
    res2 = lint_lesson(bad, rendered_content=cq)
    check('篡改恒等式必报 E207',
          bool([i for i in res2.issues if i.rule_id == 'E207']))
    bad_text = cq.replace('已计入五行评分·地支关系得分',
                          '已含于上方地支关系得分')
    res3 = lint_lesson(rq, rendered_content=bad_text)
    check('旧措辞必报 E207',
          bool([i for i in res3.issues if i.rule_id == 'E207']))

    print('[Q2] 地支关系并列计分（冲/害/刑/破不互斥）')
    from modules.评分器 import Scorer
    s211 = calculate_sizhu(date(2024, 2, 11), 12, 0)
    _s, _lines = Scorer()._calc_all_zhi_relations_detail(s211)
    check('寅巳：六害与相刑并列明细',
          any('寅巳害' in l for l in _lines)
          and any('无恩之刑，寅巳刑' in l for l in _lines))
    s108 = calculate_sizhu(date(2024, 1, 8), 12, 0)
    _s, _lines = Scorer()._calc_all_zhi_relations_detail(s108)
    check('丑未：六冲与相刑并列明细',
          any('丑未冲' in l for l in _lines)
          and any('恃势之刑，丑未刑' in l for l in _lines))
    s103 = calculate_sizhu(date(2024, 1, 3), 10, 0)
    _hs, _hl = Scorer()._calc_hour_zhi_relations_detail(s103)
    check('时柱块寅巳：害+刑并列',
          any('时支巳害日支寅' in l for l in _hl)
          and any('时支巳刑日支寅' in l for l in _hl))
    s106 = calculate_sizhu(date(2024, 1, 6), 16, 0)
    _hs, _hl = Scorer()._calc_hour_zhi_relations_detail(s106)
    check('时柱块巳申：刑+破并列（六合独立计）',
          any('时支申刑日支巳' in l for l in _hl)
          and any('时支申破日支巳' in l for l in _hl)
          and any('时支申合日支巳' in l for l in _hl))

    print('\nverify_20261008_batch：全部断言通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
