# -*- coding: utf-8 -*-
"""
================================================================================
拆舍规则模块（基于《钦定协纪辩方书》）
================================================================================
实现拆舍、拆除等事项的宜忌规则

核心规则：
1. 拆舍吉日：天德、月德、除日、破日（利于拆除）
2. 拆舍忌日：建日、满日、四离四绝
3. 拆舍大忌：冲宅主生肖、三煞
================================================================================
"""

from .修造规则 import ConstructionRuleChecker


class ChaiSheRuleChecker(ConstructionRuleChecker):
    """拆舍规则检查器
    
    继承修造规则，添加拆舍专属规则：
    - 拆舍宜忌标签
    - 拆舍专属神煞检查
    """
    
    def __init__(self):
        super().__init__()
        self.event_type = '拆舍'
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查拆舍规则"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list, False, ""
        
        house_type = kwargs.get('house_type')
        shan_xiang = kwargs.get('shan_xiang')
        
        # 1. 建除十二神规则
        self._check_jianchu_chaishe(date_obj, yi_list, ji_list)
        
        # 2. 天德、月德日
        self._check_tiande_yuede_chaishe(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 月破、四离四绝（岁破已删：岁破批 2026-10-20，001 §140）
        self._check_po_and_sili_chaishe(date_obj, sizhu, owners, ji_list)
        
        # 5. 山向相关规则（扶山）
        zuoshan = self._extract_zuoshan(shan_xiang)
        if zuoshan:
            self._check_fushan(sizhu, zuoshan, owners, yi_list, ji_list)
            self._check_sanhe(sizhu, zuoshan, yi_list)
        
        # 6. 相主：忌与事主生肖相冲
        self._check_shengxiao_chong(sizhu, owners, ji_list)
        
        # 7. 二十四山择吉天机检查
        if shan_xiang and self.has_mountain_data:
            self._check_mountain_yearly_luck(shan_xiang, sizhu, yi_list, ji_list)
            self._check_mountain_monthly_luck(shan_xiang, date_obj, yi_list, ji_list)
            self._check_mountain_avoid_info(shan_xiang, sizhu, ji_list)
            self._check_mountain_keshan(shan_xiang, sizhu, ji_list)
        
        # 8. 拆舍专属宜忌
        self._add_chaishe_yi_ji(yi_list, ji_list)
        
        # 9. 检查一票否决项
        veto, veto_reason = self._check_veto_items(shan_xiang, sizhu, owners, ji_list, yi_list)
        if veto:
            ji_list.append(veto_reason)
            return yi_list, ji_list, True, veto_reason
        
        return yi_list, ji_list, False, ""
    
    def _check_jianchu_chaishe(self, date_obj, yi_list, ji_list):
        """检查建除十二神（拆舍版）"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            # 拆舍宜：除、破（利于拆除）、危、成
            chaishe_yi = ['除', '危', '破', '成', '开']
            chaishe_ji = ['建', '满', '平', '收', '闭', '执', '定']
            
            if jianchu in chaishe_yi:
                yi_list.append(f'建除{jianchu}日宜拆舍')
            elif jianchu in chaishe_ji:
                ji_list.append(f'建除{jianchu}日忌拆舍')
        except Exception:
            pass
    
    def _check_tiande_yuede_chaishe(self, date_obj, yi_list):
        """检查天德、月德日（拆舍版）"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜拆舍')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜拆舍')
        except Exception:
            pass
    
    def _check_po_and_sili_chaishe(self, date_obj, sizhu, owners, ji_list):
        """检查月破、四离四绝（『岁破』日课普适项已删：岁破批 2026-10-20，001 §140）"""
        if not self.has_marriage_shensha:
            return
        
        try:
            # 月破（月支与日支相冲）
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌拆舍')
            
            # 四离四绝
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌拆舍')
            
            # 岁破×拆舍已删（岁破批 2026-10-20，001 §140）：日课普适岁破注册零日课
            # 典据，拍板删日课通道普适忌注册。发射原为：
            #     year_zhi = sizhu.get('year_zhi', '')
            #     if year_zhi and self.is_year_break(date_obj, year_zhi):
            #         ji_list.append('岁破日忌拆舍')
            
            # 与事主年支相冲
            if owners:
                for owner in owners:
                    owner_zhi = self._get_owner_year_zhi(owner)
                    if owner_zhi and self.is_year_break(date_obj, owner_zhi):
                        name = owner.get('name', '事主')
                        ji_list.append(f'与{name}年命相冲，忌拆舍')
        except Exception:
            pass
    
    def _add_chaishe_yi_ji(self, yi_list, ji_list):
        """添加拆舍宜忌"""
        yi_list.append('拆舍')
        yi_list.append('拆除')
