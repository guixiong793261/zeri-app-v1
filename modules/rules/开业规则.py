import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

# -*- coding: utf-8 -*-
"""
================================================================================
开业规则模块
================================================================================
实现开业择日的宜忌规则
================================================================================
"""

from .规则基类 import EventRuleChecker


class OpeningRuleChecker(EventRuleChecker):
    """开业规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查开业规则"""
        # 开业宜日
        if self._is_kaiye_yi_day(sizhu):
            yi_list.append('开业')

        # 开业忌日
        if self._is_kaiye_ji_day(sizhu):
            ji_list.append('开业')

        # 开市吉日
        if self._is_kaishi_jiri(sizhu):
            yi_list.append('开市')

        # 纳财吉日
        if self._is_nacai_jiri(sizhu):
            yi_list.append('纳财')

        # 事主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('事主八字宜开业')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('事主八字忌开业')

    def _is_kaiye_yi_day(self, sizhu):
        """是否开业宜日"""
        day_zhi = sizhu['day_zhi']
        # 开业宜日：子、寅、卯、巳、午、酉
        yi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in yi_days

    def _is_kaiye_ji_day(self, sizhu):
        """是否开业忌日"""
        day_zhi = sizhu['day_zhi']
        # 开业忌日：丑、辰、未、戌、亥、申
        ji_days = ['丑', '辰', '未', '戌', '亥', '申']
        return day_zhi in ji_days

    def _is_kaishi_jiri(self, sizhu):
        """是否开市吉日"""
        day_zhi = sizhu['day_zhi']
        day_gan = sizhu['day_gan']
        # 开市吉日：满日、成日、开日
        kaishi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in kaishi_days

    def _is_nacai_jiri(self, sizhu):
        """是否纳财吉日"""
        day_zhi = sizhu['day_zhi']
        # 纳财吉日
        nacai_days = ['寅', '卯', '巳', '午', '申', '酉']
        return day_zhi in nacai_days

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查事主八字是否宜开业"""
        # 简化判断
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查事主八字是否忌开业"""
        # 简化判断
        return False
