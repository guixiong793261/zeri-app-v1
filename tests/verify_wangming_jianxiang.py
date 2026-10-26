# -*- coding: utf-8 -*-
"""
仙命×兼向 分体并列判定验证（§59.13，2026-10-05 用户拍板①②；
批次一 2026-10-07：主兼双坐山克强制VETO + 兼向独立否决前缀）

口径：
  拍板①分体并列：主山为体（分计入 final_score）、兼向为用（独立成条、
    分数不进 final_score、不双扣）；兼向独立 VETO 仅当
    "兼向判定=坐山克仙命 且 主山判定≠坐山克仙命"（硬触发，无制化出口，
    文案【兼向独立否决】）；主山已坐山克且兼向亦坐山克 →
    主兼双坐山克强制 VETO（制化不豁免，批次一）；
    主山坐山克而兼向非坐山克 → 走主山三级通道，兼向不洗白、不加分。
  拍板②环序约定+三兜底：复用 _update_jianxiang_options 的 idx-1=兼左
    （MOUNTAIN_RING 逆时针）/idx+1=兼右；笼统无左右不硬判仅提示；
    环序映射展示明示约定；"兼X"非相邻山=手动覆盖。

§1 解析函数形态穷举（含非法输入反向断言）
§2 集成·拍板四情形＋同五行＋手动覆盖（走 calculate_score 生产入口，
   日期锚点来自改前基线 C:\\Temp\\baseline_jianxiang_BEFORE.json 实证）
§3 边界反向断言：兼吉不洗白/同凶强制VETO(批次一)/三重叠加去重/
   非法兼向不影响/双凶不扩大/非安葬与无山向路径零污染

退出码：全过 0，失败 1。
"""
import os
import sys
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.二十四山 import parse_shan_xiang_jianxiang  # noqa: E402
from modules.四柱计算器 import calculate_sizhu  # noqa: E402
from modules.评分器 import calculate_score  # noqa: E402

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(('  OK ' if cond else '  FAIL ') + name)


def dead(name, bd):
    return {'name': name, 'role': '死者', '性别': '男', 'birth_date': bd}


def score(ds, shan, jx=None, event='安葬', owners=None):
    d0 = dt.date.fromisoformat(ds) if isinstance(ds, str) else ds
    sz = calculate_sizhu(d0, 12, 0)
    sz.update({'year': d0.year, 'month': d0.month, 'day': d0.day, 'date': d0})
    ow = owners if owners is not None else [dead('甲子', '1924-03-01')]
    return calculate_score(sz, event, ow, None, shan, None, None, None,
                           zaozhu_mode=None, jian_xiang=jx, zeli_mode='feixing')


# ---------------------------------------------------------------------------
# §1 解析函数：形态穷举（正反断言）
# ---------------------------------------------------------------------------
print('== 1. parse_shan_xiang_jianxiang 形态穷举 ==')
r = parse_shan_xiang_jianxiang('甲山庚向兼卯')
check('拼接态：甲兼卯 → 主甲/兼卯/环序映射',
      (r['主山'], r['兼向'], r['兼向来源']) == ('甲', '卯', '环序映射'))

r = parse_shan_xiang_jianxiang('甲山庚向', '兼寅')
check('分传态：甲 + 兼寅（idx-1兼左）→ 主甲/兼寅/环序',
      (r['主山'], r['兼向'], r['兼向来源']) == ('甲', '寅', '环序映射'))

r = parse_shan_xiang_jianxiang('甲山庚向', '卯')
check('分传裸值：甲 + 卯 → 规范化识别为兼卯/环序',
      (r['主山'], r['兼向'], r['兼向来源']) == ('甲', '卯', '环序映射'))

r = parse_shan_xiang_jianxiang('甲山庚向')
check('正向无兼 → 兼向None', r['兼向'] is None and r['主山'] == '甲')

r = parse_shan_xiang_jianxiang('甲山庚向', '正中')
check('正中 → 兼向None', r['兼向'] is None)

r = parse_shan_xiang_jianxiang('甲山庚向兼亥')
check('手动覆盖（拼接）：甲兼亥非相邻 → 兼亥/手动覆盖',
      (r['主山'], r['兼向'], r['兼向来源']) == ('甲', '亥', '手动覆盖'))

