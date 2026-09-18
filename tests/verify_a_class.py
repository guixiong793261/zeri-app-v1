# -*- coding: utf-8 -*-
"""
A 类神煞第一批批量验证
=======================

覆盖：五不遇时、天乙贵人、禄神、羊刃、文昌贵人、
      三合、六合、六冲、六害、三刑、相破

用法：
  python tests/verify_a_class.py --all          # 跑全部（默认）
  python tests/verify_a_class.py --case 天乙贵人 # 只跑指定
  python tests/verify_a_class.py --verbose      # 打印差异明细
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shensha_verify_engine import run_cli

# 导入各神煞用例
from verify_wubuyushi import case as c_wubuyushi
from verify_tianyi import case as c_tianyi
from verify_lushen import case as c_lushen
from verify_yangren import case as c_yangren
from verify_wenchang import case as c_wenchang
from verify_sanhe import case as c_sanhe
from verify_liuhe import case as c_liuhe
from verify_liuchong import case as c_liuchong
from verify_liuhai import case as c_liuhai
from verify_sanxing import case as c_sanxing
from verify_po import case as c_po

CASES = [
    c_wubuyushi, c_tianyi, c_lushen, c_yangren, c_wenchang,
    c_sanhe, c_liuhe, c_liuchong, c_liuhai, c_sanxing, c_po,
]


if __name__ == '__main__':
    sys.exit(run_cli(CASES))
