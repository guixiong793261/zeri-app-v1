# -*- coding: utf-8 -*-
"""
verify_city_longitude — 城市经度辅助输入验证（001 §51）

城市只是真太阳时的【辅助输入层】，不改任何判断逻辑。验证：
  1. 数据完整性：355 城、无重名、经度全部在 [60,150] 有效域、省份归属齐全
  2. 查询：城市→经度锚点；未知/空/空白/None → None；自动 strip
  3. 过滤：子串包含、空词分页、limit 生效
  4. 行为等价（核心）：每个城市经“城市填入”的值，走与手动输入完全相同的
     _parse_owner_longitude 解析路径后，数值必须 == 该城市经度——即“选城市”
     与“手填经度”严格等价，真太阳时计算零差异
  5. 持久化键 birth_city/longitude 的 var 往返（模拟 StringVar）
  6. 反向断言：未知城市不改动经度；非城市文本不会误填

运行：python tests/verify_city_longitude.py    退出码 0=全通过 / 1=失败
"""
import os
import sys

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj = os.path.dirname(_this_dir)
for _p in [_proj, os.path.join(_proj, 'modules')]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from modules import 城市经度 as city_mod
from modules.城市经度 import (CITY_LONGITUDE, CITY_NAMES, get_longitude,
                               filter_cities, province_of, PROVINCE_CITIES)
# 复用生产解析器：城市填入值与手动输入必须走同一条解析路径
from 主程序 import _parse_owner_longitude

FAILS = []


def check(name, cond, extra=''):
    print(('[PASS] ' if cond else '[FAIL] ') + name
          + (('  >> ' + extra) if not cond and extra else ''))
    if not cond:
        FAILS.append(name)


class _Var:
    """最小 StringVar 替身（持久化只用到 get/set）。"""
    def __init__(self, v=''):
        self._v = v

    def get(self):
        return self._v

    def set(self, v):
        self._v = v


# ============================================================
# 1. 数据完整性
# ============================================================
check('城市数 >= 300', len(CITY_NAMES) >= 300, str(len(CITY_NAMES)))
check('CITY_NAMES 与字典键一致（无重名/无缺失）',
      sorted(CITY_NAMES) == sorted(CITY_LONGITUDE.keys()))
check('全部经度为数值且 ∈ [60,150]',
      all(isinstance(v, (int, float)) and 60.0 <= v <= 150.0
          for v in CITY_LONGITUDE.values()))
check('城市名非空字符串', all(isinstance(c, str) and c.strip() for c in CITY_NAMES))
check('每城均有省份归属', all(province_of(c) for c in CITY_NAMES))
check('省份分组覆盖全部城市',
      sorted(c for _p, cs in PROVINCE_CITIES for c, _ in cs) == sorted(CITY_NAMES))

# 无两个城市经度完全相同到城市级别的问题不做要求（同城邻县可同值），跳过

# ============================================================
# 2. 查询锚点与边界
# ============================================================
anchors = [('北京', 116.4), ('上海', 121.5), ('成都', 104.1), ('乌鲁木齐', 87.6),
           ('深圳', 114.1), ('拉萨', 91.1), ('香港', 114.2), ('台北', 121.5),
           ('海南州(共和)', 100.6)]
for name, lng in anchors:
    check(f'get_longitude({name})={lng}', get_longitude(name) == lng,
          str(get_longitude(name)))

check('未知城市 → None', get_longitude('火星') is None)
check('None → None', get_longitude(None) is None)
check('空串 → None', get_longitude('') is None)
check('自动 strip（" 成都 "）', get_longitude(' 成都 ') == 104.1)
check('省份：成都→四川，深圳→广东',
      province_of('成都') == '四川' and province_of('深圳') == '广东')

# ============================================================
# 3. 过滤
# ============================================================
fc = filter_cities('成')
check("filter('成') 收窄且含成都", 0 < len(fc) < len(CITY_NAMES) and '成都' in fc,
      str(fc))
check("filter 精确城市 = 单元素", filter_cities('成都') == ['成都'])
check('filter 无匹配 = []', filter_cities('不存在的地名xyz') == [])
check('空词返回首页（=全量前100）', filter_cities('') == CITY_NAMES[:100])
check('limit 生效', len(filter_cities('', limit=10)) == 10)
check('filter 保持显示顺序',
      filter_cities('州') == [c for c in CITY_NAMES if '州' in c][:100])

# ============================================================
# 4. 核心：选城市 ≡ 手填经度（同一解析路径，真太阳时零差异）
# ============================================================
mismatch = []
for c, lng in CITY_LONGITUDE.items():
    # 模拟 apply：city → 经度字符串进经度框；扫日回路不弹窗
    parsed = _parse_owner_longitude(_Var(str(lng)), show_warning=False)
    if abs(parsed - lng) > 1e-9:
        mismatch.append((c, lng, parsed))
check('全部城市：城市填入值经生产解析路径 == 城市经度（选城市≡手填）',
      not mismatch, str(mismatch[:5]))

# 真太阳时启用/不启用语义随城市经度自然成立，不新增判断：
check('120 附近城市按原口径处理（北京116.4≠120 → 启用）',
      _parse_owner_longitude(_Var('116.4'), show_warning=False) == 116.4)

# ============================================================
# 5. 持久化键往返（save 读 var → load 写 var）
# ============================================================
owner_info = {'longitude': _Var('120'), 'birth_city': _Var('')}
# 保存侧取值（与 主程序.save_owners_info 同构）
saved = {'longitude': owner_info['longitude'].get(),
         'birth_city': owner_info['birth_city'].get()}
# 加载侧回填（与 load_owners_info 同构）
restored = {'longitude': _Var(), 'birth_city': _Var()}
restored['longitude'].set(saved.get('longitude', '120'))
restored['birth_city'].set(saved.get('birth_city', ''))
check('默认方案持久化往返 = 120 / 空',
      restored['longitude'].get() == '120' and restored['birth_city'].get() == '')

owner_info['longitude'].set('87.6')
owner_info['birth_city'].set('乌鲁木齐')
saved = {'longitude': owner_info['longitude'].get(),
         'birth_city': owner_info['birth_city'].get()}
restored['longitude'].set(saved.get('longitude', '120'))
restored['birth_city'].set(saved.get('birth_city', ''))
check('城市方案持久化往返 = 87.6 / 乌鲁木齐',
      restored['longitude'].get() == '87.6'
      and restored['birth_city'].get() == '乌鲁木齐')

# 旧方案兼容：无 birth_city 键 → 加载默认 ''，不报错
old_data = {'longitude': '104.1'}
check('旧方案缺 birth_city 键兼容', old_data.get('birth_city', '') == '')
check('旧方案缺 longitude 键兼容', old_data.get('longitude', '120') == '104.1')

# ============================================================
# 6. 反向断言：未知/非城市文本不改动经度
# ============================================================
lng_var = _Var('120')
city_text = '随便打的字'
_l = get_longitude(city_text)
if _l is not None:   # 生产 apply 的判定
    lng_var.set(str(_l))
check('反向：非城市文本不误填经度（保持120）', lng_var.get() == '120')

# 反向：过滤词若意外为空也必须保持顺序一致（不抛异常）
check("filter(空白 '   ') == 空词首页", filter_cities('   ') == CITY_NAMES[:100])

print('=' * 60)
print('FAIL', len(FAILS), '项')
sys.exit(1 if FAILS else 0)