r = parse_shan_xiang_jianxiang('庚山甲向兼寅')
check('手动覆盖：庚兼寅（跨多山）→ 手动覆盖',
      (r['兼向'], r['兼向来源']) == ('寅', '手动覆盖'))

r = parse_shan_xiang_jianxiang('壬山丙向兼亥')
check('环序回绕：壬(idx1)兼亥(idx24，idx-1) → 环序映射',
      (r['主山'], r['兼向'], r['兼向来源']) == ('壬', '亥', '环序映射'))

r = parse_shan_xiang_jianxiang('亥山巳向兼壬')
check('环序回绕：亥(idx24)兼壬(idx1，idx+1) → 环序映射',
      (r['主山'], r['兼向'], r['兼向来源']) == ('亥', '壬', '环序映射'))

r = parse_shan_xiang_jianxiang('甲山庚向兼甲')
check('反向：兼向=主山本身 → 非相邻/手动覆盖（不误判环序）',
      r['兼向'] == '甲' and r['兼向来源'] == '手动覆盖')

r = parse_shan_xiang_jianxiang('甲山庚向兼庚')
check('反向：兼对宫庚（差12非相邻）→ 手动覆盖',
      r['兼向'] == '庚' and r['兼向来源'] == '手动覆盖')

r = parse_shan_xiang_jianxiang('甲山庚向', '兼左')
check('反向（旧值/笼统）：兼左非山名 → 不硬判，兼向None', r['兼向'] is None)

r = parse_shan_xiang_jianxiang('甲山庚向兼X')
check('反向：非法兼向字 → 兼向None，主山仍可判',
      r['兼向'] is None and r['主山'] == '甲')

r = parse_shan_xiang_jianxiang('')
check('反向：空山向 → 主山None', r['主山'] is None and r['兼向'] is None)

# ---------------------------------------------------------------------------
# §2 集成：拍板①四情形（改前基线干净日锚点，甲子亡命=海中金）
# ---------------------------------------------------------------------------
print('== 2. 四情形集成（生产入口）==')

# 情形1：主山吉 + 兼向坐山克（反向）→ 兼向独立 VETO（C2，2023-03-06 改前100分大吉）
r = score('2023-03-06', '未山丑向兼丁')
se, jxe = r['shanzuo_eval'], r['shanzuo_eval'].get('兼向判定')
check('情形1 主山：未土生金=坐山生仙命 +20',
      (se['relation'], se['score']) == ('坐山生仙命', 20))
check('情形1 兼向：丁火克金=坐山克仙命 -30，反向标注',
      jxe['relation'] == '坐山克仙命' and jxe['score'] == -30
      and jxe['与主山反向'] is True)
check('情形1 兼向独立VETO触发、总分归零、等级凶',
      any('兼向坐山克仙命' in v for v in r['veto_reasons'])
      and r['score'] == 0 and r['level'] == '❌ 凶')
check('情形1 VETO文案含【兼向独立否决】前缀+反向说明与主山关系',
      any(v.startswith('【兼向独立否决】') and '与主山判定反向' in v
          and '主山未' in v for v in r['veto_reasons']))
check('情形1 兼向分入score_details（仙命兼向得分=-30）',
      r['score_details'].get('仙命兼向得分') == -30)

# 情形2：主山坐山克 + 兼向吉（反向）→ 不额外VETO，兼不洗白（C3，2024-01-06）
r = score('2024-01-06', '丁山癸向兼未')
se, jxe = r['shanzuo_eval'], r['shanzuo_eval'].get('兼向判定')
check('情形2 主山：丁火克金=坐山克仙命 -30（有制化三合WARN）',
      se['relation'] == '坐山克仙命' and se.get('_with_huajie')
      and '三合' in se.get('reason', ''))
check('情形2 兼向：未土生金=坐山生仙命 +20，反向但不洗白',
      jxe['relation'] == '坐山生仙命' and jxe['score'] == 20
      and jxe['与主山反向'] is True)
check('情形2 不额外VETO（兼向通道关闭，主山WARN本无否决）',
      r['veto_reasons'] == []
      and not any('兼向坐山克仙命' in v for v in r['veto_reasons']))
