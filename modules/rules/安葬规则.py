# -*- coding: utf-8 -*-
"""
================================================================================
安葬规则模块（已废弃）
================================================================================
本模块已于 §186（2026-10-26 安葬深水区修复批）废弃。

历史问题：
1. 重丧日起例误作「春月甲乙、夏月丙丁、秋月庚辛、冬月壬癸 + 初三/二十七」，
   与正统口诀「正七连庚甲，二八乙辛当…」完全不符。
2. 三丧日起例误作「春戌夏丑秋辰冬未」（实为四击/杀师日表），
   正统三丧为「春辰夏未秋戌冬丑」（四季墓库派）。
3. 重丧/三丧/复日/年重丧在本模块为 early-return 一票否决，
   但活跃路径（高级安葬规则）仅扣分不否决，两轨口径冲突。

迁移：安葬事项规则检查器已统一为 AdvancedBurialRuleChecker（见 高级安葬规则.py）。
本模块保留 BurialRuleChecker 作为薄别名，仅为兼容 rules/__init__.py 的历史导入，
不再承载任何业务逻辑。请勿在此模块新增代码。
================================================================================
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
modules_dir = os.path.dirname(os.path.abspath(__file__))
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

try:
    from .高级安葬规则 import AdvancedBurialRuleChecker as _ActiveChecker
except ImportError:
    from 高级安葬规则 import AdvancedBurialRuleChecker as _ActiveChecker


class BurialRuleChecker(_ActiveChecker):
    """安葬规则检查器（废弃别名）。

    已迁移至 AdvancedBurialRuleChecker。本类仅作向后兼容占位，
    不承载独立业务逻辑。新代码请直接使用 AdvancedBurialRuleChecker。
    """
    pass
