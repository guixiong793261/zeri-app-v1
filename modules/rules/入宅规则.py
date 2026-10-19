# -*- coding: utf-8 -*-
"""
================================================================================
入宅规则模块（基于《钦定协纪辩方书》）
================================================================================
实现入宅、移徙等事项的宜忌规则

核心规则：
1. 入宅吉时：天德、月德、天德合、月德合
2. 入宅忌时：月破、岁破、四离四绝、往亡、归忌
3. 移徙吉日：三合、六合、天赦、母仓
4. 入宅大忌：冲宅主生肖、红嘴朱雀（2026-10-18 删「土符」：三库无「土符×入宅」
   明文，判据(b)五档判定零典据，docs/典据研究_土符入宅_(b)所忌事项范围_取证.md）
================================================================================
"""

from .修造规则 import ConstructionRuleChecker


class RuZhaiRuleChecker(ConstructionRuleChecker):
    """入宅规则检查器
    
    继承修造规则，添加入宅专属规则：
    - 入宅宜忌标签
    - 入宅专属神煞检查
    - 宅主生肖冲合检查
    """
    
    def __init__(self):
        super().__init__()
        self.event_type = '入宅'
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查入宅规则"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list, False, ""
        
        house_type = kwargs.get('house_type')
        shan_xiang = kwargs.get('shan_xiang')
        
        # 1. 建除十二神规则
        self._check_jianchu_ruzhai(date_obj, yi_list, ji_list)
        
        # 2. 天德、月德日
        self._check_tiande_yuede_ruzhai(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 月破、岁破、四离四绝
        self._check_po_and_sili_ruzhai(date_obj, sizhu, owners, ji_list)
        
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
        
        # 8. 入宅专属宜忌
        self._add_ruzhai_yi_ji(yi_list, ji_list)
        
        # 9. 检查一票否决项
        veto, veto_reason = self._check_veto_items(shan_xiang, sizhu, owners, ji_list, yi_list)
        if veto:
            ji_list.append(veto_reason)
            return yi_list, ji_list, True, veto_reason
        
        return yi_list, ji_list, False, ""
    
    def _check_jianchu_ruzhai(self, date_obj, yi_list, ji_list):
        """检查建除十二神（入宅版）"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            ruzhai_yi = ['除', '危', '定', '执', '成', '开']
            ruzhai_ji = ['建', '满', '平', '收', '闭', '破']
            
            if jianchu in ruzhai_yi:
                yi_list.append(f'建除{jianchu}日宜入宅')
            elif jianchu in ruzhai_ji:
                ji_list.append(f'建除{jianchu}日忌入宅')
        except Exception:
            pass
    
    def _check_tiande_yuede_ruzhai(self, date_obj, yi_list):
        """检查天德、月德日（入宅版）"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜入宅')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜入宅')
        except Exception:
            pass
    
    def _check_po_and_sili_ruzhai(self, date_obj, sizhu, owners, ji_list):
        """检查月破、岁破、四离四绝（入宅版）"""
        if not self.has_marriage_shensha:
            return
        
        try:
            # 月破（月支与日支相冲）
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌入宅')
            
            # 四离四绝
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌入宅')
            
            # 岁破（年支与日支相冲）
            year_zhi = sizhu.get('year_zhi', '')
            if year_zhi and self.is_year_break(date_obj, year_zhi):
                ji_list.append('岁破日忌入宅')
            
            # 与事主年支相冲
            if owners:
                for owner in owners:
                    owner_zhi = self._get_owner_year_zhi(owner)
                    if owner_zhi and self.is_year_break(date_obj, owner_zhi):
                        name = owner.get('name', '事主')
                        ji_list.append(f'与{name}年命相冲，忌入宅')
        except Exception:
            pass
    
    def _add_ruzhai_yi_ji(self, yi_list, ji_list):
        """添加入宅宜忌"""
        yi_list.append('入宅')
        yi_list.append('移徙')
