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
规则模块包
================================================================================
根据事项类型返回相应的规则检查器
================================================================================
"""

from .嫁娶规则 import MarriageRuleChecker
from .修造规则 import ConstructionRuleChecker
from .作灶规则 import StoveRuleChecker
from .开业规则 import OpeningRuleChecker
from .出行规则 import TravelRuleChecker
from .安葬规则 import BurialRuleChecker
from .安床规则 import BedRuleChecker


def get_rule_checker(event_type):
    """
    根据事项类型获取规则检查器
    
    Args:
        event_type: 事项类型
        
    Returns:
        EventRuleChecker: 规则检查器实例
    """
    marriage_events = ['嫁娶', '订婚', '纳采']
    construction_events = ['修造', '动土', '入宅', '装修']
    stove_events = ['作灶']
    opening_events = ['开业']
    travel_events = ['出行']
    burial_events = ['安葬']
    bed_events = ['安床']
    
    if event_type in marriage_events:
        return MarriageRuleChecker()
    elif event_type in construction_events:
        return ConstructionRuleChecker()
    elif event_type in stove_events:
        return StoveRuleChecker()
    elif event_type in opening_events:
        return OpeningRuleChecker()
    elif event_type in travel_events:
        return TravelRuleChecker()
    elif event_type in burial_events:
        return BurialRuleChecker()
    elif event_type in bed_events:
        return BedRuleChecker()
    else:
        # 通用规则检查器
        from .规则基类 import EventRuleChecker
        return EventRuleChecker()
