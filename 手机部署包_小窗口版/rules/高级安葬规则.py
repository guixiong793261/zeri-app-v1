# -*- coding: utf-8 -*-
"""
================================================================================
高级安葬规则模块
================================================================================
实现高级安葬择日的宜忌规则，加入二十四山项参与

主要功能：
1. 二十四山五行属性分析
2. 二十四山与日支关系分析
3. 二十四山与年支关系分析（三煞、岁破等）
4. 二十四山与月支关系分析
5. 更详细的安葬宜忌规则
================================================================================
"""

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

from .规则基类 import EventRuleChecker

class AdvancedBurialRuleChecker(EventRuleChecker):
    """高级安葬规则检查器"""
    
    def __init__(self):
        super().__init__()
        # 二十四山五行属性
        self.er_shi_si_shan_wuxing = {
            # 北方三山
            '壬': '水', '子': '水', '癸': '水',
            # 东北三山
            '丑': '土', '艮': '土', '寅': '木',
            # 东方三山
            '甲': '木', '卯': '木', '乙': '木',
            # 东南三山
            '辰': '土', '巽': '木', '巳': '火',
            # 南方三山
            '丙': '火', '午': '火', '丁': '火',
            # 西南三山
            '未': '土', '坤': '土', '申': '金',
            # 西方三山
            '庚': '金', '酉': '金', '辛': '金',
            # 西北三山
            '戌': '土', '乾': '金', '亥': '水'
        }
        
        # 地支五行
        self.zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        # 五行生克
        self.wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        self.wuxing_ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        
        # 三煞方位（年支对应）
        self.san_sha = {
            '申': ['巳', '午', '未'],  # 申子辰年煞南方
            '子': ['巳', '午', '未'],
            '辰': ['巳', '午', '未'],
            '寅': ['亥', '子', '丑'],  # 寅午戌年煞北方
            '午': ['亥', '子', '丑'],
            '戌': ['亥', '子', '丑'],
            '巳': ['寅', '卯', '辰'],  # 巳酉丑年煞东方
            '酉': ['寅', '卯', '辰'],
            '丑': ['寅', '卯', '辰'],
            '亥': ['申', '酉', '戌'],  # 亥卯未年煞西方
            '卯': ['申', '酉', '戌'],
            '未': ['申', '酉', '戌']
        }
        
        # 岁破方位（年支对冲）
        self.sui_po = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
    
    def _check_rules(self, sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, yi_list, ji_list):
        """检查安葬规则"""
        # 1. 安葬宜日：阴日
        if self._is_yin_day(sizhu):
            yi_list.append('安葬')
        
        # 2. 安葬忌日：阳日
        if self._is_yang_day(sizhu):
            ji_list.append('安葬')
        
        # 3. 山向相关规则
        if shan_xiang:
            # 山向宜日
            if self._is_shan_xiang_yi(sizhu, shan_xiang):
                yi_list.append(f'{shan_xiang}向安葬')
            
            # 山向忌日
            if self._is_shan_xiang_ji(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向安葬')
            
            # 三煞检查
            if self._is_san_sha(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向犯三煞')
            
            # 岁破检查
            if self._is_sui_po(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向犯岁破')
            
            # 月煞检查
            if self._is_yue_sha(sizhu, shan_xiang):
                ji_list.append(f'{shan_xiang}向犯月煞')
    
    def _is_yin_day(self, sizhu):
        """是否阴日"""
        # 阴日：子、丑、寅、卯、辰、巳
        yin_days = ['子', '丑', '寅', '卯', '辰', '巳']
        return sizhu.get('day_zhi', '') in yin_days
    
    def _is_yang_day(self, sizhu):
        """是否阳日"""
        # 阳日：午、未、申、酉、戌、亥
        yang_days = ['午', '未', '申', '酉', '戌', '亥']
        return sizhu.get('day_zhi', '') in yang_days
    
    def _is_shan_xiang_yi(self, sizhu, shan_xiang):
        """山向宜日"""
        # 安葬宜：山向五行与日支五行相生
        sx_wuxing = self.er_shi_si_shan_wuxing.get(shan_xiang)
        dz_wuxing = self.zhi_wuxing.get(sizhu.get('day_zhi', ''))
        
        return self.wuxing_sheng.get(sx_wuxing) == dz_wuxing
    
    def _is_shan_xiang_ji(self, sizhu, shan_xiang):
        """山向忌日"""
        # 安葬忌：山向五行与日支五行相克
        sx_wuxing = self.er_shi_si_shan_wuxing.get(shan_xiang)
        dz_wuxing = self.zhi_wuxing.get(sizhu.get('day_zhi', ''))
        
        return self.wuxing_ke.get(sx_wuxing) == dz_wuxing
    
    def _is_san_sha(self, sizhu, shan_xiang):
        """是否犯三煞"""
        # 获取年支
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            # 从年柱提取年支
            year_zhu = sizhu.get('年柱', '')
            if len(year_zhu) >= 2:
                year_zhi = year_zhu[1]
        
        # 检查山向是否在三煞方位
        san_sha_directions = self.san_sha.get(year_zhi, [])
        return shan_xiang in san_sha_directions
    
    def _is_sui_po(self, sizhu, shan_xiang):
        """是否犯岁破"""
        # 获取年支
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            # 从年柱提取年支
            year_zhu = sizhu.get('年柱', '')
            if len(year_zhu) >= 2:
                year_zhi = year_zhu[1]
        
        # 检查山向是否是岁破方位
        sui_po_direction = self.sui_po.get(year_zhi, '')
        return shan_xiang == sui_po_direction
    
    def _is_yue_sha(self, sizhu, shan_xiang):
        """是否犯月煞"""
        # 获取月支
        month_zhi = sizhu.get('month_zhi', '')
        if not month_zhi:
            # 从月柱提取月支
            month_zhu = sizhu.get('月柱', '')
            if len(month_zhu) >= 2:
                month_zhi = month_zhu[1]
        
        # 月煞：月支与山向相冲
        yue_sha_directions = self.sui_po.get(month_zhi, '')
        return shan_xiang == yue_sha_directions
    
    def get_er_shi_si_shan_info(self, shan_xiang):
        """获取二十四山信息"""
        if shan_xiang in self.er_shi_si_shan_wuxing:
            return {
                'name': shan_xiang,
                'wuxing': self.er_shi_si_shan_wuxing[shan_xiang]
            }
        return None
    
    def get_forbidden_directions(self, sizhu):
        """
        获取禁止使用的方位列表
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            list: 禁止使用的方位列表
        """
        forbidden = []
        all_directions = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
        
        for direction in all_directions:
            if self._is_shan_xiang_ji(sizhu, direction) or \
               self._is_san_sha(sizhu, direction) or \
               self._is_sui_po(sizhu, direction) or \
               self._is_yue_sha(sizhu, direction):
                forbidden.append(direction)
        
        return forbidden
    
    def is_direction_forbidden(self, sizhu, direction):
        """
        检查某个方位是否被禁止
        
        Args:
            sizhu: 四柱信息
            direction: 方位
            
        Returns:
            bool: 是否被禁止
        """
        return self._is_shan_xiang_ji(sizhu, direction) or \
               self._is_san_sha(sizhu, direction) or \
               self._is_sui_po(sizhu, direction) or \
               self._is_yue_sha(sizhu, direction)

if __name__ == '__main__':
    # 测试代码
    checker = AdvancedBurialRuleChecker()
    
    # 测试四柱
    test_sizhu = {
        '年柱': '戊子',
        '月柱': '庚申',
        '日柱': '辛亥',
        '时柱': '甲午',
        'year_zhi': '子',
        'month_zhi': '申',
        'day_zhi': '亥',
        'hour_zhi': '午'
    }
    
    # 测试山向规则
    test_shan_xiang = '壬'
    print(f"山向 {test_shan_xiang} 五行: {checker.er_shi_si_shan_wuxing.get(test_shan_xiang)}")
    print(f"山向 {test_shan_xiang} 宜日: {checker._is_shan_xiang_yi(test_sizhu, test_shan_xiang)}")
    print(f"山向 {test_shan_xiang} 忌日: {checker._is_shan_xiang_ji(test_sizhu, test_shan_xiang)}")
    print(f"山向 {test_shan_xiang} 犯三煞: {checker._is_san_sha(test_sizhu, test_shan_xiang)}")
    print(f"山向 {test_shan_xiang} 犯岁破: {checker._is_sui_po(test_sizhu, test_shan_xiang)}")
    print(f"山向 {test_shan_xiang} 犯月煞: {checker._is_yue_sha(test_sizhu, test_shan_xiang)}")
    
    # 测试禁止方位
    forbidden = checker.get_forbidden_directions(test_sizhu)
    print(f"\n禁止使用的方位: {forbidden}")
