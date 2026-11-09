# -*- coding: utf-8 -*-
"""001 §234：正常择日结果表「核验」列 + 筛选下拉断言。

用户拍板（2026-11-08）：
  A. 核验列：第 4 位（等级后），显示 'N/5 ✓'，无 detail 显示 '—'，
     与反推页签同口径（modules.排序键.perfect_profile 单点）；
  B. 全✓金底：tag 'allok' background='#FFE680'，优先于星级 tag；
  C. 悬停弹层：_check_full_map 复用 _jishen_tooltip；
  D. 筛选下拉：_check_filter_var ∈ {全部, 极品(5✓), 大吉(4-5✓), 优吉(2-3✓)}，
     切换即 _render_result_tree() 重渲；
  E. 静默事主：渲染路径 _collect_owners_data(silent=True)，弹窗仅在 silent=False 时；
  F. 导入路径：三处手工 insert 各插 '—' 占位（注释恰好出现 3 次）。

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


from modules.排序键 import perfect_profile  # noqa: E402

_src = open(os.path.join(ROOT, '主程序.py'), encoding='utf-8').read()

# ── A：列结构 ─────────────────────────────────────────────────────
check('A1 主程序导入 perfect_profile', 'perfect_profile' in _src.split('模块自查')[0])
_i = _src.find('columns = ("日期/四柱", "评分", "等级", "核验",')
check('A2 columns 第 4 位为「核验」', _i > 0)
check('A3 列宽配置（58/居中/不拉伸）',
      'self.result_tree.column("核验", width=58, anchor=tk.CENTER, stretch=False)' in _src)
check('A4 _update_result_columns 恒显集合含「核验」',
      '"日期/四柱", "评分", "等级", "核验", "五行得分", "月令得分"' in _src)

# ── B：金底 tag ───────────────────────────────────────────────────
check('B1 allok tag 注册', "tag_configure('allok', background='#FFE680')" in _src)
check('B2 极品行替换星级 tag（非叠加；重煞行优先 heavy_warn；§240 极品=日课校验无警告）',
      "('allok',) if _lint_ok else (row_tag,)" in _src
      and "heavy_warn" in _src)

# ── C：悬停弹层 ───────────────────────────────────────────────────
check('C1 _check_full_map 初始化 + 挂载',
      'self._check_full_map = {}' in _src and 'self._check_full_map[_iid] = _chk_tip' in _src)
check('C2 tooltip 文案逐条 ✓/-/✗ 生成（含空事主 N/A 态）',
      "_chk_tip = '\\n'.join(" in _src and "'- ' if _i.get('na')" in _src)
check('C3 on_tree_motion 核验列参与弹层',
      "_cur != _col_j and _cur != _col_c" in _src
      and "if _cur == _col_c" in _src)
check('C4 _tree_column_id 通用化且核心吉神调用同行保留',
      "def _tree_column_id(self, name):" in _src
      and "self._tree_column_id('核心吉神')" in _src)

# ── D：筛选下拉 ───────────────────────────────────────────────────
check('D1 下拉变量与四档选项（§240 文案：极品(无警告)/大吉(≥4✓)）',
      "self._check_filter_var = tk.StringVar(value='全部')" in _src
      and "values=('全部', '极品(无警告)', '大吉(≥4✓)', '优吉(2-3✓)')" in _src)
check('D2 下拉只读 + 切换即重渲',
      "state='readonly'" in _src
      and '_check_cbo.bind("<<ComboboxSelected>>", lambda *_a: self._render_result_tree())' in _src)
check('D3 三档过滤条件（§240：极品=日课校验无警告）',
      "if _flt == '极品(无警告)' and not _lint_ok:" in _src
      and "if _flt == '大吉(≥4✓)' and _ok_n < 4:" in _src
      and "if _flt == '优吉(2-3✓)' and not (2 <= _ok_n <= 3):" in _src)

# ── E：渲染接线与静默事主 ─────────────────────────────────────────
check('E1 渲染处 perfect_profile(result, owners, event_type) 调用（§243 增补 lucky_hours/bride_year_zhi）',
      'perfect_profile(_ck_detail, _owners_ck, _ev_ck' in _src)
check('E2 渲染处静默收集事主',
      '_owners_ck = self._collect_owners_data(silent=True)' in _src)
check('E3 silent 形参 + 弹窗守卫',
      'def _collect_owners_data(self, silent=False):' in _src
      and 'if not silent:' in _src)
check('E4 无 detail 时列显示占位 —',
      "_chk_text = '—'" in _src and "result.get('detail')" in _src)
check('E5 核验列值接入正常渲染 insert', '_chk_text,' in _src)

# ── F：导入路径三处占位 ───────────────────────────────────────────
_n_imp = _src.count('# 001 §234：导入路径无 detail，核验列占位')
check('F1 导入路径占位注释恰好 3 处', _n_imp == 3, _n_imp)

# ── G：perfect_profile 真源（防伪锚点，防误改成分值函数）───────────
_pp = perfect_profile(
    {'score_details': {'旺衰得分': 10}, 'score': 30, 'level': '大吉',
     'veto_reasons': [], 'shensha_list': [{'name': '天德', 'score': 20}]},
    owners=None, event_type='')
check('G1 perfect_profile 返回五维且硬忌/得令项在列',
      isinstance(_pp, dict) and len(_pp.get('items') or []) == 5
      and any(_it.get('key') == '硬忌' for _it in _pp['items'])
      and any(_it.get('key') == '得令' for _it in _pp['items']),
      str(_pp)[:120])

# ── G2：001 §238 专属事项 6 维（修造含扶山补龙+相主双查）────────────────
_pp6 = perfect_profile(
    {'score_details': {'旺衰得分': 10}, 'score': 30, 'level': '大吉',
     'veto_reasons': [], 'shensha_list': [{'name': '补龙', 'score': 12}]},
    owners=None, event_type='修造')
_k6 = [_it.get('key') for _it in (_pp6.get('items') or [])]
check('G2 修造 6 维：得令/合局/德神/扶山补龙/相主/硬忌',
      _k6 == ['得令', '合局', '德神', '扶山补龙', '相主', '硬忌'],
      str(_k6))
check('G3 修造空事主 → 相主 N/A（第三态，不计 ✗）',
      any(_it.get('key') == '相主' and _it.get('na') for _it in _pp6['items']))

print('\n' + ('ALL PASS' if not FAILS else 'FAIL %d：%s' % (len(FAILS), '；'.join(FAILS)))
      , flush=True)
sys.exit(0 if not FAILS else 1)
