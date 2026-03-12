#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业级正五行择日软件 - 完整单文件集成工具 v16

功能：
- 将所有模块合并为单个Python文件
- 处理模块间导入
- 保留必要的代码结构
- 确保语法正确
"""

import os
from pathlib import Path

# 模块列表（按依赖顺序）
MODULES = [
    '工具函数.py',
    '八字分析工具.py',
    '喜用神计算器.py',
    '四柱计算器.py',
    '黄道.py',
    '二十四山.py',
    '电子罗盘.py',
    '八字排盘.py',
    '八字排盘模块.py',
    '日课评分系统.py',
    '事主八字分析.py',
    '事主日课匹配评分.py',
    '评分器.py',
    'shensha/神煞基类.py',
    'shensha/通用神煞.py',
    'shensha/嫁娶神煞.py',
    'shensha/修造神煞.py',
    'shensha/开业神煞.py',
    'shensha/安葬神煞.py',
    'shensha/安床神煞.py',
    'shensha/出行神煞.py',
    'shensha/入宅神煞.py',
    'shensha/作灶神煞.py',
    'rules/规则基类.py',
    'rules/嫁娶规则.py',
    'rules/修造规则.py',
    'rules/开业规则.py',
    'rules/安葬规则.py',
    'rules/安床规则.py',
    'rules/出行规则.py',
    'rules/作灶规则.py',
]

MAIN_PROGRAM = '主程序.py'
OUTPUT_FILE = '择日软件_完整单文件版.py'

def read_file(file_path):
    """读取文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def clean_module(code, module_name):
    """清理模块代码"""
    lines = code.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 跳过sys.path操作
        if 'sys.path.insert' in line and ('project_root' in line or 'modules_dir' in line):
            i += 1
            continue
        
        # 跳过project_root定义
        if 'project_root = os.path.dirname' in line:
            i += 1
            continue
        
        # 跳过if project_root not in sys.path:
        if stripped == 'if project_root not in sys.path:':
            i += 2  # 跳过下一行
            continue
        
        # 跳过__package__检查
        if '__package__ is None' in line:
            # 跳过整个块
            indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines):
                current_line = lines[j].strip()
                current_indent = len(lines[j]) - len(current_line)
                if current_indent <= indent and current_line:
                    break
                j += 1
            i = j
            continue
        
        # 跳过模块级的__main__测试代码
        if stripped.startswith('if __name__ == '):
            # 跳过整个块
            indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines):
                current_line = lines[j]
                current_line_stripped = current_line.strip()
                current_indent = len(current_line) - len(current_line_stripped)
                if current_indent <= indent and current_line_stripped:
                    break
                j += 1
            i = j
            continue
        
        # 跳过模块间的导入语句
        skip_import = False
        if stripped.startswith('from '):
            # 检查是否是导入其他模块
            for mod in MODULES:
                mod_name = os.path.splitext(os.path.basename(mod))[0]
                if mod_name in stripped:
                    skip_import = True
                    break
            # 检查是否是导入shensha或rules模块
            if 'from .shensha' in stripped or 'from .rules' in stripped:
                skip_import = True
        elif stripped.startswith('import '):
            # 检查是否是导入其他模块
            for mod in MODULES:
                mod_name = os.path.splitext(os.path.basename(mod))[0]
                if mod_name in stripped:
                    skip_import = True
                    break
            # 检查是否是导入shensha或rules模块
            if 'import shensha' in stripped or 'import rules' in stripped:
                skip_import = True
        
        if skip_import:
            # 跳过整个导入语句（包括多行导入）
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line.endswith(')'):
                    i += 1
                    break
                i += 1
            continue
        
        # 处理try-except块中的相对导入
        if stripped == 'try:':
            # 检查try块是否包含相对导入、return语句或导入语句
            has_relative_import = False
            has_return = False
            has_import = False
            j = i + 1
            try_indent = len(line) - len(line.lstrip())
            while j < len(lines):
                current_line = lines[j].strip()
                current_indent = len(lines[j]) - len(current_line)
                if current_indent <= try_indent and current_line:
                    break
                if current_line.startswith('from .') or current_line.startswith('from modules.') or current_line.startswith('import modules.'):
                    has_relative_import = True
                    break
                if current_line.startswith('return '):
                    has_return = True
                    break
                if current_line.startswith('import ') or current_line.startswith('from '):
                    has_import = True
                j += 1
            
            if has_relative_import:
                # 找到对应的except
                except_line = None
                while j < len(lines):
                    if lines[j].strip().startswith('except') and lines[j].strip().endswith(':'):
                        except_line = j
                        break
                    j += 1
                
                if except_line:
                    # 找到except块的结束位置
                    k = except_line + 1
                    except_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
                    while k < len(lines):
                        current_line = lines[k].strip()
                        current_indent = len(lines[k]) - len(current_line)
                        if current_indent <= except_indent and current_line:
                            break
                        k += 1
                    
                    # 跳过整个try-except块
                    i = k
                    continue
            elif has_return:
                # 直接跳过try语句，保留return语句并调整缩进
                j = i + 1
                while j < len(lines):
                    current_line = lines[j]
                    current_stripped = current_line.strip()
                    current_indent = len(current_line) - len(current_stripped)
                    if current_indent <= try_indent and current_stripped:
                        break
                    # 调整缩进，将return语句的缩进减少到函数体级别
                    if current_stripped.startswith('return '):
                        # 计算函数体的缩进（比try语句少4个空格）
                        function_indent = try_indent - 4
                        # 重新生成return语句，使用函数体缩进
                        return_line = ' ' * function_indent + current_stripped
                        result.append(return_line)
                    else:
                        result.append(current_line)
                    j += 1
                i = j
                continue
            elif has_import:
                # 跳过整个try块，保留导入语句并调整缩进
                j = i + 1
                while j < len(lines):
                    current_line = lines[j]
                    current_stripped = current_line.strip()
                    current_indent = len(current_line) - len(current_stripped)
                    if current_indent <= try_indent and current_stripped:
                        break
                    # 调整缩进，将导入语句的缩进减少到文件级别
                    if current_stripped.startswith('import ') or current_stripped.startswith('from '):
                        # 使用0缩进（文件级别）
                        import_line = current_stripped
                        result.append(import_line)
                    elif current_stripped.startswith('HAS_') or 'logger.info' in current_stripped:
                        # 调整变量定义和日志语句的缩进
                        # 使用0缩进（文件级别）
                        statement_line = current_stripped
                        result.append(statement_line)
                    else:
                        result.append(current_line)
                    j += 1
                i = j
                continue
            else:
                # 保留整个try-except块
                result.append(line)
                i += 1
                # 处理try块的内容
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()
                    current_indent = len(current_line) - len(current_stripped)
                    # 检查是否是except语句
                    if current_stripped.startswith('except ') and current_stripped.endswith(':'):
                        break
                    # 只有当遇到缩进级别小于try_indent的非空行时才break
                    if current_indent < try_indent and current_stripped:
                        break
                    result.append(current_line)
                    i += 1
                # 处理except块
                if i < len(lines) and lines[i].strip().startswith('except') and lines[i].strip().endswith(':'):
                    result.append(lines[i])
                    i += 1
                    except_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                    while i < len(lines):
                        current_line = lines[i]
                        current_stripped = current_line.strip()
                        current_indent = len(current_line) - len(current_stripped)
                        # 检查是否是新的方法定义
                        if current_stripped.startswith('def '):
                            # 检查缩进级别是否等于except_indent
                            if current_indent == except_indent:
                                # 这是一个新的方法定义，跳出循环
                                break
                        # 只有当遇到缩进级别小于except_indent的非空行时才break
                        if current_indent < except_indent and current_stripped:
                            break
                        result.append(current_line)
                        i += 1
                    continue
        
        # 处理空的if语句
        if stripped.endswith(':') and ('if ' in stripped or 'elif ' in stripped):
            # 检查下一行是否是注释或直接是return语句
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # 检查下一行是否是return语句
                if next_line.startswith('return '):
                    # 添加缩进
                    indent = len(line) - len(line.lstrip())
                    # 重新生成return语句，使用正确的缩进
                    return_line = ' ' * (indent + 4) + next_line
                    result.append(line)
                    result.append(return_line)
                    i += 2  # 跳过if和return
                    continue
                # 检查下一行是否是注释
                elif next_line.startswith('#'):
                    # 检查下下一行是否是else:或return语句
                    if i + 2 < len(lines):
                        next_next_line = lines[i + 2].strip()
                        if next_next_line == 'else:' or next_next_line.startswith('return '):
                            # 添加pass语句
                            indent = len(line) - len(line.lstrip())
                            pass_line = ' ' * (indent + 4) + 'pass'
                            result.append(line)
                            result.append(lines[i + 1])  # 保留注释
                            result.append(pass_line)
                            i += 3  # 跳过if、注释和else/return
                            continue
        
        # 保留其他代码
        result.append(line)
        i += 1
    
    return '\n'.join(result)