check('情形2 总分95不变（兼向+20不加分）、等级维持封顶凶带三合注',
      r['score'] == 95 and r['level'] == '❌ 凶（坐山克仙命，有制化：三合）')

# 情形3：主山仙命克(小凶) + 兼向坐山克(凶中之凶，同向升级) → VETO（C4，2026-01-07）
r = score('2026-01-07', '巽山乾向兼巳')
se, jxe = r['shanzuo_eval'], r['shanzuo_eval'].get('兼向判定')
check('情形3 主山：巽木=仙命克坐山 -15',
      (se['relation'], se['score']) == ('仙命克坐山', -15))
check('情形3 兼向：巳火=坐山克仙命 -30；同向升级（非反向）',
      jxe['relation'] == '坐山克仙命' and jxe['score'] == -30
      and jxe['与主山反向'] is False)
check('情形3 兼向独立VETO（【兼向独立否决】前缀+升级文案）、归零',
      any(v.startswith('【兼向独立否决】') and '升级为凶中之凶' in v
          for v in r['veto_reasons'])
      and r['score'] == 0 and r['level'] == '❌ 凶')

# 情形4：主山坐山克 + 兼向仙命克(同向较轻) → 不额外VETO（C5，2026-01-07）
r = score('2026-01-07', '巳山亥向兼巽')
se, jxe = r['shanzuo_eval'], r['shanzuo_eval'].get('兼向判定')
check('情形4 主山：巳火=坐山克仙命 -30（有制化三合）',
      se['relation'] == '坐山克仙命' and se.get('_with_huajie'))
check('情形4 兼向：巽木=仙命克坐山 -15（较轻）',
      (jxe['relation'], jxe['score']) == ('仙命克坐山', -15))
check('情形4 不额外VETO、总分98不变、封顶凶注不变',
      r['veto_reasons'] == [] and r['score'] == 98
      and r['level'] == '❌ 凶（坐山克仙命，有制化：三合）')

# 同五行对照：甲兼卯，主兼一致（C1，2024-02-05；H4 批按现行口径重锚 44）
r = score('2024-02-05', '甲山庚向兼卯')
se, jxe = r['shanzuo_eval'], r['shanzuo_eval'].get('兼向判定')
check('同五行：主甲木/兼卯木均=仙命克坐山 -15',
      se['relation'] == '仙命克坐山'
      and jxe['relation'] == '仙命克坐山'
      and jxe['与主山反向'] is False)
check('同五行：无VETO、总分34为现行基线（兼向不双扣；§185 44→34：乙亥日煞西向首酉∈日三煞(向方)-15×0.7=-10）',
      r['veto_reasons'] == [] and r['score'] == 34)

# 手动覆盖：庚兼寅（C6，2026-01-11；H4 批按现行口径重锚 87；§185 立春前年柱
# 乙巳煞东+丑月煞东+辛酉日煞东，向首甲→卯三向方项齐发 -60×0.7=-42 → 45）
r = score('2026-01-11', '庚山甲向兼寅')
se, jxe = r['shanzuo_eval'], r['shanzuo_eval'].get('兼向判定')
check('手动覆盖：主庚金比和0/兼寅木仙命克坐山-15，来源=手动覆盖',
      (se['relation'], se['score']) == ('比和', 0)
      and (jxe['relation'], jxe['score']) == ('仙命克坐山', -15)
      and jxe['来源'] == '手动覆盖')
check('手动覆盖：兼向非坐山克不VETO、总分45为现行基线（-15不进总分；§185 87→45）',
      r['veto_reasons'] == [] and r['score'] == 45)
check('手动覆盖：reason明示已覆盖系统环序映射',
      '手动指定，已覆盖系统环序映射' in r['reason'])

# ---------------------------------------------------------------------------
# §3 边界与反向断言
# ---------------------------------------------------------------------------
print('== 3. 边界反向断言 ==')

# 兼向分不进 final_score 的隔离证据（不能用"有兼/无兼总分相等"：五黄/飞星等
# 既存通道本就消费兼向字，差异与仙命无关）：
# 锚点A 现行基线 C6=45（§185 重冻 87→45，归因见上；若新逻辑把兼向-15计入应=72-42=30）；
# 锚点B 结构断言：仙命坐山得分=0（主山体）、仙命兼向得分=-15（独立披露）。
r_with = score('2026-01-11', '庚山甲向兼寅')
check('兼向分不进总分：C6 final=45 为现行基线（双扣则应为30）',
      r_with['score'] == 45)
