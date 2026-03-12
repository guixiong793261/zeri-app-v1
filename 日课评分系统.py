# -*- coding: utf-8 -*-
"""
专业级日课评分系统 - 独立启动脚本
直接运行此文件即可启动日课评分系统
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.日课评分系统 import DayScoreWindow

if __name__ == '__main__':
    app = DayScoreWindow()
    app.run()