def merge_all_modules():
    """合并所有模块"""
    project_root = Path(__file__).parent
    modules_dir = project_root / 'modules'
    
    print("=" * 80)
    print("专业级正五行择日软件 - 完整单文件集成工具 v16")
    print("=" * 80)
    print()
    
    # 读取并清理所有模块
    merged_code = []
    
    print("合并模块:")
    for module_path in MODULES:
        full_path = modules_dir / module_path
        if full_path.exists():
            code = read_file(full_path)
            cleaned_code = clean_module(code, module_path)
            merged_code.append(cleaned_code)
            print(f"  ✓ {os.path.basename(module_path)}")
        else:
            print(f"  ✗ {os.path.basename(module_path)} (文件不存在)")
    
    # 读取并清理主程序
    print()
    print("合并主程序:")
    main_path = project_root / MAIN_PROGRAM
    if main_path.exists():
        main_code = read_file(main_path)
        cleaned_main = clean_module(main_code, MAIN_PROGRAM)
        merged_code.append(cleaned_main)
        print("  ✓ 主程序")
    else:
        print("  ✗ 主程序 (文件不存在)")
    
    # 合并所有代码
    final_code = '\n\n'.join(merged_code)
    
    # 修复空的if语句、孤立的except语句和孤立的try语句
    lines = final_code.split('\n')
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检查是否是if语句，且下一行是注释，再下一行是else或return语句
        if stripped.endswith(':') and ('if ' in stripped or 'elif ' in stripped):
            # 检查下一行是否是return语句
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('return '):
                    # 添加缩进
                    indent = len(line) - len(line.lstrip())
                    # 重新生成return语句，使用正确的缩进
                    return_line = ' ' * (indent + 4) + next_line
                    fixed_lines.append(line)
                    fixed_lines.append(return_line)
                    i += 2  # 跳过if和return
                    continue
                # 检查下一行是否是注释
                elif next_line.startswith('#'):
                    # 检查下下一行是否是else:或return语句
                    if i + 2 < len(lines):
                        next_next_line = lines[i + 2].strip()
                        if next_next_line == 'else:' or next_next_line.startswith('return '):
                            # 添加pass语句
                            indent = len(line) - len(line.lstrip())
                            pass_line = ' ' * (indent + 4) + 'pass'
                            fixed_lines.append(line)
                            fixed_lines.append(lines[i + 1])  # 保留注释
                            fixed_lines.append(pass_line)
                            i += 3  # 跳过if、注释和else/return
                            continue
        
        # 检查是否是孤立的try语句
        if stripped == 'try:':
            # 向后查找对应的except或finally语句
            has_except_or_finally = False
            j = i + 1
            try_indent = len(line) - len(line.lstrip())
            while j < len(lines):
                current_line = lines[j]
                current_stripped = current_line.strip()
                current_indent = len(current_line) - len(current_stripped)
                if current_indent <= try_indent and current_stripped:
                    # 检查是否是except或finally
                    if current_stripped.startswith('except ') or current_stripped == 'finally:':
                        has_except_or_finally = True
                    break
                j += 1
            
            if not has_except_or_finally:
                # 直接移除try语句，保留块中的语句
                j = i + 1
                while j < len(lines):
                    current_line = lines[j]
                    current_stripped = current_line.strip()
                    current_indent = len(current_line) - len(current_stripped)
                    if current_indent <= try_indent and current_stripped:
                        break
                    # 调整缩进，将语句的缩进减少到函数体级别
                    if current_stripped and not current_stripped.startswith('#'):
                        # 计算函数体的缩进（比try语句少4个空格）
                        function_indent = try_indent - 4
                        # 重新生成语句，使用函数体缩进
                        statement_line = ' ' * function_indent + current_stripped
                        fixed_lines.append(statement_line)
                    else:
                        fixed_lines.append(current_line)
                    j += 1
                i = j
                continue
        
        # 检查是否是孤立的except语句
        if stripped.startswith('except ') and stripped.endswith(':'):
            # 向前查找对应的try语句
            has_try = False
            j = i - 1
            while j >= 0:
                prev_line = lines[j].strip()
                if prev_line == 'try:':
                    has_try = True
                    break
                elif prev_line and not prev_line.startswith('#'):
                    break
                j -= 1
            
            if not has_try:
                # 跳过这个孤立的except块
                indent = len(line) - len(line.lstrip())
                j = i + 1
                while j < len(lines):
                    current_indent = len(lines[j]) - len(lines[j].lstrip())
                    if current_indent <= indent and lines[j].strip():
                        break
                    j += 1
                i = j
                continue
        
        fixed_lines.append(line)
        i += 1
    
    final_code = '\n'.join(fixed_lines)
    
    # 写入输出文件
    output_path = project_root / OUTPUT_FILE
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_code)
    
    print()
    print("✓ 合并完成！")
    print(f"输出文件: {output_path}")
    print(f"文件大小: {round(os.path.getsize(output_path) / 1024 / 1024, 2)} MB")
    
    # 验证语法
    print()
    print("正在验证语法...")
    try:
        compile(final_code, OUTPUT_FILE, 'exec')
        print("✓ 语法验证通过！")
    except SyntaxError as e:
        print(f"✗ 语法错误:")
        print(f"  行号: {e.lineno}")
        print(f"  错误: {e.msg}")
        
        # 显示附近的代码
        lines = final_code.split('\n')
        start_line = max(0, e.lineno - 5)
        end_line = min(len(lines), e.lineno + 5)
        print()
        print("  附近代码:")
        for i in range(start_line, end_line):
            line_num = i + 1
            marker = " >>> " if line_num == e.lineno else "        "
            print(f"{marker}{line_num}: {lines[i]}")

if __name__ == "__main__":
    merge_all_modules()
