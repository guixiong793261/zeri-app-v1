[app]

# 应用标题
title = 改良五行择日

# 应用包名（请使用您自己的包名）
package.name = gaiang_wuxing_zheri

# 应用域名（请使用您自己的域名）
package.domain = org.gaiang

# 应用版本
version = 1.0.0

# 源代码目录
source.dir = .

# 需要排除的目录
source.include_exts = py,png,jpg,kv,atlas,json

# 主程序入口
source.include_patterns = 主程序_kivy版.py,modules/,data/

# Android最低支持版本
android.minapi = 21

# Android目标API版本
android.api = 33

# 支持的架构
android.archs = arm64-v8a, armeabi-v7a

# 全屏沉浸模式
android.fullscreen = 1

# 屏幕方向
orientation = portrait

# 依赖库
requirements = python3,kivy>=2.3.0,lunar-python>=1.0.0,loguru>=0.7.0

# 日志级别
log_level = 2

# 打包方式
p4a.bootstrap = sdl2

[buildozer]

# 日志等级
log_level = 2

# 显示构建输出
show_build_output = True
