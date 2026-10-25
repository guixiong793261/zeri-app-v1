# -*- coding: utf-8 -*-
"""R1 影响面诊断：24 山基础名+兼向键的静态 chongshan 规则 vs check_chong_shan 实际触发
只读：不修改任何业务代码"""
import sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'd:\自编择日软件\专业级正五行择日软件')
sys.path.insert(0, str(ROOT))
from modules.二十四山择吉天机 import MOUNTAIN_DATA, check_chong_shan

ZHIS = '子丑寅卯辰巳午未申酉戌亥'
issues = []
for bn in list(MOUNTAIN_DATA.keys()):
    data = MOUNTAIN_DATA[bn]
    cs = data.get('avoid_info', {}).get('chongshan', '')
    if isinstance(cs, dict):
        names = list(cs.keys())
    elif isinstance(cs, str):
        names = [bn]
    else:
        names = []
    for nm in names:
        rule = cs.get(nm) if isinstance(cs, dict) else (cs if isinstance(cs, str) else '')
        triggers = [z for z in ZHIS if check_chong_shan(nm, z)]
        if rule and len(triggers) != 1 or (rule and triggers[0] != rule[1]):
            issues.append((nm, rule, triggers))
        print(f'{nm}: 静态={rule!r} 触发={triggers}')

print('\n=== 触发与静态规则不符的条目（回退映射叠加项） ===')
for nm, rule, trig in issues:
    print(f'  {nm}: 静态忌{rule[1]} 实际触发={trig}')
print(f'共 {len(issues)} 条')
