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
from .高级安葬规则 import AdvancedBurialRuleChecker
from .安床规则 import BedRuleChecker
from .入宅规则 import RuZhaiRuleChecker
from .动土规则 import DongTuRuleChecker
from .拆舍规则 import ChaiSheRuleChecker
from .通用规则 import GenericRuleChecker


def get_rule_checker(event_type):
    """
    根据事项类型获取规则检查器

    2026-09-16 口径统一：事项别名、检查器派发全部以 modules/事项标准.py
    为唯一注册表，本函数仅做转发，禁止再在此维护事项列表。

    Args:
        event_type: 事项类型（规范名或别名，如 嫁娶/订婚/纳采）

    Returns:
        EventRuleChecker: 规则检查器实例
    """
    from ..事项标准 import get_rule_checker as _std_get_rule_checker
    return _std_get_rule_checker(event_type)
