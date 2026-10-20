import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

# -*- coding: utf-8 -*-
"""
================================================================================
通用规则模块
================================================================================
为「入学 / 求医 / 签约」等未设专属规则文件的事项提供基线宜忌检查。

历史问题（2026-09-16 修复）：rules/__init__.py 的兜底分支返回抽象基类
EventRuleChecker()，实例化即 TypeError，导致这三类事项在评分器中一律走
异常兜底（score=0 / level='计算错误'），报告无任何宜忌。

设计原则：不新增流派口径，全部复用系统内既有权威来源——
1. 建除十二神宜忌
   - 源一：modules/黄道.py 的 XIAO_HUANG_DAO_YIJI（与黄道评分同源，
     保证「宜/忌」字样与该日黄道加分/减分不矛盾）；
   - 源二：modules/五行择日法.py 的 EVENT_RULES（正五行口径，建除项写作"X日"）。
   事项名经 EVENT_ALIASES 映射后匹配；两源冲突（同日既宜又忌）时两边都不计。
2. 天德/月德日宜；月破/四离四绝忌（「岁破」已删：岁破批 2026-10-20，001 §140）；
   日柱冲事主年支忌
   —— 与开业/安床/出行等事项规则检查器完全同口径。
3. 不作一票否决（同开业/安床），仅产出宜忌条目。
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date


class GenericRuleChecker(EventRuleChecker):
    """通用规则检查器（入学/求医/签约 等无专属规则文件的事项）"""

    # 事项名 → 黄道宜忌表中的同义项（黄道表按通书用语书写，非事项名）
    EVENT_ALIASES = {
        '入学': ('入学',),
        '求医': ('求医', '治病', '疗病'),
        '签约': ('签约', '立券', '立约', '交易'),
    }

    # 事项名 → 五行择日法.EVENT_RULES 键（正五行口径的事项宜忌表）
    EVENT_RULES_KEY = {
        '入学': '入学',
        '签约': '立券交易',
    }

    # 地支 ↔ 生肖
    ZODIAC_TO_ZHI = {
        '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
        '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
        '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥',
    }

    # 地支六冲
    CHONG = {
        '子': '午', '午': '子', '丑': '未', '未': '丑',
        '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳',
    }

    def __init__(self, event_type=''):
        super().__init__()
        self.event_type = event_type
        self._check_marriage_deps()
        self._load_yiji_sources()

    def _check_marriage_deps(self):
        """初始化择日基础判定依赖（与开业/安床同源）"""
        self.has_marriage_shensha = False
        self.get_jianchu = None
        self.is_tiande_day = None
        self.is_yuede_day = None
        self.is_month_break = None
        self.is_year_break = None
        self.is_sili_sijue = None

        try:
            from ..shensha.marriage_shensha import (
                get_jianchu, is_tiande_day, is_yuede_day,
                is_month_break, is_year_break, is_sili_sijue
            )
            self.get_jianchu = get_jianchu
            self.is_tiande_day = is_tiande_day
            self.is_yuede_day = is_yuede_day
            self.is_month_break = is_month_break
            self.is_year_break = is_year_break
            self.is_sili_sijue = is_sili_sijue
            self.has_marriage_shensha = True
        except ImportError:
            pass

    def _load_yiji_sources(self):
        """加载两处既有宜忌权威表（失败则对应源不参与判定，不影响主流程）"""
        try:
            from ..黄道 import 黄道计算器
            self._xiao_huang_dao_yiji = 黄道计算器.XIAO_HUANG_DAO_YIJI
        except Exception:
            self._xiao_huang_dao_yiji = {}
        try:
            from ..五行择日法 import WuXingZeRiFa
            self._event_rules = WuXingZeRiFa.EVENT_RULES
        except Exception:
            self._event_rules = {}

    def _sizhu_to_date(self, sizhu):
        """从sizhu构建日期对象"""
        if 'date' in sizhu:
            return sizhu['date']

        try:
            year = int(sizhu.get('year', sizhu.get('年柱', '2000')[0:4]))
            month = int(sizhu.get('month', 1))
            day = int(sizhu.get('day', 1))
            return date(year, month, day)
        except Exception:
            return None

    def _get_owner_year_zhi(self, owner):
        """获取事主年支（与开业规则同口径）"""
        zodiac = owner.get('生肖', '') or owner.get('zodiac', '')
        if zodiac:
            return self.ZODIAC_TO_ZHI.get(zodiac, '')

        zhi = owner.get('年支', '') or owner.get('year_zhi', '')
        if zhi:
            return zhi

        if 'birth_date' in owner:
            try:
                from ..四柱计算器 import calculate_sizhu
                birth_sizhu = calculate_sizhu(
                    owner['birth_date'],
                    owner.get('birth_hour', 12),
                    owner.get('birth_minute', 0),
                    longitude=owner.get('birth_longitude')
                )
                return birth_sizhu['年柱'][1]
            except Exception:
                pass

        return ''

    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查通用规则；返回 (宜列表, 忌列表, 否决标志, 否决原因)"""
        yi_list = []
        ji_list = []

        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list, False, ''

        event_type = self.event_type or ''

        self._check_jianchu(date_obj, event_type, yi_list, ji_list)
        self._check_tiande_yuede(date_obj, event_type, yi_list)
        self._check_po_and_sili(date_obj, sizhu, owners, event_type, ji_list)
        self._check_shengxiao_chong(sizhu, owners, ji_list)

        return yi_list, ji_list, False, ''

    def _check_jianchu(self, date_obj, event_type, yi_list, ji_list):
        """建除十二神宜忌：黄道表 + 五行择日法事项表 双源合并（冲突不计）"""
        if not self.get_jianchu or not event_type:
            return

        try:
            jianchu = self.get_jianchu(date_obj)
        except Exception:
            return
        if not jianchu:
            return

        aliases = self.EVENT_ALIASES.get(event_type, (event_type,))
        yi_hit = ji_hit = False

        # 源一：小黄道十二建星宜忌表（与黄道评分同源）
        table = self._xiao_huang_dao_yiji.get(jianchu) or {}
        if any(a in table.get('yi', []) for a in aliases):
            yi_hit = True
        if any(a in table.get('ji', []) for a in aliases):
            ji_hit = True

        # 源二：正五行事项宜忌表（建除项写作"X日"）
        rules_key = self.EVENT_RULES_KEY.get(event_type, '')
        rules = self._event_rules.get(rules_key) or {} if rules_key else {}
        if f'{jianchu}日' in rules.get('宜', []):
            yi_hit = True
        if f'{jianchu}日' in rules.get('忌', []):
            ji_hit = True

        if yi_hit and ji_hit:
            # 两源口径冲突，不作宜忌判定，避免报告内"宜/忌"并存
            return
        if yi_hit:
            yi_list.append(f'建除{jianchu}日宜{event_type}')
        elif ji_hit:
            ji_list.append(f'建除{jianchu}日忌{event_type}')

    def _check_tiande_yuede(self, date_obj, event_type, yi_list):
        """天德、月德日宜（通用吉神）"""
        if not self.has_marriage_shensha or not event_type:
            return

        try:
            if self.is_tiande_day(date_obj):
                yi_list.append(f'天德日宜{event_type}')
            if self.is_yuede_day(date_obj):
                yi_list.append(f'月德日宜{event_type}')
        except Exception:
            pass

    def _check_po_and_sili(self, date_obj, sizhu, owners, event_type, ji_list):
        """月破、四离四绝忌（非一票否决，同开业/安床）
        （『岁破』日课普适项已删：岁破批 2026-10-20，001 §140）"""
        if not self.has_marriage_shensha or not event_type:
            return

        try:
            if self.is_month_break(date_obj):
                ji_list.append(f'月破日忌{event_type}')

            if self.is_sili_sijue(date_obj):
                ji_list.append(f'四离四绝日忌{event_type}')

            # 岁破×通用（f-string 覆盖 入学/求医/签约/通用 等 event_type）已删
            # （岁破批 2026-10-20，001 §140）：日课普适岁破注册零日课典据（协纪卷内
            # 「岁破日」0 命中），拍板删日课通道普适忌注册。删除后 4 事项逐一断言清零。
            # 发射原为：
            #     year_zhi = sizhu.get('year_zhi', '')
            #     if year_zhi and self.is_year_break(date_obj, year_zhi):
            #         ji_list.append(f'岁破日忌{event_type}')
        except Exception:
            pass

    def _check_shengxiao_chong(self, sizhu, owners, ji_list):
        """日/时/年/月柱冲事主年支（日柱为主）"""
        if not owners:
            return

        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return

        for owner in owners:
            if not isinstance(owner, dict):
                continue
            name = owner.get('name', '事主')
            owner_zhi = self._get_owner_year_zhi(owner)
            target = self.CHONG.get(owner_zhi, '')
            if not target:
                continue
            if sizhu.get('day_zhi', '') == target:
                ji_list.append(f'日柱{day_zhi}冲{name}')
            if sizhu.get('hour_zhi', '') == target:
                ji_list.append(f'时柱{sizhu.get("hour_zhi", "")}冲{name}')
            if sizhu.get('year_zhi', '') == target:
                ji_list.append(f'年柱{sizhu.get("year_zhi", "")}冲{name}')
            if sizhu.get('month_zhi', '') == target:
                ji_list.append(f'月柱{sizhu.get("month_zhi", "")}冲{name}')


# 测试
if __name__ == '__main__':
    from modules.四柱计算器 import calculate_sizhu

    for _ev in ['入学', '求医', '签约']:
        checker = GenericRuleChecker(_ev)
        _sz = calculate_sizhu(date(2026, 3, 10), 12, 0)
        _sz['year'], _sz['month'], _sz['day'], _sz['date'] = 2026, 3, 10, date(2026, 3, 10)
        _yi, _ji, _veto, _reason = checker.check(_sz, None)
        print(f"{_ev}: 宜={_yi} 忌={_ji} 否决={_veto} {_reason}")