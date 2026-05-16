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
出行规则模块
================================================================================
实现出行择日的宜忌规则
================================================================================
"""

from .规则基类 import EventRuleChecker


class TravelRuleChecker(EventRuleChecker):
    """出行规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查出行规则"""
        # 出行宜日
        if self._is_chuxing_yi_day(sizhu):
            yi_list.append('出行')

        # 出行忌日
        if self._is_chuxing_ji_day(sizhu):
            ji_list.append('出行')

        # 远行吉日
        if self._is_yuanxing_jiri(sizhu):
            yi_list.append('远行')

        # 归家吉日
        if self._is_guijia_jiri(sizhu):
            yi_list.append('归家')

        # 事主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('事主八字宜出行')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('事主八字忌出行')

    def _is_chuxing_yi_day(self, sizhu):
        """是否出行宜日"""
        day_zhi = sizhu['day_zhi']
        # 出行宜日：子、寅、卯、巳、午、酉
        yi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in yi_days

    def _is_chuxing_ji_day(self, sizhu):
        """是否出行忌日"""
        day_zhi = sizhu['day_zhi']
        # 出行忌日：丑、辰、未、戌、亥、申
        ji_days = ['丑', '辰', '未', '戌', '亥', '申']
        return day_zhi in ji_days

    def _is_yuanxing_jiri(self, sizhu):
        """是否远行吉日"""
        day_zhi = sizhu['day_zhi']
        # 远行吉日
        yuanxing_days = ['寅', '卯', '巳', '午', '申', '酉']
        return day_zhi in yuanxing_days

    def _is_guijia_jiri(self, sizhu):
        """是否归家吉日"""
        day_zhi = sizhu['day_zhi']
        # 归家吉日
        guijia_days = ['子', '丑', '辰', '未', '戌', '亥']
        return day_zhi in guijia_days

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查事主八字是否宜出行"""
        # 简化判断
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查事主八字是否忌出行"""
        # 简化判断
        return False