check('兼向分不进总分：主山仙命得分=0、兼向-15仅独立披露',
      r_with['score_details'].get('仙命坐山得分') == 0
      and r_with['score_details'].get('仙命兼向得分') == -15)
r_without = score('2026-01-11', '庚山甲向')
check('无兼向案：无仙命兼向得分键、有未指定提示',
      '仙命兼向得分' not in r_without['score_details']
      and '未指定兼向，按正向处理' in r_without['reason'])

# 主兼双坐山克（丙火兼午火，亡命金）→ 批次一强制 VETO（制化不豁免）。
# 2023-03-22 为既有 verify 锚点（丙山无兼：score=100 月德WARN无否决）。
r_same = score('2023-03-22', '丙山壬向兼午')
se = r_same['shanzuo_eval'] or {}
jxe = se.get('兼向判定')
if not (se.get('relation') == '坐山克仙命' and jxe
        and jxe['relation'] == '坐山克仙命'):
    check('同凶强制VETO：2023-03-22 丙兼午 主兼均坐山克（锚点适用）', False)
else:
    check('同凶强制VETO：主兼均坐山克仙命', True)
    check('同凶强制VETO：触发【主兼双坐山克强制否决】、归零、等级凶',
          any(v.startswith('【主兼双坐山克强制否决】')
              for v in r_same['veto_reasons'])
          and r_same['score'] == 0 and r_same['level'] == '❌ 凶')
    check('同凶强制VETO：文案明示制化不豁免、触发源互斥（无兼向独立条目）',
          any('制化不豁免' in v for v in r_same['veto_reasons'])
          and not any('兼向独立否决】' in v for v in r_same['veto_reasons']))
    check('同凶强制VETO：分数层不变——仙命坐山得分仍-30、兼向-30仅披露',
          r_same['score_details'].get('仙命坐山得分') == -30
          and r_same['score_details'].get('仙命兼向得分') == -30)
    check('同凶强制VETO：veto_reasons 无重复条目',
          len(r_same['veto_reasons']) == len(set(r_same['veto_reasons'])))

# 三重凶叠加：主兼双坐山克 + 日支真冲（午日冲甲子命）→
# 双凶叠加与主兼双坐山克两触发源并列各一条、无重复、无兼向独立条目
found3 = None
_d = dt.date(2023, 1, 1)
while _d.year == 2023:
    sz = calculate_sizhu(_d, 12, 0)
    if sz.get('day_zhi') == '午':
        rr = score(_d, '丙山壬向兼午')
        if any('仙命双凶叠加' in v for v in rr['veto_reasons']):
            found3 = (_d.isoformat(), rr)
            break
    _d += dt.timedelta(days=1)
check('三重叠加：2023 找到 丙兼午 午日（真冲+主坐山克+兼坐山克）案例',
      found3 is not None)
if found3:
    _ds3, rr3 = found3
    check(f'三重叠加：{_ds3} 双凶叠加与主兼双坐山克各恰一条、无兼向独立条目',
          sum('仙命双凶叠加' in v for v in rr3['veto_reasons']) == 1
          and sum('主兼双坐山克强制否决' in v for v in rr3['veto_reasons']) == 1
          and not any('兼向独立否决】' in v for v in rr3['veto_reasons']))
    check(f'三重叠加：{_ds3} veto_reasons 无重复条目、归零、等级凶',
          len(rr3['veto_reasons']) == len(set(rr3['veto_reasons']))
          and rr3['score'] == 0 and rr3['level'] == '❌ 凶')
    check(f'三重叠加：{_ds3} 长度恰为2、顺序稳定（双凶叠加→主兼双坐山克）、'
          '两条均有【】标题前缀',
          len(rr3['veto_reasons']) == 2
          and rr3['veto_reasons'][0].startswith('【仙命双凶叠加】')
          and rr3['veto_reasons'][1].startswith('【主兼双坐山克强制否决】'))

