# -*- coding: utf-8 -*-
"""
整合脚本 - 将所有模块合并到单文件版本
运行此脚本将生成完整的单文件版本
"""
import os

# 要整合的模块列表（按依赖顺序）
MODULES = [
    ('tools', 'modules/工具函数.py'),
    ('sizhu', 'modules/四柱计算器.py'),
    ('huangdao', 'modules/黄道.py'),
    ('xishen', 'modules/喜用神计算器.py'),
    ('bazi', 'modules/八字排盘.py'),
    ('bazi_vis', 'modules/八字可视化模块.py'),
    ('shansha', 'modules/二十四山.py'),
    ('compass', 'modules/电子罗盘.py'),
    ('scorer', 'modules/评分器.py'),
    ('marriage_scorer', 'modules/婚嫁评分算法.py'),
    ('score_system', 'modules/日课评分系统.py'),
    ('shensha_base', 'modules/shensha/神煞基类.py'),
    ('marriage_shensha', 'modules/shensha/嫁娶神煞.py'),
    ('xiuzao_shensha', 'modules/shensha/修造神煞.py'),
    ('anyang_shensha', 'modules/shensha/安葬神煞.py'),
    ('kaiye_shensha', 'modules/shensha/开业神煞.py'),
    ('rules_base', 'modules/rules/规则基类.py'),
    ('marriage_rules', 'modules/rules/嫁娶规则.py'),
    ('xiuzao_rules', 'modules/rules/修造规则.py'),
    ('anyang_rules', 'modules/rules/安葬规则.py'),
]

def read_module(path):
    """读取模块内容"""
    full_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def main():
    print("=" * 60)
    print("开始整合模块到单文件版本")
    print("=" * 60)

    # 读取主程序
    main_file = '主程序.py'
    if not os.path.exists(main_file):
        print(f"错误: 找不到主程序文件 {main_file}")
        return

    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()

    print(f"主程序大小: {len(main_content)} 字符")

    # 读取各个模块
    integrated_code = []
    for name, path in MODULES:
        content = read_module(path)
        if content:
            print(f"[OK] {name}: {len(content)} 字符")
            integrated_code.append(f"\n# ==== 模块: {name} ====\n{content}")
        else:
            print(f"[SKIP] {name}: 文件不存在")

    print(f"\n成功读取 {len(integrated_code)} 个模块")

    # 生成整合后的文件
    output_file = '手机一键部署/单文件版/择日软件完整版.py'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(main_content)
        f.write('\n\n#' * 40 + '\n')
        f.write('# 以下是整合的模块代码\n')
        f.write('#' * 40 + '\n\n')
        f.write('\n\n'.join(integrated_code))

    print(f"\n整合完成! 输出文件: {output_file}")
    print(f"文件大小: {os.path.getsize(output_file)} 字节")

if __name__ == '__main__':
    main()
