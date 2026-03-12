# -*- coding: utf-8 -*-
"""
================================================================================
神煞模块包
================================================================================
根据事项类型返回相应的神煞检查器

使用方法:
    1. 作为模块导入: from modules.shensha import get_checker
    2. 直接运行: python -m modules.shensha
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    # 添加 shensha 目录到路径
    shensha_dir = os.path.dirname(os.path.abspath(__file__))
    if shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

try:
    from .通用神煞 import CommonShenShaChecker
    from .嫁娶神煞 import MarriageShenShaChecker
    from .修造神煞 import ConstructionShenShaChecker
    from .作灶神煞 import StoveShenShaChecker
    from .开业神煞 import OpeningShenShaChecker
    from .出行神煞 import TravelShenShaChecker
    from .安葬神煞 import BurialShenShaChecker
    from .安床神煞 import BedShenShaChecker
    from .入宅神煞 import RuZhaiShenShaChecker
except ImportError:
    from shensha.通用神煞 import CommonShenShaChecker
    from shensha.嫁娶神煞 import MarriageShenShaChecker
    from shensha.修造神煞 import ConstructionShenShaChecker
    from shensha.作灶神煞 import StoveShenShaChecker
    from shensha.开业神煞 import OpeningShenShaChecker
    from shensha.出行神煞 import TravelShenShaChecker
    from shensha.安葬神煞 import BurialShenShaChecker
    from shensha.安床神煞 import BedShenShaChecker
    from shensha.入宅神煞 import RuZhaiShenShaChecker


def get_checker(event_type):
    """
    根据事项类型获取神煞检查器
    
    Args:
        event_type: 事项类型
        
    Returns:
        ShenShaChecker: 神煞检查器实例
    """
    marriage_events = ['嫁娶', '订婚', '纳采']
    construction_events = ['修造', '动土', '装修']
    stove_events = ['作灶']
    opening_events = ['开业']
    travel_events = ['出行']
    burial_events = ['安葬']
    bed_events = ['安床']
    ruzhai_events = ['入宅', '移徙', '搬家', '迁居']
    
    if event_type in marriage_events:
        return MarriageShenShaChecker()
    elif event_type in construction_events:
        return ConstructionShenShaChecker()
    elif event_type in stove_events:
        return StoveShenShaChecker()
    elif event_type in opening_events:
        return OpeningShenShaChecker()
    elif event_type in travel_events:
        return TravelShenShaChecker()
    elif event_type in burial_events:
        return BurialShenShaChecker()
    elif event_type in bed_events:
        return BedShenShaChecker()
    elif event_type in ruzhai_events:
        return RuZhaiShenShaChecker()
    else:
        return CommonShenShaChecker()


if __name__ == '__main__':
    print("神煞模块包")
    print("使用方法: from modules.shensha import get_checker")
