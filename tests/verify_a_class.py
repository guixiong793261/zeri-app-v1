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

# 第二批神煞（劫煞/灾煞/岁煞/驿马真空亡，2026-09-18 接入）
from verify_jiesha import case_base as c_jiesha_base, case_table as c_jiesha_table
from verify_zaisha import case_base as c_zaisha_base, case_table as c_zaisha_table
from verify_suisha import (
    case_base as c_suisha_base,
    case_dongtu as c_suisha_dongtu,
    case_table as c_suisha_table,
)
from verify_yima import cases as c_yima_cases
from verify_yuesha import case_base as c_yuesha_base
from verify_yaoan import CASES as c_yaoan_cases
from verify_wufu import CASES as c_wufu_cases
from verify_fusheng import CASES as c_fusheng_cases
from verify_shengqi import CASES as c_shengqi_cases
# 广度扩展 A1 批（比较对象错 7 项：岁德/岁德合/月空/天马/反支/天恩/鸣吠+鸣吠对，2026-10）
from verify_a1_bijiao import CASES as c_a1_cases
# 广度扩展 A2 批（名实错 4 项：阴德/四击/土府/地囊，2026-10）
from verify_a2_mingshi import CASES as c_a2_cases
# 广度扩展 A3 批（表本身错 3 项：飞廉/八专/五墓，2026-10）
from verify_a3_biaocuo import CASES as c_a3_cases
# 广度扩展 A4 批（逻辑错 2 项：将星中神专位/三奇顺布连珠，2026-10）
from verify_a4_luoji import CASES as c_a4_cases

CASES = [
    c_wubuyushi, c_tianyi, c_lushen, c_yangren, c_wenchang,
    c_sanhe, c_liuhe, c_liuchong, c_liuhai, c_sanxing, c_po,
    c_jiesha_base, c_jiesha_table,
    c_zaisha_base, c_zaisha_table,
    c_suisha_base, c_suisha_dongtu, c_suisha_table,
    c_yuesha_base,
] + c_yima_cases + c_yaoan_cases + c_wufu_cases + c_fusheng_cases + c_shengqi_cases \
  + c_a1_cases + c_a2_cases + c_a3_cases + c_a4_cases


if __name__ == '__main__':
    sys.exit(run_cli(CASES))
