# -*- coding: utf-8 -*-
"""
打包手机一键部署包为 ZIP 文件
"""

import os
import zipfile

source_dir = os.path.dirname(os.path.abspath(__file__))
deploy_dir = os.path.join(source_dir, '手机一键部署')
zip_file = os.path.join(source_dir, '手机一键部署包.zip')

print("=" * 60)
print("=== 打包手机一键部署包 ===")
print("=" * 60)

# 打包时排除的目录/文件（防止备份、缓存、zip自身被打进包）
EXCLUDE_DIRS = {'__pycache__', '备份', 'backup', 'backups', 'build', 'dist',
                '.git', '.uploads', 'logs'}
EXCLUDE_EXTS = {'.pyc', '.pyo', '.zip'}

# 创建 ZIP 文件
with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(deploy_dir):
        # 原地修改 dirs，阻止 os.walk 下钻到备份/缓存等目录（避免把备份打进包）
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and '备份' not in d]
        for file in files:
            if os.path.splitext(file)[1].lower() in EXCLUDE_EXTS:
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, deploy_dir)
            zipf.write(file_path, arcname)
            print(f"✓ {arcname}")

print("\n" + "=" * 60)
print("=== 打包完成 ===")
print("=" * 60)

zip_size = os.path.getsize(zip_file)
print(f"\nZIP 文件：{zip_file}")
print(f"ZIP 大小：{zip_size / 1024:.2f} KB")
print(f"\n将此 ZIP 文件传输到手机，解压后即可运行！")
print("=" * 60)
