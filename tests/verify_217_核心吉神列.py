# -*- coding: utf-8 -*-
"""001 §217：结果表「核心吉神」列口径与 Tooltip 接线断言。

冻结拍板四条：
  A. 数据源合并：命局贵人 details['吉神'] + shensha_list 中 score >= 10 的正分项；
  B. 降噪：<=5 分点缀型杂神不得入列；负分凶煞不得入列；
  C. 排序与截断：命局贵人在前，神煞按分降序，列内最多 4 个 + “…”；
  D. UI：列头正名「核心吉神」，悬停弹层展示命局贵人与神煞完整列表。

退出码：0 全过；1 有失败。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAILS = []


def check(name, cond, detail=''):
    ok = bool(cond)
    print('[%s] %s%s' % ('PASS' if ok else 'FAIL', name,
                        ('  → ' + str(detail)) if detail and not ok else ''))
    if not ok:
        FAILS.append(name)


from 主程序 import (  # noqa: E402
    _extract_tree_jishen,
    _extract_tree_dizhi_jishen,
    _JISHEN_TREE_MIN_SCORE,
    _JISHEN_TREE_MAX_SHOW,
)

# ── A/B/C：合并、降噪、排序、截断 ───────────────────────────────────
_SAMPLE = {
    'wu_xing_result': {'details': {'吉神': ['天乙贵人: 日干庚见时柱未']}},
    'shensha_list': [
        {'name': '岁德', 'score': 20, 'description': '岁之德神'},
        {'name': '鸣吠日', 'score': 15, 'description': '鸣吠日吉'},
        {'name': '时与坐山三合', 'score': 15, 'description': '吉时'},
        {'name': '日贵人时', 'score': 15, 'description': '贵人时'},
        {'name': '岁合', 'score': 12, 'description': '岁合'},
        {'name': '将星', 'score': 12, 'description': '将星'},
        {'name': '上吉日', 'score': 12, 'description': '上吉日'},
        {'name': '山家六合', 'score': 12, 'description': '六合'},
        {'name': '母仓', 'score': 10, 'description': '母仓'},
        {'name': '三合', 'score': 10, 'description': '三合'},
        {'name': '山家贵人', 'score': 10, 'description': '贵人'},
        {'name': '要安', 'score': 8, 'description': '要安'},          # <=5 档邻界：8 分，滤除
        {'name': '补龙', 'score': 8, 'description': '补龙'},
        {'name': '建除十二神-成', 'score': 5, 'description': '成日'},   # 5 分点缀型：滤除
        {'name': '扶山', 'score': 5, 'description': '扶山'},
        {'name': '太岁堆黄', 'score': -15, 'description': '凶'},        # 负分：滤除
        {'name': '天乙贵人', 'score': 10, 'description': '与命局重复'},  # 去重：命局优先
        '非字典项',                                                    # 脏数据：跳过
    ],
}

_text, _full = _extract_tree_jishen(_SAMPLE)

check('A1 命局贵人入列（天乙贵人）', '天乙贵人' in _text, _text)
check('A2 高权重神煞入列（岁德 >= 10）', '岁德' in _text, _text)
check('C1 命局贵人居首', _text.startswith('天乙贵人'), _text)
check('C2 列内截断为 4 个 + 省略号',
      len([x for x in _text.replace('…', '').split('、') if x]) == _JISHEN_TREE_MAX_SHOW
      and _text.endswith('…'), _text)
check('B1 8 分杂神（要安/补龙）不入列',
      '要安' not in _text and '补龙' not in _text, _text)
check('B2 5 分点缀型（建除/扶山）不入列',
      '建除十二神-成' not in _text and '扶山' not in _text, _text)
check('B3 负分凶煞不入列', '太岁堆黄' not in _text, _text)
check('A3 去重：同名天乙贵人只出现一次（命局段）',
      _full.count('天乙贵人') == 1 and '命局贵人：天乙贵人' in _full, _full)
check('D1 悬停完整文本含命局贵人与神煞两段',
      '命局贵人：' in _full and ('神煞吉神（≥%d分）：' % _JISHEN_TREE_MIN_SCORE) in _full,
      _full)
check('D2 完整文本带神煞分值（岁德+20）', '岁德+20' in _full, _full)
check('D3 完整文本覆盖全部 >= 10 分神煞',
      all(n in _full for n in ('鸣吠日', '时与坐山三合', '日贵人时', '岁合', '将星',
                               '上吉日', '山家六合', '母仓', '三合', '山家贵人')), _full)

# 空数据：不显示假吉神
_empty_text, _empty_full = _extract_tree_jishen({})
check('A4 无吉神时列显示 - 且完整文本为空', _empty_text == '-' and _empty_full == '', _empty_text)

# ── D：三返回值兼容 + UI 接线 ─────────────────────────────────────
_dz, _js, _jsf = _extract_tree_dizhi_jishen(_SAMPLE)
check('E1 _extract_tree_dizhi_jishen 返回三值且与单函数一致',
      _js == _text and _jsf == _full, (_dz, _js, _jsf))

_src = open(os.path.join(ROOT, '主程序.py'), encoding='utf-8').read()
check('D4 列头正名「核心吉神」，旧名「吉神信息」已清零',
      '核心吉神' in _src and '吉神信息' not in _src)
check('D5 列标题随输出模式切换（不合格模式显示不合格原因）',
      "_col_title = '不合格原因' if _cur_mode == 'unqualified' else '核心吉神'" in _src)
check('D6 Tooltip 接线（离表/滚轮关闭 + 单元格悬停弹层）',
      'self.result_tree.bind("<Leave>", self._hide_jishen_tooltip, add="+")' in _src
      and 'self.result_tree.bind("<MouseWheel>", self._hide_jishen_tooltip, add="+")' in _src
      and 'def on_tree_motion' in _src and 'Toplevel' in _src)
check('D7 每行完整文本挂载（_jishen_full_map + result["jishen_full"]）',
      '_jishen_full_map[_iid]' in _src and "result.get('jishen_full'" in _src)
check('D8 正常/条件择日两条链路均写入 jishen_full',
      _src.count("'jishen_full': jishen_full,") == 2, _src.count("'jishen_full': jishen_full,"))

print('\n' + ('ALL PASS' if not FAILS else 'FAIL %d：%s' % (len(FAILS), '；'.join(FAILS)))
      , flush=True)
sys.exit(0 if not FAILS else 1)