# 环序映射明示（兜底2）
r = score('2024-02-05', '甲山庚向兼卯')
check('兜底2：环序映射兼向在reason明示环序约定',
      '系统环序约定（逆时针为兼左、顺时针为兼右）' in r['reason'])

# 非法兼向字：入口单点清洗后与正向同案一致（不硬判、不污染分金/神煞、不否决）
r_bad = score('2023-03-22', '丙山壬向兼X')
r_ok = score('2023-03-22', '丙山壬向')
check('反向：非法兼向字 与 正向 同案 score/level/veto 一致（清洗生效）',
      (r_bad['score'], r_bad['level'], r_bad['veto_reasons'])
      == (r_ok['score'], r_ok['level'], r_ok['veto_reasons'])
      and r_bad['veto_reasons'] == []
      and not any('分金大凶' in v for v in r_bad.get('veto_reasons', [])))
check('反向：非法兼向字不产生兼向判定条目、标记为未识别',
      '兼向判定' not in (r_bad['shanzuo_eval'] or {})
      and (r_bad['shanzuo_eval'] or {}).get('兼向提示') == '未识别')
check('反向：未识别文案进入 reason/详情，明示按正向处理',
      '未能识别为二十四山山字' in r_bad['reason']
      and '未能识别' in r_bad['score_details'].get('仙命兼向详情', ''))
# 旧选项值"兼左"同样清洗
r_old = score('2023-03-22', '丙山壬向兼左')
check('反向：旧值兼左 与 正向 同案 score/level/veto 一致',
      (r_old['score'], r_old['level'], r_old['veto_reasons'])
      == (r_ok['score'], r_ok['level'], r_ok['veto_reasons'])
      and (r_old['shanzuo_eval'] or {}).get('兼向提示') == '未识别')

# 双凶定义不扩大：主山非坐山克 + 兼向坐山克 + 日支真冲（午日）→
# 仅兼向VETO，不得出现"仙命双凶叠加"文案（双凶维持主山定义）
found = None
_d = dt.date(2023, 1, 1)
while _d.year == 2023:
    sz = calculate_sizhu(_d, 12, 0)
    if sz.get('day_zhi') == '午':
        rr = score(_d, '未山丑向兼丁')
        if any('兼向坐山克仙命' in v for v in rr['veto_reasons']):
            found = (_d.isoformat(), rr)
            break
    _d += dt.timedelta(days=1)
check('双凶不扩大：2023 找到 未兼丁 午日（真冲+兼向凶克）案例', found is not None)
if found:
    _ds, rr = found
    check(f'双凶不扩大：{_ds} 只有兼向VETO、无仙命双凶叠加文案',
          any('兼向坐山克仙命' in v for v in rr['veto_reasons'])
          and not any('仙命双凶叠加' in v for v in rr['veto_reasons']))

# 非安葬路径零污染：嫁娶无死者 → shanzuo_eval=None，reason 无兼向提示
r_jq = score('2026-02-22', '甲山庚向兼卯', event='嫁娶',
             owners=[{'name': '新郎', '性别': '男', 'role': '新郎',
                      'birth_date': '1990-05-01'}])
check('非安葬：shanzuo_eval=None、reason不含仙命兼向段',
      r_jq.get('shanzuo_eval') is None
      and '仙命×兼向' not in r_jq.get('reason', ''))

# 安葬无山向 → shanzuo_eval=None
r_no = score('2026-02-22', None)
check('安葬无山向：shanzuo_eval=None', r_no.get('shanzuo_eval') is None)

# 分传态引擎直连：shan/jian 分传与拼接态等价
r1 = score('2023-03-06', '未山丑向', '兼丁')
r2 = score('2023-03-06', '未山丑向兼丁')
check('分传态=拼接态：兼向VETO与score一致',
      (r1['score'], [v[:6] for v in r1['veto_reasons']])
      == (r2['score'], [v[:6] for v in r2['veto_reasons']])
      and any('兼向坐山克仙命' in v for v in r1['veto_reasons']))

print('=' * 60)
print(f'PASS {len(PASS)}  FAIL {len(FAIL)}')
if FAIL:
    print('FAIL 项:')
    for f in FAIL:
        print('  - ' + f)
    sys.exit(1)
print('ALL PASS')
sys.exit(0)
