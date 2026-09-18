# -*- coding: utf-8 -*-
"""
================================================================================
规则模块基类
================================================================================
定义规则检查的基础接口

改进要点：
1. 使用 abc 模块强制子类实现 _check_rules
2. 使用 **kwargs 减少冗余参数
3. _check_rules 直接返回宜忌列表和一票否决状态
4. 添加完整的类型提示
================================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union


class EventRuleChecker(ABC):
    """事项规则检查器基类（抽象类）"""
    
    def __init__(self):
        """初始化规则检查器"""
        pass
    
    def check(self, 
              sizhu: Dict[str, Any], 
              owners: Optional[List[Dict[str, Any]]] = None, 
              **kwargs) -> Tuple[List[str], List[str], bool, str]:
        """
        检查规则（模板方法）
        
        Args:
            sizhu: 四柱信息字典，包含 day_gan, day_zhi, month_zhi, year_zhi 等
            owners: 事主信息列表，每个元素包含 name, 生肖, bazi 等
            **kwargs: 事项特定参数，包括：
                - house_type: 宅型（阳宅/阴宅）
                - shan_xiang: 山向（如"子山午向"）
                - zaoxiang: 灶向（作灶专用）
                - zaowei: 灶位（作灶专用）
                - chuangwei: 床位朝向（安床专用）
        
        Returns:
            tuple: (宜事项列表, 忌事项列表, 一票否决标志, 否决原因)
        
        Raises:
            NotImplementedError: 如果子类未实现 _check_rules
        """
        # 交节日口径：把本次评分的“真实时柱月支”注入上下文，供建除等日级神煞
        # （get_jianchu 内部默认按当日 12:00 取月支）与小黄道(sizhu['月柱'][1])统一。
        def _month_zhi_of(sz):
            try:
                if not isinstance(sz, dict):
                    return ''
                return (sz.get('month_zhi') or sz.get('月支')
                        or (sz.get('月柱')[1] if sz.get('月柱') else ''))
            except Exception:
                return ''
        try:
            from ..shensha.marriage_shensha import (
                push_month_zhi_context, pop_month_zhi_context)
            _mz_token = push_month_zhi_context(_month_zhi_of(sizhu))
        except Exception:
            _mz_token = None

        try:
            # 调用子类实现的具体规则检查
            result = self._check_rules(sizhu, owners, **kwargs)
        finally:
            if _mz_token is not None:
                try:
                    pop_month_zhi_context(_mz_token)
                except Exception:
                    pass

        # 处理返回值（支持新老两种格式）
        if isinstance(result, tuple) and len(result) == 4:
            yi_list, ji_list, veto, veto_reason = result
        elif isinstance(result, tuple) and len(result) == 2:
            yi_list, ji_list = result
            veto = False
            veto_reason = ""
        else:
            yi_list, ji_list = [], []
            veto = False
            veto_reason = ""
        
        # 确保返回值类型正确
        yi_list = yi_list if isinstance(yi_list, list) else []
        ji_list = ji_list if isinstance(ji_list, list) else []
        
        return yi_list, ji_list, veto, veto_reason
    
    @abstractmethod
    def _check_rules(self, 
                     sizhu: Dict[str, Any], 
                     owners: Optional[List[Dict[str, Any]]] = None, 
                     **kwargs) -> Tuple[List[str], List[str], bool, str]:
        """
        检查具体规则（抽象方法，子类必须实现）
        
        Args:
            sizhu: 四柱信息字典
            owners: 事主信息列表
            **kwargs: 事项特定参数
        
        Returns:
            tuple: (宜事项列表, 忌事项列表, 一票否决标志, 否决原因)
        
        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError("子类必须实现 _check_rules 方法")
