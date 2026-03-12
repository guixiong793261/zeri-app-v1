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
作灶规则模块
================================================================================
实现作灶择日的宜忌规则
================================================================================
"""

from .规则基类 import EventRuleChecker


class StoveRuleChecker(EventRuleChecker):
    """作灶规则检查器"""

    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查作灶规则"""
        # 作灶宜日
        if self._is_zuozao_yi_day(sizhu):
            yi_list.append('作灶')

        # 作灶忌日
        if self._is_zuozao_ji_day(sizhu):
            ji_list.append('作灶')

        # 灶向相关规则
        if zaoxiang:
            if self._is_zaoxiang_yi(sizhu, zaoxiang):
                yi_list.append(f'{zaoxiang}向作灶')
            if self._is_zaoxiang_ji(sizhu, zaoxiang):
                ji_list.append(f'{zaoxiang}向作灶')

        # 灶位相关规则
        if zaowei:
            if self._is_zaowei_yi(sizhu, zaowei):
                yi_list.append(f'{zaowei}位安灶')
            if self._is_zaowei_ji(sizhu, zaowei):
                ji_list.append(f'{zaowei}位安灶')

        # 宅主八字相关规则
        if owners:
            for owner in owners:
                if self._check_owner_bazi_yi(sizhu, owner):
                    yi_list.append('宅主八字宜作灶')
                if self._check_owner_bazi_ji(sizhu, owner):
                    ji_list.append('宅主八字忌作灶')

    def _is_zuozao_yi_day(self, sizhu):
        """是否作灶宜日"""
        day_zhi = sizhu['day_zhi']
        # 作灶宜日：子、寅、卯、巳、午、酉
        yi_days = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in yi_days

    def _is_zuozao_ji_day(self, sizhu):
        """是否作灶忌日"""
        day_zhi = sizhu['day_zhi']
        # 作灶忌日：丑、辰、未、戌、亥、申
        ji_days = ['丑', '辰', '未', '戌', '亥', '申']
        return day_zhi in ji_days

    def _is_zaoxiang_yi(self, sizhu, zaoxiang):
        """灶向宜日"""
        # 灶向五行与日支五行相生为宜
        zaoxiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }

        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        zx_wuxing = zaoxiang_wuxing.get(zaoxiang)
        dz_wuxing = zhi_wuxing.get(sizhu['day_zhi'])

        # 五行相生
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng.get(zx_wuxing) == dz_wuxing

    def _is_zaoxiang_ji(self, sizhu, zaoxiang):
        """灶向忌日"""
        # 灶向五行与日支五行相克为忌
        zaoxiang_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水',
        }

        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        zx_wuxing = zaoxiang_wuxing.get(zaoxiang)
        dz_wuxing = zhi_wuxing.get(sizhu['day_zhi'])

        # 五行相克
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return ke.get(zx_wuxing) == dz_wuxing

    def _is_zaowei_yi(self, sizhu, zaowei):
        """灶位宜日"""
        # 灶位五行与日支五行相生为宜
        return self._is_zaoxiang_yi(sizhu, zaowei)

    def _is_zaowei_ji(self, sizhu, zaowei):
        """灶位忌日"""
        # 灶位五行与日支五行相克为忌
        return self._is_zaoxiang_ji(sizhu, zaowei)

    def _check_owner_bazi_yi(self, sizhu, owner):
        """检查宅主八字是否宜作灶"""
        # 简化判断，实际应根据宅主八字详细分析
        # 宅主日柱与作灶日相生或比和为宜
        return True

    def _check_owner_bazi_ji(self, sizhu, owner):
        """检查宅主八字是否忌作灶"""
        # 简化判断，实际应根据宅主八字详细分析
        # 宅主日柱与作灶日相冲为忌
        return False
