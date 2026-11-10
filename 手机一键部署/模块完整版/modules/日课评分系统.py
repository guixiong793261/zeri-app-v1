# -*- coding: utf-8 -*-
"""
================================================================================
日课评分系统模块
================================================================================
专业级日课评分系统，支持多种输入方式和详细评分分析

使用方法:
    1. 作为主程序导入: from modules.日课评分系统 import DayScoreWindow
    2. 直接运行: python -m modules.日课评分系统
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, date
import json
import os
import re
import sys

# 处理导入
# 添加项目根目录到路径
project_root = (getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable))) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# 添加 modules 目录到路径
modules_dir = (getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable))) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)))
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

# 定义备用函数（签名必须与真实模块函数完全兼容，允许任何位置/关键字参数）
def _mock_calculate_sizhu(*args, **kwargs):
    return {'年柱': '甲子', '月柱': '甲子', '日柱': '甲子', '时柱': '甲子'}

def _mock_analyze_sizhu(*args, **kwargs):
    return {}

def _mock_calculate_score(*args, **kwargs):
    return {
        'score': 0,
        'level': '平',
        'yi_list': [],
        'ji_list': [],
        'shensha_list': [],
        'score_details': {
            '基础分': 100,
            '月令得分': 0,
            '月令详细': {
                '旺衰得分': 0,
                '支支关系得分': 0
            },
            '喜用神得分': 0,
            '黄道得分': 0,
            '总分': 0,
            '事主匹配': []
        },
        'wu_xing_result': {
            'details': {
                '地支关系': [],
                '吉神': [],
                '日主旺衰': '中和'
            }
        },
        'huangdao_info': {
            'da_huang_dao': {
                'name': '黄道吉日',
                'description': '适合办大事'
            },
            'xiao_huang_dao': {
                'name': '黄道吉日',
                'description': '适合办大事'
            }
        },
        'reason': '此日为黄道吉日，适合各项事务。'
    }

def _mock_calculate_xishen_yongshen(*args, **kwargs):
    return ('', '')

def _mock_get_shan_xiang_list(*args, **kwargs):
    """备用：兼容真实签名 use_24_shan 等关键字参数"""
    return []

def _mock_show_compass_dialog(*args, **kwargs):
    pass

def _mock_shan_xiang_to_shan(*args, **kwargs):
    """备用的山向转坐山函数（兼容真实签名）"""
    # 取第一个位置参数当作 shan_xiang，若没有则尝试关键字 shan_xiang
    shan_xiang = args[0] if args else kwargs.get('shan_xiang', '')
    if shan_xiang:
        return shan_xiang.split('山')[0] if '山' in shan_xiang else shan_xiang
    return ''

# 初始化所有导入的名称为备用值
calculate_sizhu = _mock_calculate_sizhu
analyze_sizhu = _mock_analyze_sizhu
calculate_score = _mock_calculate_score
calculate_xishen_yongshen = _mock_calculate_xishen_yongshen
get_shan_xiang_list = _mock_get_shan_xiang_list
show_compass_dialog = _mock_show_compass_dialog
shan_xiang_to_shan = _mock_shan_xiang_to_shan

# 添加日志记录器
import logging
logger = logging.getLogger(__name__)

# 模块级变量，存储真实的函数（初始为None，表示未加载）
_calculate_sizhu = None
_analyze_sizhu = None
_calculate_score = None
_calculate_xishen_yongshen = None
_get_shan_xiang_list = None
_show_compass_dialog = None
_shan_xiang_to_shan = None

def _load_real_functions():
    """尝试加载真实的模块函数，返回是否全部加载成功"""
    global _calculate_sizhu, _analyze_sizhu, _calculate_score
    global _calculate_xishen_yongshen, _get_shan_xiang_list
    global _show_compass_dialog, _shan_xiang_to_shan
    
    # 尝试策略1: 相对导入（作为模块导入时）
    try:
        from .四柱计算器 import calculate_sizhu, analyze_sizhu
        from .评分器 import calculate_score
        from .喜用神计算器 import calculate_xishen_yongshen
        from .二十四山 import get_shan_xiang_list, shan_xiang_to_shan
        from .电子罗盘 import show_compass_dialog
        _calculate_sizhu = calculate_sizhu
        _analyze_sizhu = analyze_sizhu
        _calculate_score = calculate_score
        _calculate_xishen_yongshen = calculate_xishen_yongshen
        _get_shan_xiang_list = get_shan_xiang_list
        _show_compass_dialog = show_compass_dialog
        _shan_xiang_to_shan = shan_xiang_to_shan
        return True
    except ImportError:
        pass
    
    # 尝试策略2: 绝对导入（运行时）
    try:
        from modules.四柱计算器 import calculate_sizhu, analyze_sizhu
        from modules.评分器 import calculate_score
        from modules.喜用神计算器 import calculate_xishen_yongshen
        from modules.二十四山 import get_shan_xiang_list, shan_xiang_to_shan
        from modules.电子罗盘 import show_compass_dialog
        _calculate_sizhu = calculate_sizhu
        _analyze_sizhu = analyze_sizhu
        _calculate_score = calculate_score
        _calculate_xishen_yongshen = calculate_xishen_yongshen
        _get_shan_xiang_list = get_shan_xiang_list
        _show_compass_dialog = show_compass_dialog
        _shan_xiang_to_shan = shan_xiang_to_shan
        return True
    except ImportError:
        pass
    
    # 尝试策略3: 直接导入
    try:
        from 四柱计算器 import calculate_sizhu, analyze_sizhu
        from 评分器 import calculate_score
        from 喜用神计算器 import calculate_xishen_yongshen
        from 二十四山 import get_shan_xiang_list, shan_xiang_to_shan
        from 电子罗盘 import show_compass_dialog
        _calculate_sizhu = calculate_sizhu
        _analyze_sizhu = analyze_sizhu
        _calculate_score = calculate_score
        _calculate_xishen_yongshen = calculate_xishen_yongshen
        _get_shan_xiang_list = get_shan_xiang_list
        _show_compass_dialog = show_compass_dialog
        _shan_xiang_to_shan = shan_xiang_to_shan
        return True
    except ImportError as e:
        logger.warning(f"所有导入策略均失败: {e}")
        return False

# 在模块加载时立即尝试导入真实函数
_import_success = _load_real_functions()
if _import_success:
    logger.info("日课评分系统: 成功加载核心模块")
else:
    logger.warning("日课评分系统: 核心模块加载失败，将使用备用函数")

def calculate_sizhu(*args, **kwargs):
    """计算四柱"""
    if _calculate_sizhu:
        return _calculate_sizhu(*args, **kwargs)
    return _mock_calculate_sizhu(*args, **kwargs)

def analyze_sizhu(*args, **kwargs):
    """分析四柱"""
    if _analyze_sizhu:
        return _analyze_sizhu(*args, **kwargs)
    return _mock_analyze_sizhu(*args, **kwargs)

def calculate_score(*args, **kwargs):
    """计算评分"""
    if _calculate_score:
        return _calculate_score(*args, **kwargs)
    return _mock_calculate_score(*args, **kwargs)

def calculate_xishen_yongshen(*args, **kwargs):
    """计算喜用神"""
    if _calculate_xishen_yongshen:
        return _calculate_xishen_yongshen(*args, **kwargs)
    return _mock_calculate_xishen_yongshen(*args, **kwargs)

def get_shan_xiang_list(*args, **kwargs):
    """获取山向列表（与二十四山模块签名完全一致，允许 use_24_shan 等关键字）"""
    if _get_shan_xiang_list:
        return _get_shan_xiang_list(*args, **kwargs)
    return _mock_get_shan_xiang_list(*args, **kwargs)

def show_compass_dialog(*args, **kwargs):
    """显示罗盘对话框"""
    if _show_compass_dialog:
        return _show_compass_dialog(*args, **kwargs)
    return _mock_show_compass_dialog(*args, **kwargs)

def shan_xiang_to_shan(*args, **kwargs):
    """山向转坐山（与真实模块签名一致，允许位置参数 shan_xiang 或关键字参数）"""
    if _shan_xiang_to_shan:
        return _shan_xiang_to_shan(*args, **kwargs)
    return _mock_shan_xiang_to_shan(*args, **kwargs)

class DayScoreWindow:
    """日课评分系统主窗口"""
    
    def __init__(self, master=None, mode='full'):
        """初始化

        Args:
            master: 父窗口，None 表示独立启动（Tk根窗口），否则作为 Toplevel 子窗口
            mode: 显示模式
                - 'full'     完整版：标题+事主信息+特殊选项+输入区+按钮+列表+结果（独立运行默认）
                - 'embedded' 精简版（主程序导入择日结果用）：
                             仅显示 日课输入区 + 按钮区 + 日课列表 + 评分结果，
                             不显示 标题区、事主信息区、特殊选项区
        """
        # 检查核心模块是否加载成功
        if not _import_success:
            logger.warning("核心模块未加载，评分结果可能不准确")

        # 显示模式校验
        if mode not in ('full', 'embedded'):
            mode = 'full'
        self.mode = mode

        self._is_standalone = (master is None)

        if master is None:
            self.window = tk.Tk()
            if self.mode == 'embedded':
                self.window.title("日课评分（导入结果）")
            else:
                self.window.title("专业级日课评分系统")
        else:
            self.window = tk.Toplevel(master)
            if self.mode == 'embedded':
                self.window.title("日课评分（导入结果）")
            else:
                self.window.title("专业级日课评分系统")
            # 强制设置Toplevel窗口的背景色和文本颜色
            self.window.configure(bg='white')
        
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置为屏幕的90%大小，与主程序一致
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        try:
            self.window.state('zoomed')  # 窗口最大化，与主程序一致
        except Exception:
            # 安卓 Tk 不支持 zoomed，铺满屏幕（与主程序 fallback 一致）
            self.window.geometry("%dx%d+0+0" % (screen_width, screen_height))
        
        # 确保窗口显示
        self.window.deiconify()
        
        # 数据存储
        self.date_list = []
        self.scoring_results = []
        self.owners_info = []
        self._owner_entries_list = []  # 存储所有事主的输入框，用于键盘导航
        
        # 创建界面
        self.create_widgets()
    
    def import_results(self, results, event_type, owners_data):
        """从主程序导入择日结果

        Args:
            results: 主程序的择日结果列表
            event_type: 事项类型
            owners_data: 事主数据列表
        """
        try:
            # 设置事项类型
            self.event_var.set(event_type)
            # 清空并更新事主信息框架
            self.update_owners_frame()
            # 更新特殊选项
            self.update_special_options()

            # 强制刷新界面（Toplevel窗口需要更强的刷新）
            self.window.update_idletasks()
            self.window.update()

            # ——————————————————————————————————————
            # embedded 精简模式：不显示 事主信息区 / 特殊选项区
            # ——————————————————————————————————————
            if self.mode != 'embedded':
                # 重新打包框架以确保布局更新
                self.owners_frame.pack_forget()
                self.owners_frame.pack(fill=tk.X, pady=6, padx=20)
                self.special_frame.pack_forget()
                self.special_frame.pack(fill=tk.X, pady=3)
            else:
                # embedded 下保持隐藏：强制 pack_forget，防止 update_owners_frame /
                # update_special_options 的某些逻辑误把它们显示出来
                try:
                    self.owners_frame.pack_forget()
                except Exception:
                    pass
                try:
                    self.special_frame.pack_forget()
                except Exception:
                    pass

            # 再次强制刷新，确保Toplevel窗口完全更新
            self.window.update_idletasks()
            self.window.update()

            # 如果是Toplevel窗口，确保窗口可见并置顶
            if isinstance(self.window, tk.Toplevel):
                self.window.lift()
                self.window.focus_force()
                self.window.deiconify()
                self.window.update_idletasks()
                self.window.update()
            
            # 填充事主信息
            for i, owner_data in enumerate(owners_data):
                if i < len(self.owners_info):
                    # 填充公历日期
                    self.owners_info[i]['solar_year'].set(str(owner_data.get('year', '')))
                    self.owners_info[i]['solar_month'].set(str(owner_data.get('month', '')))
                    self.owners_info[i]['solar_day'].set(str(owner_data.get('day', '')))
                    self.owners_info[i]['hour'].set(str(owner_data.get('hour', 12)))
                    self.owners_info[i]['minute'].set(str(owner_data.get('minute', 0)))
                    # 事主经度（真太阳时）：本窗口无经度输入框，经度仅随 owners_data 管道透传，
                    # 以普通键值挂在 owners_info 上（无 StringVar）；None=120°E 北京时间基准，行为与旧版一致
                    self.owners_info[i]['longitude'] = owner_data.get('longitude')
                    
                    # 获取事主名称（从name变量中获取字符串值）
                    owner_name = self.owners_info[i]['name']
                    if hasattr(owner_name, 'get'):
                        owner_name = owner_name.get()
                    
                    # 自动计算四柱
                    self.calculate_owner_sizhu(
                        self.owners_info[i]['solar_year'],
                        self.owners_info[i]['solar_month'],
                        self.owners_info[i]['solar_day'],
                        self.owners_info[i]['lunar_year'],
                        self.owners_info[i]['lunar_month'],
                        self.owners_info[i]['lunar_day'],
                        self.owners_info[i]['leap'],
                        self.owners_info[i]['hour'],
                        self.owners_info[i]['minute'],
                        owner_name,  # 传递字符串而不是StringVar
                        self.owners_info[i]['sizhu_var'],
                        self.owners_info[i]['xishen_var'],
                        self.owners_info[i]['yongshen_var'],
                        self.owners_info[i].get('fuzi_var'),
                        self.owners_info[i].get('date_type_var'),
                        self.owners_info[i].get('gender_var'),
                        longitude=self.owners_info[i].get('longitude')
                    )
            
            # 提取事主信息（从界面上已填充的数据中获取）
            owners_detail = []
            for info in self.owners_info:
                try:
                    # 修正：使用正确的字段名称
                    year_val = info['solar_year'].get() if hasattr(info['solar_year'], 'get') else ''
                    month_val = info['solar_month'].get() if hasattr(info['solar_month'], 'get') else ''
                    day_val = info['solar_day'].get() if hasattr(info['solar_day'], 'get') else ''
                    hour_val = info['hour'].get() if hasattr(info['hour'], 'get') else '12'
                    minute_val = info['minute'].get() if hasattr(info['minute'], 'get') else '0'
                    
                    if not (year_val and month_val and day_val):
                        continue
                    
                    year = int(year_val)
                    month = int(month_val)
                    day = int(day_val)
                    hour = int(hour_val)
                    minute = int(minute_val)
                    
                    name = info['name'].get() if hasattr(info['name'], 'get') else info.get('name', '')
                    sizhu_str = info['sizhu_var'].get() if hasattr(info.get('sizhu_var'), 'get') else ''
                    
                    owner_detail = {
                        'name': name,
                        'gender': info['gender_var'].get() if hasattr(info.get('gender_var'), 'get') else info.get('gender', ''),
                        'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                        'sizhu': sizhu_str,
                        'xishen': info['xishen_var'].get() if hasattr(info.get('xishen_var'), 'get') else '',
                        'yongshen': info['yongshen_var'].get() if hasattr(info.get('yongshen_var'), 'get') else '',
                        'fu_xing': '',
                        'zi_xing': ''
                    }
                    
                    if event_type == "嫁娶" and info.get('fuzi_var'):
                        fuzi_str = info['fuzi_var'].get()
                        if '夫星:' in fuzi_str:
                            parts = fuzi_str.split(', ')
                            owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                            if len(parts) > 1:
                                owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                    
                    owners_detail.append(owner_detail)
                except Exception as e:
                    continue
            
            # 导入择日结果到列表
            for result in results:
                date_str = result.get('date', '')
                if date_str and date_str not in self.date_list:
                    self.date_list.append(date_str)
                    
                    # 准备显示数据
                    score = result.get('score', 0)
                    level = result.get('level', '未知')
                    sizhu = result.get('sizhu', {})
                    
                    # 处理sizhu可能是字符串或字典的情况
                    if isinstance(sizhu, str):
                        sizhu_str = sizhu
                        # 尝试从字符串解析四柱
                        sizhu_parts = sizhu_str.split()
                        if len(sizhu_parts) == 4:
                            sizhu_dict = {
                                '年柱': sizhu_parts[0],
                                '月柱': sizhu_parts[1],
                                '日柱': sizhu_parts[2],
                                '时柱': sizhu_parts[3]
                            }
                        else:
                            sizhu_dict = {}
                    else:
                        sizhu_dict = sizhu
                        sizhu_str = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
                    
                    # 从detail字段中获取详细信息
                    detail = result.get('detail', {})
                    
                    # 获取详细得分信息
                    score_details = result.get('score_details', detail.get('score_details', {}))
                    wuxing_score = score_details.get('五行评分', 100)
                    yueling_score = score_details.get('月令得分', 0)
                    xishen_score = score_details.get('喜用神得分', 0)
                    huangdao_score = score_details.get('黄道得分', 0)
                    
                    # 获取地支关系信息（从wu_xing_result中获取详细地支关系）
                    wu_xing_result = result.get('wu_xing_result', detail.get('wu_xing_result', {}))
                    wu_xing_details = wu_xing_result.get('details', {})
                    
                    # 构建地支关系文本（显示具体的三合、六合等）
                    dizhi_relations = wu_xing_details.get('地支关系', [])
                    if dizhi_relations:
                        # 提取地支关系的简短描述
                        dizhi_text_list = []
                        for relation in dizhi_relations:
                            # 提取关键信息，如"三合火局"、"六合"等
                            if '三合' in relation:
                                # 提取"三合X局"
                                import re
                                match = re.search(r'三合(.)局', relation)
                                if match:
                                    dizhi_text_list.append(f"三合{match.group(1)}局")
                                else:
                                    dizhi_text_list.append('三合')
                            elif '六合' in relation:
                                dizhi_text_list.append('六合')
                            elif '六冲' in relation:
                                dizhi_text_list.append('六冲')
                            elif '六害' in relation:
                                dizhi_text_list.append('六害')
                            elif '三刑' in relation:
                                dizhi_text_list.append('三刑')
                            elif '相破' in relation:
                                dizhi_text_list.append('相破')
                            else:
                                # 其他关系，取前10个字符
                                dizhi_text_list.append(relation[:10])
                        dizhi_text = ', '.join(dizhi_text_list[:2])  # 最多显示2个关系
                    else:
                        dizhi_text = '-'
                    
                    # 获取吉神信息（从wu_xing_details中获取详细吉神）
                    jishen_list = wu_xing_details.get('吉神', [])
                    if jishen_list:
                        # 提取吉神的简短描述
                        jishen_text_list = []
                        for jishen in jishen_list:
                            # 提取关键信息，如"天德贵人"、"禄神"等
                            if '天德贵人' in jishen:
                                jishen_text_list.append('天德贵人')
                            elif '月德贵人' in jishen:
                                jishen_text_list.append('月德贵人')
                            elif '天乙贵人' in jishen:
                                jishen_text_list.append('天乙贵人')
                            elif '文昌贵人' in jishen:
                                jishen_text_list.append('文昌贵人')
                            elif '禄神' in jishen:
                                jishen_text_list.append('禄神')
                            elif '福星' in jishen:
                                jishen_text_list.append('福星')
                            else:
                                # 其他吉神，取前6个字符
                                jishen_text_list.append(jishen[:6])
                        jishen_text = ', '.join(jishen_text_list[:2])  # 最多显示2个吉神
                    else:
                        # 如果没有详细吉神，使用yi_list
                        yi_list = result.get('yi_list', detail.get('yi_list', []))
                        jishen_text = ', '.join(yi_list[:2]) if yi_list else '-'
                    
                    # 添加到Treeview
                    self.date_treeview.insert('', tk.END, values=(date_str, score, level, sizhu_str, wuxing_score, yueling_score, xishen_score, huangdao_score, dizhi_text, jishen_text))
                    
                    # 如果结果包含评分信息，也添加到评分结果中
                    if 'score' in result and 'level' in result:
                        # 从detail字段中获取详细信息（detail保存了完整的calculate_score结果）
                        detail = result.get('detail', {})
                        
                        # 保留原始分数和详细评分信息（来自条件择日，这是标准分数）
                        score_details = detail.get('score_details', result.get('score_details', {}))
                        original_score = score  # 使用条件择日的原始分数（标准分数）
                        original_level = level  # 使用条件择日的原始等级
                        
                        score_result = {
                            'date': date_str,
                            'score': original_score,  # 标准分数
                            'level': original_level,  # 标准等级
                            'reason': detail.get('reason', result.get('reason', '')),
                            'sizhu': sizhu_dict,
                            'event_type': event_type,
                            'owners_detail': owners_detail,
                            'huangdao_info': detail.get('huangdao_info', result.get('huangdao_info', {})),
                            'wu_xing_result': detail.get('wu_xing_result', result.get('wu_xing_result', {})),
                            'yi_list': detail.get('yi_list', result.get('yi_list', [])),
                            'ji_list': detail.get('ji_list', result.get('ji_list', [])),
                            'shensha_list': detail.get('shensha_list', result.get('shensha_list', [])),
                            'score_details': score_details,
                            'wuxing_score': result.get('wuxing_score', score_details.get('五行评分', 100)),
                            'yueling_score': result.get('yueling_score', score_details.get('月令得分', 0)),
                            'xishen_score': result.get('xishen_score', score_details.get('喜用神得分', 0)),
                            'huangdao_score': result.get('huangdao_score', score_details.get('黄道得分', 0)),
                            'marriage_details': detail.get('marriage_details', []),  # 婚嫁评分详情
                            'original_result': result,  # 保存原始结果引用
                            'is_imported': True  # 标记为导入结果
                        }
                        self.scoring_results.append(score_result)
            
            # 只有在有结果时才显示成功消息
            if results:
                messagebox.showinfo("成功", f"成功导入 {len(results)} 个择日结果到评分系统")
        except Exception as e:
            messagebox.showerror("错误", f"导入择日结果时出错: {str(e)}")
    
    def run(self):
        """运行日课评分系统"""
        # 确保窗口显示在最前面
        self.window.lift()
        self.window.focus_force()
        
        # 只有在没有调用过import_results时，才初始化默认的事主信息
        # 通过检查owners_info是否为空来判断是否已经初始化过
        if not self.owners_info:
            self.update_owners_frame()
            self.update_special_options()
        
        # 如果是主窗口（Tk），使用mainloop
        # 如果是子窗口（Toplevel），使用wait_window等待窗口关闭
        if isinstance(self.window, tk.Tk):
            self.window.mainloop()
        else:
            # 对于Toplevel窗口，确保它可见并等待用户交互
            self.window.transient(self.window.master)
            self.window.grab_set()
            self.window.wait_window()
    
    def configure_styles(self):
        """配置界面样式，与主程序一致"""
        style = ttk.Style()
        
        # 主题设置
        style.theme_use('clam')
        
        # 主框架样式
        style.configure('MainFrame.TFrame', background='#ffffff')
        
        # 标题框架样式
        style.configure('TitleFrame.TFrame', background='#007bff')
        
        # 标题样式
        style.configure('Title.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 28, 'bold'))
        
        # 副标题样式
        style.configure('Subtitle.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 14))
        
        # 卡片样式
        style.configure('Card.TLabelframe', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 12, 'bold'),
                       borderwidth=2,
                       relief='groove')
        
        # 表单框架样式
        style.configure('Form.TFrame', background='#ffffff')
        
        # 标签样式
        style.configure('Label.TLabel', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 12, 'bold'))
        
        # 输入框样式
        style.configure('Entry.TEntry', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 12),
                       borderwidth=2,
                       relief='solid')
        
        # 下拉框样式
        style.configure('Combobox.TCombobox', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 12),
                       borderwidth=2,
                       relief='solid')
        
        # 按钮框架样式
        style.configure('ButtonFrame.TFrame', background='#ffffff')
        
        # 主按钮样式
        style.configure('Primary.TButton', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 11, 'bold'),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton', 
                  background=[('active', '#0069d9')])
        
        # 次要按钮样式 - 使用与主按钮相同的蓝色系
        style.configure('Secondary.TButton', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 11, 'bold'),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                  background=[('active', '#0069d9')])
        
        # 信息按钮样式
        style.configure('Info.TButton', 
                       background='#17a2b8',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Info.TButton', 
                  background=[('active', '#138496')])
        
        # 危险按钮样式
        style.configure('Danger.TButton', 
                       background='#dc3545',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Danger.TButton', 
                  background=[('active', '#c82333')])
        
        # 内容框架样式
        style.configure('ContentFrame.TFrame', background='#ffffff')
        
        # 树形视图样式
        style.configure('Treeview.Treeview', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 10),
                       rowheight=25,
                       fieldbackground='#ffffff',
                       borderwidth=1,
                       relief='solid')
        
        # 树形视图标题样式
        style.configure('Treeview.Heading', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 10, 'bold'),
                       padding=(10, 5))
        
        # 树形视图悬停样式
        style.map('Treeview.Treeview', 
                  background=[('selected', '#cce7ff'), ('!selected', '#ffffff')],
                  foreground=[('selected', '#007bff'), ('!selected', '#333333')])
        
        # 滚动条样式
        style.configure('Scrollbar.Vertical.TScrollbar', 
                       background='#ffffff',
                       troughcolor='#e0e0e0',
                       borderwidth=0)
    
    def create_widgets(self):
        """创建界面组件（双版本：完整版 / 主程序导入精简版）"""
        # 配置样式
        self.configure_styles()

        # 创建主滚动区域 - 添加水平和垂直滚动条
        main_frame_container = ttk.Frame(self.window)
        main_frame_container.pack(fill=tk.BOTH, expand=True)

        main_canvas = tk.Canvas(main_frame_container, bg="#ffffff")
        v_scrollbar = ttk.Scrollbar(main_frame_container, orient="vertical", command=main_canvas.yview)
        h_scrollbar = ttk.Scrollbar(main_frame_container, orient="horizontal", command=main_canvas.xview)

        self.main_frame = ttk.Frame(main_canvas, padding="20", style="MainFrame.TFrame")

        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.window.winfo_screenwidth()-50)
        main_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 使用网格布局
        main_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 配置网格权重
        main_frame_container.grid_rowconfigure(0, weight=1)
        main_frame_container.grid_columnconfigure(0, weight=1)

        # 绑定鼠标滚轮（垂直滚动）
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # 绑定Shift+鼠标滚轮（水平滚动）
        main_canvas.bind_all("<Shift-MouseWheel>", lambda e: main_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))

        # 提前定义event_var变量
        self.event_var = tk.StringVar(value="嫁娶")

        # ——————————————————————————————————————————
        # 无论哪个模式，都先创建 owners_frame / special_frame 作为占位容器
        # （因为 import_results() / update_owners_frame() / update_special_options()
        #    都假设它们存在，否则会 AttributeError）
        # embedded 模式下这两个容器"只创建不显示"
        # ——————————————————————————————————————————
        self.owners_frame = ttk.LabelFrame(self.main_frame, text="事主信息", padding="20", style="Card.TLabelframe")
        self.special_frame = ttk.Frame(self.main_frame)  # placeholder

        # =====================================================
        # 【完整版 full】：标题 + 事主信息 + 特殊选项 + 输入 + 按钮 + 列表 + 结果
        # =====================================================
        # 注意：字符串比较必须严格使用 ASCII 单引号，不允许任何不可见字符或全角引号
        if self.mode == 'full':
            # 标题区域
            title_frame = ttk.Frame(self.main_frame, style="TitleFrame.TFrame")
            title_frame.pack(fill=tk.X, pady=8, padx=20)

            title_label = ttk.Label(title_frame, text="专业级日课评分系统",
                                   font=("微软雅黑", 18, "bold"), style="Title.TLabel")
            title_label.pack(pady=4)

            subtitle_label = ttk.Label(title_frame, text="精准评分，详细分析",
                                      font=("微软雅黑", 9), style="Subtitle.TLabel")
            subtitle_label.pack()

            # 事主信息区域（放在最上方）
            self.owners_frame.pack(fill=tk.X, pady=6, padx=20)

            # 创建左右分栏布局
            content_frame = ttk.Frame(self.main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

            # 使用网格布局，设置左右分栏的宽度比例
            content_frame.columnconfigure(0, weight=1, minsize=500)  # 左侧占1份
            content_frame.columnconfigure(1, weight=1, minsize=500)  # 右侧占1份
            content_frame.rowconfigure(0, weight=1)

            # 左侧内容（输入区域和按钮）
            left_frame = ttk.Frame(content_frame)
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

            # 右侧内容（留空，用于平衡布局）
            right_frame = ttk.Frame(content_frame)
            right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

            # 输入区域
            input_frame = ttk.LabelFrame(left_frame, text="日课输入", padding="8", style="Card.TLabelframe")
            input_frame.pack(fill=tk.X, pady=6)

            # 事项类型选择
            event_frame = ttk.Frame(input_frame)
            event_frame.pack(fill=tk.X, pady=5)

            ttk.Label(event_frame, text="事项类型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            events = ["嫁娶", "修造", "动土", "入宅", "开业", "出行", "安床", "作灶", "安葬"]
            event_combo = ttk.Combobox(event_frame, textvariable=self.event_var,
                                       values=events, state="readonly", width=15, font=("微软雅黑", 10))
            event_combo.pack(side=tk.LEFT, padx=5)
            self.event_combo = event_combo  # 保存引用便于 embedded 模式控制状态
            # 绑定事件，使用更可靠的方式
            event_combo.bind("<<ComboboxSelected>>", self.on_event_type_changed)

            # 特殊选项框架（用于修造等需要额外选项的事项）
            # 完整版：special_frame 放到 input_frame 里
            self.special_frame = ttk.Frame(input_frame)
            # —— 显示契约：只有 修造/动土/入宅 事项才显示 special_frame（含山向/罗盘/宅型）
            #    嫁娶/安葬/作灶等其他事项 → 隐藏，保持输入区紧凑
            initial_event_type = self.event_var.get()
            if initial_event_type in ("修造", "动土", "入宅"):
                self.special_frame.pack(fill=tk.X, pady=3)

            # 独立启动时主动创建事主输入框（master为None表示独立窗口）
            # 作为主程序子窗口时，由import_results填充
            if self._is_standalone:
                self._is_standalone = True
                self.update_owners_frame()
                self.update_special_options()
                # 独立启动第一次初始化后也刷新一次滚动区
                self.window.update_idletasks()
                self.window.update()
                try:
                    self.main_frame.event_generate("<Configure>")
                except Exception:
                    pass
            else:
                self._is_standalone = False

            # 初始化特殊选项（独立启动时已在上面调用过，这里确保其他情况也有默认值）
            if not self._is_standalone:
                self.update_special_options()

            # 输入方式选择
            input_mode_frame = ttk.Frame(input_frame)
            input_mode_frame.pack(fill=tk.X, pady=5)

            ttk.Label(input_mode_frame, text="输入方式:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            self.input_mode = tk.StringVar(value="date")
            ttk.Radiobutton(input_mode_frame, text="按日期", variable=self.input_mode,
                           value="date", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(input_mode_frame, text="按四柱", variable=self.input_mode,
                           value="sizhu", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)

            # 日期输入框
            self.date_frame = ttk.Frame(input_frame)
            self.date_frame.pack(fill=tk.X, pady=5)

            ttk.Label(self.date_frame, text="日期 (YYYY-MM-DD):", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            self.date_entry = ttk.Entry(self.date_frame, width=12, font=("微软雅黑", 10))
            self.date_entry.pack(side=tk.LEFT, padx=5)
            self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

            # 时间输入
            ttk.Label(self.date_frame, text="时间 (HH:MM):", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            self.time_entry = ttk.Entry(self.date_frame, width=6, font=("微软雅黑", 10))
            self.time_entry.pack(side=tk.LEFT, padx=5)
            self.time_entry.insert(0, "12:00")

            # 为日期和时间输入框绑定键盘导航
            self._bind_entry_navigation([self.date_entry, self.time_entry])

            # 四柱输入框
            self.sizhu_frame = ttk.Frame(input_frame)
            # 默认隐藏

            ttk.Label(self.sizhu_frame, text="年柱:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
            self.sizhu_entries = []
            for i, label in enumerate(["年柱", "月柱", "日柱", "时柱"]):
                entry = ttk.Entry(self.sizhu_frame, width=10, font=("微软雅黑", 12))
                entry.pack(side=tk.LEFT, padx=5)
                self.sizhu_entries.append(entry)

            # 为四柱输入框绑定键盘导航
            self._bind_entry_navigation(self.sizhu_entries)

            # 按钮区域 - 使用两行布局，统一颜色
            button_frame = ttk.Frame(left_frame, style="ButtonFrame.TFrame")
            button_frame.pack(fill=tk.X, pady=8, padx=20)

            # 第一行按钮
            button_row1 = ttk.Frame(button_frame, style="ButtonFrame.TFrame")
            button_row1.pack(fill=tk.X, pady=3)

            ttk.Button(button_row1, text="添加日课", command=self.add_date, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="添加四柱", command=self.add_sizhu, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="日课评分", command=self.start_scoring, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="对比分析", command=self.compare_analysis, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="清空列表", command=self.clear_dates, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)

            # 第二行按钮
            button_row2 = ttk.Frame(button_frame, style="ButtonFrame.TFrame")
            button_row2.pack(fill=tk.X, pady=3)

            ttk.Button(button_row2, text="保存分析", command=self.save_single_analysis, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row2, text="导出报告", command=self.export_report, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row2, text="导入文件", command=self.import_file, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row2, text="帮助", command=self.show_help, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)

        # =====================================================
        # 【精简版 embedded】：主程序导入择日结果场景
        #   仅显示：日课输入区 + 按钮区 + 日课列表 + 评分结果
        #   不显示：标题区、事主信息区、特殊选项区、左右分栏
        # =====================================================
        else:  # embedded
            # 输入区域（直接堆叠在主框架上，紧凑排版，去掉左右分栏）
            input_frame = ttk.LabelFrame(self.main_frame, text="日课输入", padding="8", style="Card.TLabelframe")
            input_frame.pack(fill=tk.X, pady=6, padx=20)

            # 事项类型选择（embedded 下锁定，不允许用户修改——主程序已传入）
            event_frame = ttk.Frame(input_frame)
            event_frame.pack(fill=tk.X, pady=5)

            ttk.Label(event_frame, text="事项类型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            events = ["嫁娶", "修造", "动土", "入宅", "开业", "出行", "安床", "作灶", "安葬"]
            event_combo = ttk.Combobox(event_frame, textvariable=self.event_var,
                                       values=events, state="disabled", width=15, font=("微软雅黑", 10))
            event_combo.pack(side=tk.LEFT, padx=5)
            self.event_combo = event_combo
            # 注意：embedded 下事项类型由主程序 event_var.set() 锁定，不需要 ComboboxSelected 回调

            # 特殊选项（embedded 下不显示，但要保持 self.special_frame 对象存在）
            # 这里重新绑定到 input_frame 内部（但不 pack），供后续 update_special_options 填充而不出错
            self.special_frame = ttk.Frame(input_frame)
            # （不pack = 不显示）

            # 独立/子窗口标记：embedded 模式下始终不创建事主输入 UI
            self._is_standalone = False
            # 初始化事主数据结构的空壳（self.owners_info / self._owner_entries_list），
            # 由 import_results 填充，不需要显示
            self.owners_info = []
            self._owner_entries_list = []

            # 输入方式选择
            input_mode_frame = ttk.Frame(input_frame)
            input_mode_frame.pack(fill=tk.X, pady=5)

            ttk.Label(input_mode_frame, text="输入方式:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            self.input_mode = tk.StringVar(value="date")
            ttk.Radiobutton(input_mode_frame, text="按日期", variable=self.input_mode,
                           value="date", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(input_mode_frame, text="按四柱", variable=self.input_mode,
                           value="sizhu", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)

            # 日期输入框
            self.date_frame = ttk.Frame(input_frame)
            self.date_frame.pack(fill=tk.X, pady=5)

            ttk.Label(self.date_frame, text="日期 (YYYY-MM-DD):", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            self.date_entry = ttk.Entry(self.date_frame, width=12, font=("微软雅黑", 10))
            self.date_entry.pack(side=tk.LEFT, padx=5)
            self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

            # 时间输入
            ttk.Label(self.date_frame, text="时间 (HH:MM):", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
            self.time_entry = ttk.Entry(self.date_frame, width=6, font=("微软雅黑", 10))
            self.time_entry.pack(side=tk.LEFT, padx=5)
            self.time_entry.insert(0, "12:00")

            # 为日期和时间输入框绑定键盘导航
            self._bind_entry_navigation([self.date_entry, self.time_entry])

            # 四柱输入框
            self.sizhu_frame = ttk.Frame(input_frame)
            # 默认隐藏

            ttk.Label(self.sizhu_frame, text="年柱:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
            self.sizhu_entries = []
            for i, label in enumerate(["年柱", "月柱", "日柱", "时柱"]):
                entry = ttk.Entry(self.sizhu_frame, width=10, font=("微软雅黑", 12))
                entry.pack(side=tk.LEFT, padx=5)
                self.sizhu_entries.append(entry)

            # 为四柱输入框绑定键盘导航
            self._bind_entry_navigation(self.sizhu_entries)

            # 按钮区域（两行保持不变，但去掉右侧留白——直接放在 input_frame 后面的独立框架）
            button_frame = ttk.Frame(self.main_frame, style="ButtonFrame.TFrame")
            button_frame.pack(fill=tk.X, pady=8, padx=20)

            # 第一行按钮
            button_row1 = ttk.Frame(button_frame, style="ButtonFrame.TFrame")
            button_row1.pack(fill=tk.X, pady=3)

            ttk.Button(button_row1, text="添加日课", command=self.add_date, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="添加四柱", command=self.add_sizhu, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="日课评分", command=self.start_scoring, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="对比分析", command=self.compare_analysis, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row1, text="清空列表", command=self.clear_dates, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)

            # 第二行按钮
            button_row2 = ttk.Frame(button_frame, style="ButtonFrame.TFrame")
            button_row2.pack(fill=tk.X, pady=3)

            ttk.Button(button_row2, text="保存分析", command=self.save_single_analysis, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row2, text="导出报告", command=self.export_report, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row2, text="导入文件", command=self.import_file, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(button_row2, text="帮助", command=self.show_help, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)

        # ——————————————————————————————————————————
        # 【公共区】日课列表 + 评分结果：两个模式都完全一致
        # ——————————————————————————————————————————
        # 日课列表
        list_frame = ttk.LabelFrame(self.main_frame, text="日课列表", padding="20", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

        # 创建Treeview控件替代Listbox，显示更多信息
        columns = ('date', 'score', 'level', 'sizhu', 'wuxing', 'yueling', 'xishen', 'huangdao', 'dizhi', 'jishen')
        self.date_treeview = ttk.Treeview(list_frame, columns=columns, show='headings')

        # 设置列标题
        self.date_treeview.heading('date', text='日期/四柱')
        self.date_treeview.heading('score', text='评分')
        self.date_treeview.heading('level', text='等级')
        self.date_treeview.heading('sizhu', text='四柱')
        self.date_treeview.heading('wuxing', text='五行得分')
        self.date_treeview.heading('yueling', text='月令得分')
        self.date_treeview.heading('xishen', text='喜用神得分')
        self.date_treeview.heading('huangdao', text='黄道得分')
        self.date_treeview.heading('dizhi', text='地支关系')
        self.date_treeview.heading('jishen', text='吉神信息')

        # 设置列宽 - 缩小列宽以适应手机屏幕
        self.date_treeview.column('date', width=90)
        self.date_treeview.column('score', width=45, anchor='center')
        self.date_treeview.column('level', width=45, anchor='center')
        self.date_treeview.column('sizhu', width=90)
        self.date_treeview.column('wuxing', width=50, anchor='center')
        self.date_treeview.column('yueling', width=50, anchor='center')
        self.date_treeview.column('xishen', width=55, anchor='center')
        self.date_treeview.column('huangdao', width=50, anchor='center')
        self.date_treeview.column('dizhi', width=80)
        self.date_treeview.column('jishen', width=90)

        # 添加滚动条 - 同时添加垂直和水平滚动条
        tree_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                         command=self.date_treeview.yview)
        tree_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL,
                                         command=self.date_treeview.xview)
        self.date_treeview.config(yscrollcommand=tree_v_scrollbar.set,
                                  xscrollcommand=tree_h_scrollbar.set)

        # 使用网格布局
        self.date_treeview.grid(row=0, column=0, sticky="nsew")
        tree_v_scrollbar.grid(row=0, column=1, sticky="ns")
        tree_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 配置网格权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # 绑定双击事件
        self.date_treeview.bind('<Double-1>', self.on_date_double_click)

        # 结果显示区域
        result_frame = ttk.LabelFrame(self.main_frame, text="评分结果", padding="20", style="Card.TLabelframe")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.CHAR, font=("微软雅黑", 11))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 配置金色tag用于显示星星
        self.result_text.tag_configure("gold", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        self.result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        # 配置可用/不可用标签
        self.result_text.tag_configure("usable", foreground="#228B22", font=("微软雅黑", 11, "bold"))  # 森林绿
        self.result_text.tag_configure("unusable", foreground="#DC143C", font=("微软雅黑", 11, "bold"))  # 猩红
        self.result_text.tag_configure("bold", font=("微软雅黑", 11, "bold"))
        # ⚠ 警告图标金色前景（仅图标着色，不充填底色）
        self.result_text.tag_configure("warn_icon", foreground="#FFD700")

        # 保存按钮
        save_frame = ttk.Frame(result_frame)
        save_frame.pack(fill=tk.X, pady=5)

        save_btn = ttk.Button(save_frame, text="保存评分结果", width=20, command=self.save_score_result)
        save_btn.pack(side=tk.RIGHT, padx=10)
    
    def on_event_type_changed(self, event=None):
        """事项类型变化时的回调函数——严格按事项类型联动刷新：
           特殊选项（宅型/山向/兼向/罗盘）+ 事主信息数量（嫁娶2人/修造类4人/安葬4人）
        """
        # ————————————————————————————————————————
        # 完整版（full / 独立启动）：完整刷新 UI 并重排所有容器
        # ————————————————————————————————————————
        if self.mode != 'embedded':
            # 1) 特殊选项（山向/宅型/罗盘）：按新事项类型重建
            self.update_special_options()
            # 2) 事主信息（人数/性别）：按新事项类型重建
            self.update_owners_frame()

            # 3) 强制刷新所有几何计算（Tk propagation）
            self.window.update_idletasks()
            self.window.update()

            # 4) 重新打包事主信息区（确保 destroy 重建后正确显示在原位置）
            try:
                self.owners_frame.pack_forget()
            except Exception:
                pass
            self.owners_frame.pack(fill=tk.X, pady=6, padx=20)

            # 5) 重新打包特殊选项区（非修造/动土/入宅事项会清空子控件，
            #    不 repack 会导致容器高度残留或尺寸为 0 后仍占据原高度）
            try:
                self.special_frame.pack_forget()
            except Exception:
                pass
            current_event = self.event_var.get()
            if current_event in ("修造", "动土", "入宅"):
                # 仅在修造类事项显示特殊选项框架（其余事项：隐藏 → 输入区更紧凑）
                self.special_frame.pack(fill=tk.X, pady=3)

            # 6) 强制触发滚动区 Canvas 的 scrollregion 重算（因为事主区高度从2人→4人
            #    或特殊选项从空→显示山向，main_frame 高度变大）
            self.window.update_idletasks()
            self.window.update()
            try:
                self.main_frame.event_generate("<Configure>")
            except Exception:
                pass

        # ————————————————————————————————————————
        # 精简版（embedded）：内部状态刷新，但绝不显示事主/特殊 UI
        # ————————————————————————————————————————
        else:
            self.update_special_options()
            self.update_owners_frame()
            self.window.update_idletasks()
            self.window.update()
            try:
                self.owners_frame.pack_forget()
            except Exception:
                pass
            try:
                self.special_frame.pack_forget()
            except Exception:
                pass
            try:
                self.main_frame.event_generate("<Configure>")
            except Exception:
                pass
    
    def update_special_options(self):
        """更新特殊选项（如阳宅/阴宅选择）"""
        # 清空特殊选项框架
        for widget in self.special_frame.winfo_children():
            widget.destroy()
        
        event_type = self.event_var.get()
        
        # 修造、动土、入宅事项需要选择宅型（阳宅/阴宅）和山向
        if event_type in ["修造", "动土", "入宅"]:
            # 宅型选择
            ttk.Label(self.special_frame, text="宅型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=3)
            self.house_type = tk.StringVar(value="阳宅")
            house_combo = ttk.Combobox(self.special_frame, textvariable=self.house_type,
                                       values=["阳宅", "阴宅"], width=8, state="readonly", font=("微软雅黑", 10))
            house_combo.pack(side=tk.LEFT, padx=3)
            
            # 山向选择（使用二十四山模块的完整山向列表）
            ttk.Label(self.special_frame, text="山向:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=3)
            self.shan_xiang = tk.StringVar()
            # 使用二十四山模块获取完整的24山向列表
            shan_xiangs = get_shan_xiang_list(use_24_shan=True)
            shan_combo = ttk.Combobox(self.special_frame, textvariable=self.shan_xiang, 
                                      values=shan_xiangs, width=12, state="readonly", font=("微软雅黑", 10))
            shan_combo.pack(side=tk.LEFT, padx=3)
            
            # 兼向选择（动态更新）
            ttk.Label(self.special_frame, text="兼向:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=3)
            self.jian_xiang = tk.StringVar(value="正中")
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                      values=["正中", "兼左", "兼右"], width=10, state="readonly", font=("微软雅黑", 10))
            self.jian_xiang_combo.pack(side=tk.LEFT, padx=3)
            self.jian_xiang.set("正中")  # 默认正中
            # 绑定山向变化时更新兼向选项
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)
            
            # 电子罗盘按钮
            ttk.Button(self.special_frame, text="罗盘", width=6,
                      command=self._show_compass_dialog).pack(side=tk.LEFT, padx=3)
            
            # 强制刷新界面
            self.special_frame.update_idletasks()
            self.special_frame.update()
    
    def _update_jianxiang_options(self, *args):
        """根据山向更新兼向选项"""
        shan_xiang = self.shan_xiang.get()
        if not shan_xiang:
            return
        
        # 获取坐山名称
        mountain = shan_xiang_to_shan(shan_xiang)
        
        # 获取相邻的山
        from modules.二十四山 import TWENTY_FOUR_MOUNTAINS_DATA
        mountains = [data[1] for data in TWENTY_FOUR_MOUNTAINS_DATA]
        
        if mountain in mountains:
            idx = mountains.index(mountain)
            left_shan = mountains[(idx - 1) % len(mountains)]
            right_shan = mountains[(idx + 1) % len(mountains)]
            
            # 更新兼向选项
            options = ["正中", f"兼{left_shan}", f"兼{right_shan}"]
            self.jian_xiang_combo['values'] = options
            self.jian_xiang.set("正中")  # 重置为正中
    
    def _show_compass_dialog(self):
        """显示电子罗盘对话框"""
        # 获取当前山向
        initial_shan_xiang = None
        if hasattr(self, 'shan_xiang') and self.shan_xiang.get():
            initial_shan_xiang = self.shan_xiang.get()
        
        def on_compass_select(shan_xiang: str, degree: float):
            """罗盘选择回调"""
            if shan_xiang and hasattr(self, 'shan_xiang'):
                self.shan_xiang.set(shan_xiang)
                
                # 更新兼向显示
                if hasattr(self, 'jian_xiang'):
                    # 根据度数自动识别兼向
                    from modules.电子罗盘 import CompassConverter
                    converter = CompassConverter()
                    mountain = shan_xiang_to_shan(shan_xiang)
                    jianxiang = converter.get_jianxiang(mountain, degree)
                    # 先更新兼向选项
                    self._update_jianxiang_options()
                    # 然后设置兼向值
                    if jianxiang:
                        self.jian_xiang.set(jianxiang)
                    else:
                        self.jian_xiang.set("正中")
        
        # 显示罗盘对话框
        show_compass_dialog(self.window, initial_shan_xiang, on_compass_select)
    
    def update_owners_frame(self):
        """更新事主信息框架"""
        # 清空现有组件
        for widget in self.owners_frame.winfo_children():
            widget.destroy()
        
        self.owners_info = []
        self._owner_entries_list = []  # 清空输入框列表
        event_type = self.event_var.get()
        
        # 添加提示标签
        if event_type != "嫁娶":
            hint_label = tk.Label(self.owners_frame, text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   fg="gray", bg='white', font=("微软雅黑", 11, "italic"))
            hint_label.pack(anchor=tk.W, pady=(0, 10))
        
        if event_type == "嫁娶":
            # 婚嫁需要新娘新郎（必填）
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            # 安葬需要死者（逝者）和孝子（家属）
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type in ["修造", "动土", "入宅", "装修", "作灶", "开业", "出行", "安床"]:
            # 修建类事项、作灶、开业、出行、安床，事主1-4可选（可填可不填）
            owners = ["事主1", "事主2", "事主3", "事主4"]
        else:
            # 其他事项，事主可选（可填可不填）
            owners = ["事主"]
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=8)
            
            # 标题行
            title_row = ttk.Frame(owner_frame)
            title_row.pack(fill=tk.X, pady=2)
            
            tk.Label(title_row, text=f"{owner}:", font=("微软雅黑", 12), bg='white', fg='black').pack(side=tk.LEFT, padx=5)
            
            # 日期类型和性别选择
            type_row = ttk.Frame(owner_frame)
            type_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(type_row, text="日期类型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            date_type_var = tk.StringVar(value="公历")
            
            # 创建单选按钮，先不设置command
            solar_radio = ttk.Radiobutton(type_row, text="公历", variable=date_type_var, value="公历")
            solar_radio.pack(side=tk.LEFT, padx=5)
            lunar_radio = ttk.Radiobutton(type_row, text="农历", variable=date_type_var, value="农历")
            lunar_radio.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(type_row, text="性别:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            gender_var = tk.StringVar(value="男" if owner in ["新郎", "孝子1", "孝子2", "孝子3", "事主1", "事主2", "事主3", "事主4", "事主"] else "女")
            ttk.Radiobutton(type_row, text="男", variable=gender_var, value="男").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(type_row, text="女", variable=gender_var, value="女").pack(side=tk.LEFT, padx=5)
            
            # 婚嫁事项默认填充日期，其他事项默认为空（可选）
            if event_type == "嫁娶":
                solar_year_var = tk.StringVar(value=str(date.today().year - 20))
                solar_month_var = tk.StringVar(value=str(1))
                solar_day_var = tk.StringVar(value=str(1))
                lunar_year_var = tk.StringVar(value=str(date.today().year - 20))
                lunar_month_var = tk.StringVar(value=str(1))
                lunar_day_var = tk.StringVar(value=str(1))
                hour_var = tk.StringVar(value=str(12))
                minute_var = tk.StringVar(value=str(0))
            else:
                solar_year_var = tk.StringVar()
                solar_month_var = tk.StringVar()
                solar_day_var = tk.StringVar()
                lunar_year_var = tk.StringVar()
                lunar_month_var = tk.StringVar()
                lunar_day_var = tk.StringVar()
                hour_var = tk.StringVar(value="12")
                minute_var = tk.StringVar(value="0")
            
            # 闰月变量
            leap_var = tk.BooleanVar(value=False)
            
            # 公历输入框
            solar_frame = ttk.Frame(owner_frame)
            solar_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(solar_frame, text="年:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            solar_year_entry = ttk.Entry(solar_frame, textvariable=solar_year_var, width=6, font=("微软雅黑", 10))
            solar_year_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(solar_frame, text="月:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            solar_month_entry = ttk.Entry(solar_frame, textvariable=solar_month_var, width=4, font=("微软雅黑", 10))
            solar_month_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(solar_frame, text="日:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            solar_day_entry = ttk.Entry(solar_frame, textvariable=solar_day_var, width=4, font=("微软雅黑", 10))
            solar_day_entry.pack(side=tk.LEFT, padx=3)
            
            # 农历输入框
            lunar_frame = ttk.Frame(owner_frame)
            
            ttk.Label(lunar_frame, text="农历年:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            lunar_year_entry = ttk.Entry(lunar_frame, textvariable=lunar_year_var, width=6, font=("微软雅黑", 10))
            lunar_year_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(lunar_frame, text="月:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            lunar_month_entry = ttk.Entry(lunar_frame, textvariable=lunar_month_var, width=4, font=("微软雅黑", 10))
            lunar_month_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(lunar_frame, text="日:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            lunar_day_entry = ttk.Entry(lunar_frame, textvariable=lunar_day_var, width=4, font=("微软雅黑", 10))
            lunar_day_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(lunar_frame, text="闰月:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            leap_check = ttk.Checkbutton(lunar_frame, variable=leap_var)
            leap_check.pack(side=tk.LEFT, padx=3)
            
            # 时间输入行
            time_row = ttk.Frame(owner_frame)
            time_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(time_row, text="时:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            hour_entry = ttk.Entry(time_row, textvariable=hour_var, width=4, font=("微软雅黑", 10))
            hour_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(time_row, text="分:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            minute_entry = ttk.Entry(time_row, textvariable=minute_var, width=4, font=("微软雅黑", 10))
            minute_entry.pack(side=tk.LEFT, padx=3)
            
            # 存储当前事主的输入框，用于跨事主导航
            owner_entries = {
                'solar': [solar_year_entry, solar_month_entry, solar_day_entry],
                'lunar': [lunar_year_entry, lunar_month_entry, lunar_day_entry],
                'time': [hour_entry, minute_entry],
                'all': [solar_year_entry, solar_month_entry, solar_day_entry,
                       lunar_year_entry, lunar_month_entry, lunar_day_entry,
                       hour_entry, minute_entry]
            }
            self._owner_entries_list.append(owner_entries)
            
            # 绑定当前事主的输入框导航
            self._bind_owner_navigation(owner_entries, len(self._owner_entries_list) - 1)
            
            # 四柱显示
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=2)
            
            tk.Label(sizhu_row, text="四柱:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
            sizhu_var = tk.StringVar(value="未计算")
            sizhu_label = tk.Label(sizhu_row, textvariable=sizhu_var, font=("微软雅黑", 10, "bold"), bg='white', fg='black')
            sizhu_label.pack(side=tk.LEFT, padx=3)
            
            # 喜用神显示
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=2)
            
            tk.Label(xishen_row, text="喜神:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
            tk.Label(xishen_row, textvariable=xishen_var, fg="blue", bg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)
            tk.Label(xishen_row, text="  用神:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
            tk.Label(xishen_row, textvariable=yongshen_var, fg="green", bg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=2)
                
                tk.Label(fuzi_row, text="夫星/子星:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
                tk.Label(fuzi_row, textvariable=fuzi_var, fg="purple", bg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)
            
            # 为每个事主创建独立的auto_calculate函数
            def create_auto_calculate(syv, smv, sdv, lyv, lmv, ldv, lv, hv, miv, o, sv, xv, ygv, fzv, dtv, gv):
                def auto_calculate(event):
                    # 根据日期类型获取相应的日期变量
                    if dtv.get() == "公历":
                        year_val = syv.get()
                        month_val = smv.get()
                        day_val = sdv.get()
                    else:
                        year_val = lyv.get()
                        month_val = lmv.get()
                        day_val = ldv.get()
                    
                    hour_val = hv.get()
                    minute_val = miv.get()
                    
                    if year_val and month_val and day_val and hour_val and minute_val:
                        try:
                            year = int(year_val)
                            month = int(month_val)
                            day = int(day_val)
                            hour = int(hour_val)
                            minute = int(minute_val)
                            
                            # 验证日期有效性
                            if 0 <= hour < 24 and 0 <= minute < 60:
                                # 延迟计算，避免频繁触发
                                self.window.after(500, lambda:
                                    self.calculate_owner_sizhu(syv, smv, sdv, lyv, lmv, ldv, lv, hv, miv, o, sv, xv, ygv, fzv, dtv, gv))
                        except:
                            pass
                return auto_calculate
            
            # 创建独立的auto_calculate函数
            auto_calculate = create_auto_calculate(solar_year_var, solar_month_var, solar_day_var, 
                                                lunar_year_var, lunar_month_var, lunar_day_var, leap_var, 
                                                hour_var, minute_var, owner, sizhu_var, xishen_var, yongshen_var, fuzi_var, 
                                                date_type_var, gender_var)
            
            # 日期类型选择变化时的回调函数
            def create_toggle_command(dt_var, sf, lf, tr, owner_name):
                def toggle_date_fields():
                    current_type = dt_var.get()
                    print(f"[DEBUG] {owner_name}: 日期类型切换为 '{current_type}'")
                    if current_type == "农历":
                        # 显示农历输入框，隐藏公历输入框
                        print(f"[DEBUG] {owner_name}: 显示农历输入框")
                        sf.pack_forget()
                        lf.pack(fill=tk.X, pady=2, before=tr)
                    else:
                        # 显示公历输入框，隐藏农历输入框
                        print(f"[DEBUG] {owner_name}: 显示公历输入框")
                        lf.pack_forget()
                        sf.pack(fill=tk.X, pady=2, before=tr)
                return toggle_date_fields
            
            # 创建并绑定日期类型变化事件
            toggle_command = create_toggle_command(date_type_var, solar_frame, lunar_frame, time_row, owner)
            
            # 为单选按钮设置command - 使用工厂函数确保正确捕获变量
            def create_radio_command(dt_var, cmd, value):
                def radio_command():
                    dt_var.set(value)
                    self.window.after(10, cmd)
                return radio_command
            
            solar_radio.config(command=create_radio_command(date_type_var, toggle_command, "公历"))
            lunar_radio.config(command=create_radio_command(date_type_var, toggle_command, "农历"))
            
            # 同时绑定变量变化事件
            def create_trace_callback(cmd):
                return lambda *args: self.window.after(10, cmd)
            
            date_type_var.trace_add('write', create_trace_callback(toggle_command))
            
            # 初始状态
            toggle_command()
            
            # 绑定输入框的事件
            solar_year_entry.bind('<KeyRelease>', auto_calculate)
            solar_month_entry.bind('<KeyRelease>', auto_calculate)
            solar_day_entry.bind('<KeyRelease>', auto_calculate)
            lunar_year_entry.bind('<KeyRelease>', auto_calculate)
            lunar_month_entry.bind('<KeyRelease>', auto_calculate)
            lunar_day_entry.bind('<KeyRelease>', auto_calculate)
            hour_entry.bind('<KeyRelease>', auto_calculate)
            minute_entry.bind('<KeyRelease>', auto_calculate)
            
            # 按钮行
            button_row = ttk.Frame(owner_frame)
            button_row.pack(fill=tk.X, pady=2)
            
            # 计算按钮
            calc_btn = ttk.Button(button_row, text="计算四柱", 
                                 command=lambda sy=solar_year_var, sm=solar_month_var, sd=solar_day_var, 
                                 ly=lunar_year_var, lm=lunar_month_var, ld=lunar_day_var, lp=leap_var, 
                                 h=hour_var, mi=minute_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var, dt=date_type_var, g=gender_var: 
                                 self.calculate_owner_sizhu(sy, sm, sd, ly, lm, ld, lp, h, mi, o, s, x, yg, fz, dt, g))
            calc_btn.pack(side=tk.LEFT, padx=10)
            
            # 八字排盘详情按钮
            bazi_btn = ttk.Button(button_row, text="八字排盘详情", 
                                 command=lambda sy=solar_year_var, sm=solar_month_var, sd=solar_day_var, 
                                 ly=lunar_year_var, lm=lunar_month_var, ld=lunar_day_var, lp=leap_var, 
                                 h=hour_var, mi=minute_var, o=owner, dt=date_type_var, g=gender_var: 
                                 self.show_bazi_detail(sy, sm, sd, ly, lm, ld, lp, h, mi, o, dt, g))
            bazi_btn.pack(side=tk.LEFT, padx=10)
            
            # 保存事主信息
            owner_info = {
                'name': owner,
                'solar_year': solar_year_var,
                'solar_month': solar_month_var,
                'solar_day': solar_day_var,
                'lunar_year': lunar_year_var,
                'lunar_month': lunar_month_var,
                'lunar_day': lunar_day_var,
                'leap': leap_var,
                'hour': hour_var,
                'minute': minute_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var,
                'date_type_var': date_type_var,  # 保存日期类型引用
                'gender_var': gender_var  # 保存性别引用
            }
            
            self.owners_info.append(owner_info)
    
    def _bind_entry_navigation(self, entries):
        """为输入框绑定键盘导航功能"""
        if not entries:
            return
            
        def on_key_down(event, idx):
            """向下/向右移动到下一个输入框"""
            if idx < len(entries) - 1:
                entries[idx + 1].focus_set()
                entries[idx + 1].select_range(0, tk.END)
            return "break"
        
        def on_key_up(event, idx):
            """向上/向左移动到上一个输入框"""
            if idx > 0:
                entries[idx - 1].focus_set()
                entries[idx - 1].select_range(0, tk.END)
            return "break"
        
        def on_key_right(event, idx):
            """向右移动到下一个输入框"""
            # 检查光标是否在最后或输入框为空
            widget = event.widget
            if widget.index(tk.INSERT) >= len(widget.get()):
                if idx < len(entries) - 1:
                    entries[idx + 1].focus_set()
                    entries[idx + 1].select_range(0, tk.END)
                    return "break"
            return None
        
        def on_key_tab(event, idx):
            """Tab键移动到下一个输入框"""
            if idx < len(entries) - 1:
                entries[idx + 1].focus_set()
                entries[idx + 1].select_range(0, tk.END)
                return "break"
            return None
        
        def on_key_left(event, idx):
            """向左移动到上一个输入框"""
            # 检查光标是否在开头
            widget = event.widget
            if widget.index(tk.INSERT) == 0:
                if idx > 0:
                    entries[idx - 1].focus_set()
                    entries[idx - 1].select_range(0, tk.END)
                    return "break"
            return None
        
        for i, entry in enumerate(entries):
            # 绑定方向键
            entry.bind('<Down>', lambda e, idx=i: on_key_down(e, idx))
            entry.bind('<Up>', lambda e, idx=i: on_key_up(e, idx))
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, idx))
            # 绑定Tab键
            entry.bind('<Tab>', lambda e, idx=i: on_key_tab(e, idx))
    
    def _bind_owner_navigation(self, owner_entries, owner_idx):
        """为单个事主的输入框绑定键盘导航，支持跨事主导航
        
        Args:
            owner_entries: 当前事主的输入框字典
            owner_idx: 当前事主的索引
        """
        solar_entries = owner_entries['solar']
        lunar_entries = owner_entries['lunar']
        time_entries = owner_entries['time']
        
        # 获取当前日期类型
        date_type = self.owners_info[owner_idx]['date_type'] if owner_idx < len(self.owners_info) else None
        
        def get_visible_entries():
            """获取当前可见的输入框列表"""
            if date_type and date_type.get() == "农历":
                return lunar_entries + time_entries
            else:
                return solar_entries + time_entries
        
        def on_key_right(event, current_entries, entry_idx):
            """向右移动"""
            visible_entries = get_visible_entries()
            # 在当前可见组内移动
            if entry_idx < len(current_entries) - 1:
                next_idx = entry_idx + 1
            elif current_entries == solar_entries and date_type and date_type.get() == "公历":
                # 从公历日移动到时
                time_entries[0].focus_set()
                time_entries[0].select_range(0, tk.END)
                return "break"
            elif current_entries == lunar_entries and date_type and date_type.get() == "农历":
                # 从农历日移动到时
                time_entries[0].focus_set()
                time_entries[0].select_range(0, tk.END)
                return "break"
            elif current_entries == time_entries:
                # 从分移动到下一个事主
                if owner_idx < len(self._owner_entries_list) - 1:
                    next_owner = self._owner_entries_list[owner_idx + 1]
                    next_visible = next_owner['solar'] if next_owner.get('date_type', '公历') == '公历' else next_owner['lunar']
                    next_visible[0].focus_set()
                    next_visible[0].select_range(0, tk.END)
                return "break"
            else:
                return None
            
            current_entries[next_idx].focus_set()
            current_entries[next_idx].select_range(0, tk.END)
            return "break"
        
        def on_key_left(event, current_entries, entry_idx):
            """向左移动"""
            if entry_idx > 0:
                prev_idx = entry_idx - 1
                current_entries[prev_idx].focus_set()
                current_entries[prev_idx].select_range(0, tk.END)
                return "break"
            elif current_entries == time_entries:
                # 从时移动到日（公历或农历）
                if date_type and date_type.get() == "农历":
                    lunar_entries[-1].focus_set()
                    lunar_entries[-1].select_range(0, tk.END)
                else:
                    solar_entries[-1].focus_set()
                    solar_entries[-1].select_range(0, tk.END)
                return "break"
            elif current_entries in [solar_entries, lunar_entries] and owner_idx > 0:
                # 移动到上一个事主的最后一个输入框
                prev_owner = self._owner_entries_list[owner_idx - 1]
                prev_time = prev_owner['time']
                prev_time[-1].focus_set()
                prev_time[-1].select_range(0, tk.END)
                return "break"
            return None
        
        def on_key_down(event):
            """向下移动到下一个事主的对应输入框"""
            if owner_idx < len(self._owner_entries_list) - 1:
                next_owner = self._owner_entries_list[owner_idx + 1]
                # 找到当前输入框在可见列表中的位置
                visible = get_visible_entries()
                widget = event.widget
                try:
                    current_idx = visible.index(widget)
                    next_visible = next_owner['solar'] if next_owner.get('date_type', '公历') == '公历' else next_owner['lunar']
                    if current_idx < len(next_visible):
                        next_visible[current_idx].focus_set()
                        next_visible[current_idx].select_range(0, tk.END)
                except ValueError:
                    pass
            return "break"
        
        def on_key_up(event):
            """向上移动到上一个事主的对应输入框"""
            if owner_idx > 0:
                prev_owner = self._owner_entries_list[owner_idx - 1]
                visible = get_visible_entries()
                widget = event.widget
                try:
                    current_idx = visible.index(widget)
                    prev_visible = prev_owner['solar'] if prev_owner.get('date_type', '公历') == '公历' else prev_owner['lunar']
                    if current_idx < len(prev_visible):
                        prev_visible[current_idx].focus_set()
                        prev_visible[current_idx].select_range(0, tk.END)
                except ValueError:
                    pass
            return "break"
        
        # 绑定公历输入框
        for i, entry in enumerate(solar_entries):
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, solar_entries, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, solar_entries, idx))
            entry.bind('<Down>', on_key_down)
            entry.bind('<Up>', on_key_up)
        
        # 绑定农历输入框
        for i, entry in enumerate(lunar_entries):
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, lunar_entries, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, lunar_entries, idx))
            entry.bind('<Down>', on_key_down)
            entry.bind('<Up>', on_key_up)
        
        # 绑定时间输入框
        for i, entry in enumerate(time_entries):
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, time_entries, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, time_entries, idx))
            entry.bind('<Down>', on_key_down)
            entry.bind('<Up>', on_key_up)
    
    def calculate_owner_sizhu(self, solar_year_var, solar_month_var, solar_day_var, 
                              lunar_year_var, lunar_month_var, lunar_day_var, leap_var, 
                              hour_var, minute_var, owner, sizhu_var, xishen_var, yongshen_var, 
                              fuzi_var=None, date_type_var=None, gender_var=None, longitude=None):
        """计算事主四柱

        longitude: 事主出生地经度（真太阳时）；None=120°E 北京时间基准。
                   界面手动输入回路（L1470/L1540）无经度来源，不传即保持旧行为。
        """
        try:
            # 防御性检查：获取小时和分钟
            hour_str = hour_var.get() if hour_var and hasattr(hour_var, 'get') else str(hour_var) if hour_var else ''
            minute_str = minute_var.get() if minute_var and hasattr(minute_var, 'get') else str(minute_var) if minute_var else ''
            
            # 使用默认值而不是直接返回
            hour = int(hour_str) if hour_str else 12
            minute = int(minute_str) if minute_str else 0
            
            # 处理日期类型和闰月
            date_type = date_type_var.get() if date_type_var and hasattr(date_type_var, 'get') else "公历"
            is_leap = leap_var.get() if leap_var and hasattr(leap_var, 'get') else False
            
            if date_type == "农历":
                # 农历日期转换为公历
                lunar_year_str = lunar_year_var.get() if lunar_year_var and hasattr(lunar_year_var, 'get') else str(lunar_year_var) if lunar_year_var else ''
                lunar_month_str = lunar_month_var.get() if lunar_month_var and hasattr(lunar_month_var, 'get') else str(lunar_month_var) if lunar_month_var else ''
                lunar_day_str = lunar_day_var.get() if lunar_day_var and hasattr(lunar_day_var, 'get') else str(lunar_day_var) if lunar_day_var else ''
                
                if not (lunar_year_str and lunar_month_str and lunar_day_str):
                    return
                    
                year = int(lunar_year_str)
                month = int(lunar_month_str)
                day = int(lunar_day_str)
                # 使用sxtwl库进行农历转公历
                import sxtwl
                day_obj = sxtwl.fromLunar(year, month, day, is_leap)
                target_date = date(day_obj.getSolarYear(), day_obj.getSolarMonth(), day_obj.getSolarDay())
            else:
                # 公历日期
                solar_year_str = solar_year_var.get() if solar_year_var and hasattr(solar_year_var, 'get') else str(solar_year_var) if solar_year_var else ''
                solar_month_str = solar_month_var.get() if solar_month_var and hasattr(solar_month_var, 'get') else str(solar_month_var) if solar_month_var else ''
                solar_day_str = solar_day_var.get() if solar_day_var and hasattr(solar_day_var, 'get') else str(solar_day_var) if solar_day_var else ''
                
                if not (solar_year_str and solar_month_str and solar_day_str):
                    return
                    
                year = int(solar_year_str)
                month = int(solar_month_str)
                day = int(solar_day_str)
                target_date = date(year, month, day)
            
            sizhu = calculate_sizhu(target_date, hour, minute, longitude=longitude)
            analysis = analyze_sizhu(sizhu)
            
            # 显示四柱
            sizhu_text = f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}"
            sizhu_var.set(sizhu_text)
            
            # 显示生肖
            year_zhi = sizhu['年柱'][1] if len(sizhu['年柱']) > 1 else ''
            zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                         '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
            zodiac = zodiac_map.get(year_zhi, '')
            # 如果有生肖显示变量，则设置生肖
            if hasattr(self, 'zodiac_var') and self.zodiac_var and hasattr(self.zodiac_var, 'set'):
                self.zodiac_var.set(zodiac)
            
            # 显示喜用神 - 使用统一的喜用神计算器
            xishen, yongshen = calculate_xishen_yongshen(sizhu, analysis)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 婚嫁事项显示夫星子星
            if fuzi_var and hasattr(fuzi_var, 'set') and self.event_var.get() == "嫁娶" and owner == "新娘":
                fuzi = analysis.get('夫星子星', {})
                fu_xing = fuzi.get('fu', '')
                zi_xing = fuzi.get('zi', '')
                if fu_xing or zi_xing:
                    fuzi_var.set(f"夫星: {fu_xing}, 子星: {zi_xing}")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算四柱失败: {str(e)}")
            logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
    
    def show_bazi_detail(self, solar_year_var, solar_month_var, solar_day_var, 
                         lunar_year_var, lunar_month_var, lunar_day_var, leap_var, 
                         hour_var, minute_var, owner, date_type_var=None, gender_var=None):
        """显示八字排盘详情"""
        try:
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            
            # 处理日期类型和闰月
            date_type = date_type_var.get() if date_type_var else "公历"
            is_leap = leap_var.get() if leap_var else False
            gender = gender_var.get() if gender_var else "男"
            
            if date_type == "农历":
                # 农历日期转换为公历
                year = int(lunar_year_var.get())
                month = int(lunar_month_var.get())
                day = int(lunar_day_var.get())
                # 使用sxtwl库进行农历转公历
                import sxtwl
                day_obj = sxtwl.fromLunar(year, month, day, is_leap)
                solar_year = day_obj.getSolarYear()
                solar_month = day_obj.getSolarMonth()
                solar_day = day_obj.getSolarDay()
            else:
                # 公历日期
                solar_year = int(solar_year_var.get())
                solar_month = int(solar_month_var.get())
                solar_day = int(solar_day_var.get())

            # 使用八字可视化模块显示排盘
            from .八字可视化模块 import show_bazi_from_birth
            show_bazi_from_birth(
                self.window,
                solar_year,
                solar_month,
                solar_day,
                hour,
                minute,
                gender
            )
        except Exception as e:
            messagebox.showerror("错误", f"显示八字排盘详情失败: {str(e)}")
            logger.error(f"显示八字排盘详情失败: {str(e)}", exc_info=True)
    
    def toggle_input_mode(self):
        """切换输入方式"""
        if self.input_mode.get() == "date":
            self.date_frame.pack(fill=tk.X, pady=5)
            self.sizhu_frame.pack_forget()
        else:
            self.date_frame.pack_forget()
            self.sizhu_frame.pack(fill=tk.X, pady=5)
    
    def add_date(self):
        """添加日期到列表"""
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            datetime.strptime(time_str, '%H:%M')
            
            # 组合日期和时间
            date_time_str = f"{date_str} {time_str}"
            
            if date_time_str not in self.date_list:
                self.date_list.append(date_time_str)
                # 添加到Treeview - 使用完整的10列
                self.date_treeview.insert('', tk.END, values=(date_time_str, '', '', '', '', '', '', '', '', ''))
            else:
                messagebox.showwarning("警告", "该日期时间已在列表中")
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确")
    
    def add_sizhu(self):
        """添加四柱到列表"""
        nian_zhu = self.sizhu_entries[0].get().strip()
        yue_zhu = self.sizhu_entries[1].get().strip()
        ri_zhu = self.sizhu_entries[2].get().strip()
        shi_zhu = self.sizhu_entries[3].get().strip()
        
        # 验证四柱格式
        if not all([nian_zhu, yue_zhu, ri_zhu, shi_zhu]):
            messagebox.showwarning("警告", "请完整填写四柱")
            return
        
        for zhu, name in [(nian_zhu, "年柱"), (yue_zhu, "月柱"), (ri_zhu, "日柱"), (shi_zhu, "时柱")]:
            if len(zhu) != 2:
                messagebox.showwarning("警告", f"{name}格式错误，应为两个字（如：甲子）")
                return
        
        # 生成四柱字符串
        sizhu_str = f"{nian_zhu} {yue_zhu} {ri_zhu} {shi_zhu}"
        
        # 检查是否已存在
        if sizhu_str in self.date_list:
            messagebox.showwarning("警告", "该四柱已存在")
            return
        
        # 添加到列表
        self.date_list.append(sizhu_str)
        # 添加到Treeview
        self.date_treeview.insert('', tk.END, values=(sizhu_str, '', '', sizhu_str, '', '', '', '', '', ''))
        
        # 清空输入框
        for entry in self.sizhu_entries:
            entry.delete(0, tk.END)
    
    def clear_dates(self):
        """清空日期"""
        self.date_list = []
        # 清空Treeview
        for item in self.date_treeview.get_children():
            self.date_treeview.delete(item)
        self.scoring_results = []
    
    def start_scoring(self):
        """开始评分"""
        # 根据当前输入方式获取日课
        input_mode = self.input_mode.get()
        
        if input_mode == "date":
            # 按日期输入
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                
                # 处理时间格式，支持多种输入方式
                if ':' in time_str:
                    # 已有冒号，直接验证
                    datetime.strptime(time_str, '%H:%M')
                else:
                    # 无冒号，根据长度处理
                    time_str = time_str.strip()
                    if len(time_str) == 1:
                        # 只有小时，如"8" → "08:00"
                        time_str = f"0{time_str}:00"
                    elif len(time_str) == 2:
                        # 只有小时，如"12" → "12:00"
                        time_str = f"{time_str}:00"
                    elif len(time_str) == 3:
                        # 小时+分钟，如"830" → "08:30"
                        time_str = f"0{time_str[:1]}:{time_str[1:]}"
                    elif len(time_str) == 4:
                        # 小时+分钟，如"1230" → "12:30"
                        time_str = f"{time_str[:2]}:{time_str[2:]}"
                    else:
                        # 其他情况，抛出异常
                        raise ValueError("时间格式错误")
                
                current_rike = f"{date_str} {time_str}"
            except ValueError:
                messagebox.showerror("错误", "日期或时间格式不正确")
                return
        else:
            # 按四柱输入
            nian_zhu = self.sizhu_entries[0].get().strip()
            yue_zhu = self.sizhu_entries[1].get().strip()
            ri_zhu = self.sizhu_entries[2].get().strip()
            shi_zhu = self.sizhu_entries[3].get().strip()
            
            # 验证四柱格式
            if not all([nian_zhu, yue_zhu, ri_zhu, shi_zhu]):
                messagebox.showwarning("警告", "请完整填写四柱")
                return
            
            for zhu, name in [(nian_zhu, "年柱"), (yue_zhu, "月柱"), (ri_zhu, "日柱"), (shi_zhu, "时柱")]:
                if len(zhu) != 2:
                    messagebox.showwarning("警告", f"{name}格式错误，应为两个字（如：甲子）")
                    return
            
            current_rike = f"{nian_zhu} {yue_zhu} {ri_zhu} {shi_zhu}"
        
        # 检查是否已存在于已评分列表中
        if current_rike in self.date_list:
            # 检查是否已经有评分结果
            has_score = False
            for item in self.date_treeview.get_children():
                values = self.date_treeview.item(item, 'values')
                if values[0] == current_rike and values[1] != '':  # 第二列是评分
                    has_score = True
                    break
            
            if has_score:
                messagebox.showwarning("警告", "该日课已评分")
                return
            # 如果已添加但未评分，继续评分流程
        
        event_type = self.event_var.get()
        
        # 获取事主信息
        owners_detail = []
        for info in self.owners_info:
            try:
                # 修正：使用正确的字段名称
                year_val = info['solar_year'].get() if hasattr(info['solar_year'], 'get') else ''
                month_val = info['solar_month'].get() if hasattr(info['solar_month'], 'get') else ''
                day_val = info['solar_day'].get() if hasattr(info['solar_day'], 'get') else ''
                hour_val = info['hour'].get() if hasattr(info['hour'], 'get') else '12'
                minute_val = info['minute'].get() if hasattr(info['minute'], 'get') else '0'
                
                # 检查是否有完整的日期信息
                if not (year_val and month_val and day_val):
                    continue
                
                year = int(year_val)
                month = int(month_val)
                day = int(day_val)
                hour = int(hour_val)
                minute = int(minute_val)
                
                target_date = date(year, month, day)
                sizhu = calculate_sizhu(target_date, hour, minute, longitude=info.get('longitude'))
                analysis = analyze_sizhu(sizhu)
                
                # 获取姓名（添加防御性检查）
                name = info['name'].get() if hasattr(info['name'], 'get') else info.get('name', '')
                
                owner_detail = {
                    'name': name,
                    'gender': info['gender_var'].get() if hasattr(info.get('gender_var'), 'get') else info.get('gender', ''),
                    'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'xishen': info['xishen_var'].get() if hasattr(info.get('xishen_var'), 'get') else '',
                    'yongshen': info['yongshen_var'].get() if hasattr(info.get('yongshen_var'), 'get') else '',
                    'fu_xing': '',
                    'zi_xing': ''
                }
                
                if event_type == "嫁娶" and info.get('fuzi_var'):
                    fuzi_str = info['fuzi_var'].get()
                    if '夫星:' in fuzi_str:
                        parts = fuzi_str.split(', ')
                        owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                        if len(parts) > 1:
                            owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                
                owners_detail.append(owner_detail)
            except Exception as e:
                continue
        
        # 评分当前日课
        try:
            _hour_is_demo = True  # 默认午时为示例柱；四柱直入/带时分日期改为False
            # 判断是日期还是四柱
            if len(current_rike.split()) == 4 and all(len(zhu) == 2 for zhu in current_rike.split()):
                # 这是四柱格式（如：甲子 乙丑 丙寅 丁卯）
                parts = current_rike.split()
                sizhu = {
                    '年柱': parts[0],
                    '月柱': parts[1],
                    '日柱': parts[2],
                    '时柱': parts[3],
                    'year_gan': parts[0][0],
                    'year_zhi': parts[0][1],
                    'month_gan': parts[1][0],
                    'month_zhi': parts[1][1],
                    'day_gan': parts[2][0],
                    'day_zhi': parts[2][1],
                    'hour_gan': parts[3][0],
                    'hour_zhi': parts[3][1],
                    'is_sizhu_input': True  # 标记这是四柱输入模式
                }
                # 从年柱地支推断年份（仅用于显示，不用于验证）
                zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                year_zhi = parts[0][1]
                if year_zhi in zhi_order:
                    base_year = 2024
                    base_zhi_index = zhi_order.index('辰')
                    target_zhi_index = zhi_order.index(year_zhi)
                    diff = (target_zhi_index - base_zhi_index) % 12
                    sizhu['year'] = base_year + diff
                # 从月柱地支推断月份
                month_zhi = parts[1][1]
                if month_zhi in zhi_order:
                    sizhu['month'] = zhi_order.index(month_zhi) + 1
                # 从日柱地支推断日期（简化处理）
                sizhu['day'] = 1
                display_date = f"四柱: {current_rike}"
                _hour_is_demo = False
                _hour_is_demo = False
            else:
                # 这是日期时间格式（如：2025-03-03 14:30）
                parts = current_rike.split()
                if len(parts) == 2:
                    date_part = parts[0]
                    time_part = parts[1]
                    hour, minute = map(int, time_part.split(':'))
                    score_date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                    sizhu = calculate_sizhu(score_date_obj, hour, minute)
                    display_date = current_rike
                    _hour_is_demo = False
                    _hour_is_demo = False
                else:
                    # 兼容旧格式（只有日期）
                    score_date_obj = datetime.strptime(current_rike, '%Y-%m-%d').date()
                    sizhu = calculate_sizhu(score_date_obj, 12, 0)
                    display_date = current_rike
            
            # 获取宅型和山向（如果是修造、动土、入宅事项）
            house_type = None
            shan_xiang = None
            jian_xiang = None
            if event_type in ["修造", "动土", "入宅"]:
                # 获取宅型
                house_type = getattr(self, 'house_type', None)
                if house_type:
                    house_type = house_type.get()
                # 获取山向
                shan_xiang = getattr(self, 'shan_xiang', None)
                if shan_xiang:
                    shan_xiang = shan_xiang.get()
                # 获取兼向
                jian_xiang = getattr(self, 'jian_xiang', None)
                if jian_xiang:
                    jian_xiang = jian_xiang.get()
            
            # 使用calculate_score进行评分
            score_result = calculate_score(sizhu, event_type, owners_detail, house_type, shan_xiang, None, None, None, jian_xiang)
            result = {
                'date': display_date,
                'score': score_result['score'],
                'level': score_result['level'],
                'reason': score_result.get('reason', ''),
                'sizhu': sizhu,
                'event_type': event_type,
                'owners_detail': owners_detail,
                'huangdao_info': score_result.get('huangdao_info', {}),
                'wu_xing_result': score_result.get('wu_xing_result', {}),
                'yi_list': score_result.get('yi_list', []),
                'ji_list': score_result.get('ji_list', []),
                'shensha_list': score_result.get('shensha_list', []),
                'score_details': score_result.get('score_details', {}),
                'sansha_info': score_result.get('sansha_info', {}),
                'shan_xiang': shan_xiang or ''
            }
            # 用户显式指定时柱（四柱直入/带时分日期）：时柱关系实际计入五行评分·
            # 地支关系得分，用 is_demo_hour=False 重算五行详情并加真实后缀，
            # 避免“（示例时柱，不计分）”与“时柱关系得分+6”自相矛盾（2026-09-10勘正）
            if not _hour_is_demo and isinstance(score_result.get('wu_xing_result'), dict):
                try:
                    try:
                        from modules.评分器 import Scorer as _RScorer
                    except Exception:
                        try:
                            from .评分器 import Scorer as _RScorer
                        except Exception:
                            from 评分器 import Scorer as _RScorer
                    _h_suffix = ('（所选时柱，冲合刑害不计入日课总分，详见十二时辰吉凶）'
                                 if event_type in ('嫁娶', '订婚', '纳采')
                                 else '（所选时柱，已计入五行评分·地支关系得分）')
                    _nd = _RScorer()._generate_wu_xing_details(sizhu, owners_detail, is_demo_hour=False)
                    if isinstance(_nd, dict) and isinstance(_nd.get('地支关系'), list):
                        _new_dz = []
                        for _ln in _nd['地支关系']:
                            if '示例时柱' in _ln:
                                _ln = _ln.replace('（示例时柱，不计分）', _h_suffix)
                            elif '时柱' in _ln and not _ln.endswith(_h_suffix):
                                _ln = _ln + _h_suffix
                            _new_dz.append(_ln)
                        _nd['地支关系'] = _new_dz
                        score_result['wu_xing_result']['details'] = _nd
                except Exception:
                    pass

            # 添加到列表
            self.date_list.append(current_rike)
            
            # 准备显示数据
            score = result['score']
            level = result['level']
            sizhu = result['sizhu']
            sizhu_str = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
            
            # 获取详细得分信息
            score_details = score_result.get('score_details', {})
            wuxing_score = score_details.get('五行评分', 100)
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            
            # 获取地支关系信息（从wu_xing_result中获取详细地支关系）
            wu_xing_result = score_result.get('wu_xing_result', {})
            wu_xing_details = wu_xing_result.get('details', {})
            
            # 构建地支关系文本（显示具体的三合、六合等）
            dizhi_relations = wu_xing_details.get('地支关系', [])
            if dizhi_relations:
                # 提取地支关系的简短描述
                dizhi_text_list = []
                for relation in dizhi_relations:
                    # 提取关键信息，如"三合火局"、"六合"等
                    if '三合' in relation:
                        # 提取"三合X局"
                        import re
                        match = re.search(r'三合(.)局', relation)
                        if match:
                            dizhi_text_list.append(f"三合{match.group(1)}局")
                        else:
                            dizhi_text_list.append('三合')
                    elif '六合' in relation:
                        dizhi_text_list.append('六合')
                    elif '六冲' in relation:
                        dizhi_text_list.append('六冲')
                    elif '六害' in relation:
                        dizhi_text_list.append('六害')
                    elif '三刑' in relation:
                        dizhi_text_list.append('三刑')
                    elif '相破' in relation:
                        dizhi_text_list.append('相破')
                    else:
                        # 其他关系，取前10个字符
                        dizhi_text_list.append(relation[:10])
                dizhi_text = ', '.join(dizhi_text_list[:2])  # 最多显示2个关系
            else:
                dizhi_text = '-'
            
            # 获取吉神信息（从wu_xing_details中获取详细吉神）
            jishen_list = wu_xing_details.get('吉神', [])
            if jishen_list:
                # 提取吉神的简短描述
                jishen_text_list = []
                for jishen in jishen_list:
                    # 提取关键信息，如"天德贵人"、"禄神"等
                    if '天德贵人' in jishen:
                        jishen_text_list.append('天德贵人')
                    elif '月德贵人' in jishen:
                        jishen_text_list.append('月德贵人')
                    elif '天乙贵人' in jishen:
                        jishen_text_list.append('天乙贵人')
                    elif '文昌贵人' in jishen:
                        jishen_text_list.append('文昌贵人')
                    elif '禄神' in jishen:
                        jishen_text_list.append('禄神')
                    elif '福星' in jishen:
                        jishen_text_list.append('福星')
                    else:
                        # 其他吉神，取前6个字符
                        jishen_text_list.append(jishen[:6])
                jishen_text = ', '.join(jishen_text_list[:2])  # 最多显示2个吉神
            else:
                # 如果没有详细吉神，使用yi_list
                yi_list = score_result.get('yi_list', [])
                jishen_text = ', '.join(yi_list[:2]) if yi_list else '-'
            
            # 更新或添加到Treeview
            values = (current_rike, score, level, sizhu_str, wuxing_score, yueling_score, xishen_score, huangdao_score, dizhi_text, jishen_text)
            
            # 检查是否已存在于Treeview中
            existing_item = None
            for item in self.date_treeview.get_children():
                item_values = self.date_treeview.item(item, 'values')
                if item_values[0] == current_rike:
                    existing_item = item
                    break
            
            if existing_item:
                # 更新已存在的行
                self.date_treeview.item(existing_item, values=values)
            else:
                # 添加新行
                self.date_treeview.insert('', tk.END, values=values)
            
            self.scoring_results.append(result)
            
            # 显示结果
            self.show_single_result(result)
            
            # 确保日课评分系统窗口获得焦点后再显示消息框
            self.window.lift()
            self.window.focus_force()
            messagebox.showinfo("成功", f"日课评分完成！\n评分：{result['score']} 分\n等级：{result['level']}")
        except Exception as e:
            messagebox.showerror("错误", f"评分时出错: {str(e)}")
    
    def on_date_double_click(self, event):
        """双击日课显示详细信息"""
        selected = self.date_treeview.selection()
        if not selected:
            return
        
        item = selected[0]
        date_str = self.date_treeview.item(item, 'values')[0]
        
        # 查找对应的评分结果
        result = None
        for r in self.scoring_results:
            if r['date'] == date_str:
                result = r
                break
        
        if result:
            self.show_single_result(result)
    
    def _insert_colored_text(self, text, tag=None):
        """插入带颜色的文本；⚠ 警告图标统一金色前景（不充填底色）"""
        if '⚠' in text:
            _segments = text.split('⚠')
            for _k, _part in enumerate(_segments):
                if _k:
                    if _part.startswith('️'):
                        _part = _part[1:]  # 去emoji变体符，确保前景色生效
                    self.result_text.insert(tk.END, '⚠', "warn_icon")
                if _part:
                    if tag:
                        self.result_text.insert(tk.END, _part, tag)
                    else:
                        self.result_text.insert(tk.END, _part)
            return
        if tag:
            self.result_text.insert(tk.END, text, tag)
        else:
            self.result_text.insert(tk.END, text)
    
    def _generate_yueling_analysis(self, result):
        """【月令分析】兜底现算：reason无月令段时，用四柱旺相休囚死表生成分析文字。
        措辞与主程序详情页【月令分析】保持一致（2026-02-26 校对新增）。"""
        try:
            parts4 = None
            sz = result.get('sizhu')
            if isinstance(sz, dict):
                parts4 = [sz.get('年柱', '') or '', sz.get('月柱', '') or '',
                          sz.get('日柱', '') or '', sz.get('时柱', '') or '']
            elif isinstance(sz, str) and len(sz.split()) == 4:
                parts4 = sz.split()
            if not parts4:
                det = result.get('detail') or result.get('original_result') or {}
                if isinstance(det, dict):
                    dsz = det.get('sizhu')
                    if isinstance(dsz, dict):
                        parts4 = [dsz.get('年柱', '') or '', dsz.get('月柱', '') or '',
                                  dsz.get('日柱', '') or '', dsz.get('时柱', '') or '']
                    elif isinstance(dsz, str) and len(dsz.split()) == 4:
                        parts4 = dsz.split()
            if not parts4:
                return ''
            day_gan = (parts4[2] or '')[:1]
            month_zhi = (parts4[1] or '')[1:2]
            if not day_gan or not month_zhi:
                return ''
            gan_wx = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
                      '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
            zhi_wx = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
                      '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}
            wangxiang_table = {
                '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
                '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
                '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
                '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
                '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
                '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
                '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
                '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
            }
            state = ''
            for k, zlist in wangxiang_table.get(day_gan, {}).items():
                if month_zhi in zlist:
                    state = k
                    break
            if not state:
                return ''
            day_wx = gan_wx.get(day_gan, '')
            month_wx = zhi_wx.get(month_zhi, '')
            sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
            ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
            parts = []
            if state == '旺':
                parts.append(f"{day_gan}日主属{day_wx}气，月支{month_zhi}为{day_wx}气得令之月，日主得令而旺")
            elif state == '相':
                parts.append(f"{day_gan}日主属{day_wx}气，月支{month_zhi}得生而相")
            elif state == '休':
                parts.append(f"{day_gan}日主属{day_wx}气，月支{month_zhi}休囚泄气")
            elif state == '囚':
                parts.append(f"{day_gan}日主属{day_wx}气，月支{month_zhi}非{day_wx}气得令之月，日主失令（{day_wx}克当令之气，反受令困，处囚地）")
            elif state == '死':
                parts.append(f"{day_gan}日主属{day_wx}气，月支{month_zhi}非{day_wx}气得令之月，日主失令，{day_wx}气衰微")
            if month_wx:
                if sheng.get(month_wx) == day_wx:
                    parts.append(f"{month_wx}生{day_wx}")
                elif ke.get(month_wx) == day_wx:
                    parts.append(f"{month_wx}克{day_wx}")
                elif month_wx == day_wx:
                    parts.append("同气相求")
                elif sheng.get(day_wx) == month_wx:
                    parts.append(f"{day_wx}生{month_wx}")
            # 失令但得生扶的补充说明（与主程序 6835-6860 行对齐）
            if state not in ('旺', '相'):
                supports = []
                year_zhi_v = (parts4[0] or '')[1:2]
                day_zhi_v = (parts4[2] or '')[1:2]
                month_gan_v = (parts4[1] or '')[:1]
                year_gan_v = (parts4[0] or '')[:1]
                if zhi_wx.get(day_zhi_v) and (sheng.get(zhi_wx[day_zhi_v]) == day_wx or zhi_wx[day_zhi_v] == day_wx):
                    supports.append(f"日坐{day_zhi_v}（{zhi_wx[day_zhi_v]}气）")
                if zhi_wx.get(year_zhi_v) and (sheng.get(zhi_wx[year_zhi_v]) == day_wx or zhi_wx[year_zhi_v] == day_wx):
                    supports.append(f"年支{year_zhi_v}（{zhi_wx[year_zhi_v]}气）")
                if gan_wx.get(month_gan_v) and (sheng.get(gan_wx[month_gan_v]) == day_wx or gan_wx[month_gan_v] == day_wx):
                    supports.append(f"月干{month_gan_v}（{gan_wx[month_gan_v]}气）")
                if gan_wx.get(year_gan_v) and (sheng.get(gan_wx[year_gan_v]) == day_wx or gan_wx[year_gan_v] == day_wx):
                    supports.append(f"年干{year_gan_v}（{gan_wx[year_gan_v]}气）")
                if supports:
                    try:
                        wang_score = (result.get('score_details') or {}).get('月令详细', {}).get('旺衰得分', 0)
                    except Exception:
                        wang_score = 0
                    tail = "故月令不扣分" if wang_score >= 0 else "稍解失令之势"
                    parts.append("惟" + "、".join(supports) + f"生扶，仍得根气，{tail}")
            return "，".join(parts)
        except Exception:
            return ''

    def show_single_result(self, result):
        """显示单个评分结果"""
        self.result_text.delete(1.0, tk.END)

        # 主程序顶部「评分/等级」直接取原始 result 字段（重算只影响详情段），
        # 此处先留存，避免重算覆盖导致头部与主程序不一致
        _orig_score = result.get('score', 0)
        _orig_level = result.get('level', '未知')

        # ── 推荐时柱重算（与主程序 _inject_best_hour_to_result 同源）──
        # 主程序在详情渲染时会用推荐时柱重算评分，日课评分系统需同步，
        # 否则两窗口时柱/五行/地支关系等全部不一致。
        try:
            _sz_raw = result.get('sizhu', {})
            if isinstance(_sz_raw, dict) and _sz_raw.get('年柱') and _sz_raw.get('日柱'):
                from modules.推荐时柱 import resolve_recommended_hour
                _ev = result.get('event_type', '')
                # 评分器需要「原始出生年月日」形态的事主（owners_detail 的 birth_date
                # 字符串会被误判为缺失 → 触发"女命忌嫁日"等假否决），此处还原
                _owners = result.get('owners_info') or []
                if not _owners:
                    import re as _re
                    _owners = []
                    for _o in (result.get('owners_detail') or []):
                        if not isinstance(_o, dict):
                            continue
                        _m = _re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})时(\d{1,2})分',
                                        str(_o.get('birth_date', '') or ''))
                        if _m:
                            _owners.append({
                                'name': _o.get('name', ''), 'role': _o.get('role', ''),
                                'gender': _o.get('gender', ''),
                                'year': int(_m.group(1)), 'month': int(_m.group(2)),
                                'day': int(_m.group(3)), 'hour': int(_m.group(4)),
                                'minute': int(_m.group(5)),
                            })
                    if not _owners:
                        _owners = result.get('owners_detail') or []
                _shan = result.get('shan_xiang', '') or ''
                _rec = resolve_recommended_hour(_sz_raw, _ev, _owners, _shan)
                if _rec and _rec.get('best_gz'):
                    _best_gz = _rec['best_gz']
                    if _best_gz != _sz_raw.get('时柱', ''):
                        # 构造推荐时柱的 sizhu
                        _new_sz = dict(_sz_raw)
                        _new_sz['时柱'] = _best_gz
                        _new_sz['hour_gan'] = _best_gz[0]
                        _new_sz['hour_zhi'] = _best_gz[1]
                        # 用推荐时柱重算评分
                        from modules.评分器 import calculate_score as _recalc
                        _house = result.get('house_type', '')
                        _new_sr = _recalc(_new_sz, _ev, _owners, _house, _shan)
                        if isinstance(_new_sr, dict):
                            # 用新评分结果覆盖原 result（保留 date/event_type/owners_detail）
                            for _k, _v in _new_sr.items():
                                result[_k] = _v
                            result['sizhu'] = _new_sz
                            result['event_type'] = _ev
                            # 重算五行明细（天干五行/十二长生/纳音/地支关系）
                            # 与主程序渲染前重新生成 _generate_wu_xing_details 对齐，
                            # 否则【五行分析】段会因 details 缺失而退化为空
                            try:
                                from modules.评分器 import Scorer as _RScorer
                                _wd = _RScorer()._generate_wu_xing_details(
                                    _new_sz, _owners)
                                _wxr = result.get('wu_xing_result')
                                if isinstance(_wxr, dict) and isinstance(_wd, dict):
                                    _wxr['details'] = _wd
                            except Exception:
                                pass
        except Exception:
            pass

        # 构建详细结果文本（与主程序 on_result_double_click 逐字对齐）
        # 统一四柱为字符串形式（兼容字典/字符串两种输入）
        _sizhu_raw = result.get('sizhu', '')
        if isinstance(_sizhu_raw, dict):
            _sizhu_str = ' '.join([_sizhu_raw.get('年柱',''), _sizhu_raw.get('月柱',''),
                                    _sizhu_raw.get('日柱',''), _sizhu_raw.get('时柱','')])
        else:
            _sizhu_str = str(_sizhu_raw)
        self._insert_colored_text(f"""
日期：{result.get('date', '')}
农历：{result.get('lunar', '')}
四柱：{_sizhu_str}
评分：{_orig_score} 分
等级：""")

        # 等级评定（如果有星星，用金色显示）
        level = _orig_level
        if '★' in level:
            star_count = level.count('★')
            other_text = level.replace('★', '').strip()
            self._insert_colored_text('★' * star_count, "gold_star")
            if other_text:
                self._insert_colored_text(f" {other_text}")
        else:
            self._insert_colored_text(level)

        # 提取大利月/小利月信息（婚嫁专用）
        daliyue_info = '-'
        event_type = result.get('event_type', '')
        from modules.事项标准 import MARRIAGE_EVENTS
        if result.get('shensha_list') and event_type in MARRIAGE_EVENTS:
            for shensha in result['shensha_list']:
                if isinstance(shensha, dict):
                    shensha_name = shensha.get('name', '')
                    if shensha_name == '大利月':
                        daliyue_info = '大利月'
                        break
                    elif shensha_name == '小利月':
                        daliyue_info = '小利月'
                        break

        # 如果是婚嫁择日，显示大利月/小利月信息
        if event_type in MARRIAGE_EVENTS and daliyue_info != '-':
            # 2026-10-16 第4批 L5：普通月份补括注，与【嫁娶择日分析】口径一致
            _ly_txt = '普通月份（非大利月，无利月加分）' if daliyue_info == '普通月份' else daliyue_info
            self._insert_colored_text(f"\n利月：{_ly_txt}")

        # 插入事主信息标题（与主程序一致）
        self._insert_colored_text("\n\n[事主信息]")
        self._insert_colored_text("\n ----------------------------------------")
        
        # 事主信息（与主程序 on_result_double_click 逐字对齐）
        from modules.事项标准 import MARRIAGE_UI_EVENTS
        from modules.喜用神计算器 import calculate_xishen_yongshen
        owners_detail = result.get('owners_detail', [])
        original_result = result.get('original_result', {})
        if not owners_detail and original_result:
            owners_detail = original_result.get('owners', [])

        if owners_detail:
            for i, owner_info in enumerate(owners_detail[:4], 1):
                if not isinstance(owner_info, dict):
                    self._insert_colored_text(f"\n   {owner_info}")
                    continue
                name = owner_info.get('name', owner_info.get('姓名', f'事主{i}'))
                gender = owner_info.get('gender', owner_info.get('性别', ''))

                if name:
                    self._insert_colored_text(f"\n   事主{i}:{name}")
                    if gender:
                        self._insert_colored_text(f"({gender})")

                    # 解析出生日期
                    birth_date = owner_info.get('birth_date', owner_info.get('出生日期', ''))
                    _bd = None
                    _bh = 12
                    _bm = 0
                    try:
                        if hasattr(birth_date, 'year'):
                            _bd = birth_date
                        elif isinstance(birth_date, str):
                            import re as _re
                            _m = _re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日(?:\s*(\d{1,2})时(?:(\d{1,2})分)?)?', birth_date)
                            if _m:
                                from datetime import date as _date
                                _bd = _date(int(_m.group(1)), int(_m.group(2)), int(_m.group(3)))
                                if _m.group(4):
                                    _bh = int(_m.group(4))
                                if _m.group(5):
                                    _bm = int(_m.group(5))
                    except Exception:
                        _bd = None

                    if not _bd:
                        self._insert_colored_text("\n     未提供出生日期（不参与相主计算）")
                    else:
                        try:
                            from datetime import date
                            birth_date_obj = _bd
                            # 优先用 owner_info 中的 hour/minute，否则从 birth_date 解析
                            hour_val = owner_info.get('hour', _bh)
                            minute_val = owner_info.get('minute', _bm)
                            birth_hour = int(hour_val) if str(hour_val).strip() else _bh
                            birth_minute = int(minute_val) if str(minute_val).strip() else _bm

                            # 用八字排盘计算四柱
                            from modules.八字排盘 import BaZiPanPan
                            panpan = BaZiPanPan(birth_date_obj.year, birth_date_obj.month, birth_date_obj.day,
                                                birth_hour, birth_minute, gender)
                            panpan_result = panpan.get_panpan_result()
                            year_zhu = panpan_result['四柱']['年柱'] if '年柱' in panpan_result['四柱'] else '未知'
                            month_zhu = panpan_result['四柱']['月柱'] if '月柱' in panpan_result['四柱'] else '未知'
                            day_zhu = panpan_result['四柱']['日柱'] if '日柱' in panpan_result['四柱'] else '未知'
                            hour_zhu = panpan_result['四柱']['时柱'] if '时柱' in panpan_result['四柱'] else '未知'
                            sizhu_text = f"{year_zhu} {month_zhu} {day_zhu} {hour_zhu}"

                            # 喜用神
                            sizhu_info = {
                                'year_gan': year_zhu[:1] if year_zhu else '',
                                'year_zhi': year_zhu[1:] if len(year_zhu) > 1 else '',
                                'month_gan': month_zhu[:1] if month_zhu else '',
                                'month_zhi': month_zhu[1:] if len(month_zhu) > 1 else '',
                                'day_gan': day_zhu[:1] if day_zhu else '',
                                'day_zhi': day_zhu[1:] if len(day_zhu) > 1 else '',
                                'hour_gan': hour_zhu[:1] if hour_zhu else '',
                                'hour_zhi': hour_zhu[1:] if len(hour_zhu) > 1 else ''
                            }
                            xishen, yongshen = calculate_xishen_yongshen(sizhu_info)

                            self._insert_colored_text(f"\n     公历:{birth_date_obj}")

                            # 农历
                            try:
                                from modules.高精度农历转换 import HighPrecisionLunar
                                lunar_converter = HighPrecisionLunar()
                                lunar_info = lunar_converter._get_lunar_info_sxtwl(
                                    birth_date_obj.year, birth_date_obj.month, birth_date_obj.day, 12, 0, 0)
                                lunar_str = f"{lunar_info['lunar_year']}年{lunar_info['lunar_month']}月{lunar_info['lunar_day']}日"
                                if lunar_info['is_leap']:
                                    lunar_str = f"{lunar_info['lunar_year']}年闰{lunar_info['lunar_month']}月{lunar_info['lunar_day']}日"
                                self._insert_colored_text(f"\n     农历:{lunar_str}")
                            except Exception:
                                self._insert_colored_text("\n     农历:未知")

                            self._insert_colored_text(f"\n     四柱:{sizhu_text}")

                            # 生肖
                            zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                                         '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
                            year_zhi = year_zhu[1:] if len(year_zhu) > 1 else ''
                            zodiac = zodiac_map.get(year_zhi, '')
                            if zodiac:
                                self._insert_colored_text(f"({zodiac})")

                            self._insert_colored_text(f"\n     喜用神:{xishen}")

                            # 嫁娶女命：夫星/子星/阴胎
                            if event_type in MARRIAGE_UI_EVENTS and gender == '女':
                                try:
                                    from modules.工具函数 import get_fuzi, get_yintai
                                    month_gan = month_zhu[:1] if month_zhu else '甲'
                                    month_zhi = month_zhu[1:] if len(month_zhu) > 1 else '子'
                                    year_gan = year_zhu[:1] if year_zhu else ''
                                    year_zhi_part = year_zhu[1:] if len(year_zhu) > 1 else ''
                                    if year_gan and year_zhi_part:
                                        fuzi_info = get_fuzi(year_gan, year_zhi_part)
                                        fu = fuzi_info.get('fu', '未知')
                                        zi = fuzi_info.get('zi', '未知')
                                        yintai = get_yintai(month_gan, month_zhi)
                                        self._insert_colored_text(f"\n    夫星：{fu}")
                                        self._insert_colored_text(f"\n    子星：{zi}")
                                        self._insert_colored_text(f"\n    阴胎：{yintai}")
                                except Exception:
                                    pass
                            # 嫁娶男命：阳气
                            if event_type in MARRIAGE_UI_EVENTS and gender == '男':
                                try:
                                    from modules.工具函数 import get_yangqi
                                    if month_zhu and len(month_zhu) >= 2:
                                        self._insert_colored_text(f"\n    阳气：{get_yangqi(month_zhu[:1], month_zhu[1:])}")
                                except Exception:
                                    pass
                        except Exception as _q1_err:
                            self._insert_colored_text(f"\n     出生信息解析失败：{_q1_err}")
        else:
            self._insert_colored_text("\n  暂无事主信息")

        # [二十四山方位吉凶] / [出发方向吉凶] 头部段（与主程序 6200-6379 行逐字对齐）
        self._insert_shan_head(result)

        # 评分详情
        self._insert_colored_text("""

【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        score_details = result.get('score_details', {})
        if score_details:
            # 2026-02-05 修正：嫁娶评分路径同步有 '五行评分' 键（即嫁娶评分专用评分）；
            # 若历史数据缺该键则取 '嫁娶评分'，不得回退100错显满分。
            wuxing_score = score_details.get('五行评分', score_details.get('嫁娶评分', 100))
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            total_score = score_details.get('总分', result['score'])
            
            self._insert_colored_text(f"  五行评分：{wuxing_score} 分\n")
            
            # 五行评分详细得分
            wu_xing_result = result.get('wu_xing_result', {})
            score_breakdown = wu_xing_result.get('score_breakdown', {})
            if score_breakdown:
                self._insert_colored_text(f"    ├─ 基础分：{score_breakdown.get('基础分', 100)} 分\n")
                shensha_score = score_breakdown.get('神煞得分', 0)
                if shensha_score != 0:
                    self._insert_colored_text(f"    ├─ 神煞得分：{shensha_score:+d} 分\n")
                yi_score = score_breakdown.get('宜事得分', 0)
                if yi_score != 0:
                    self._insert_colored_text(f"    ├─ 宜事得分：+{yi_score} 分\n")
                ji_score = score_breakdown.get('忌事得分', 0)
                if ji_score != 0:
                    self._insert_colored_text(f"    ├─ 忌事得分：{ji_score} 分\n")
                zhangsheng = score_breakdown.get('十二长生得分', 0)
                if zhangsheng != 0:
                    self._insert_colored_text(f"    ├─ 十二长生得分（日干在各柱地支的长生旺衰）：{zhangsheng:+d} 分\n")
                    for _zl in score_breakdown.get('十二长生明细', []):
                        self._insert_colored_text(f"      • {_zl}\n")
                zhizhi = score_breakdown.get('地支关系得分', 0)
                # Q5（2026-10-08 拍板）：地支关系 0 分也展示总分行，
                # 明细存在即列出（如午午午未：六合+24/自刑-24 相抵为 0），
                # 避免审查/用户把"0 分隐藏"误读为时柱关系未计入。
                self._insert_colored_text(f"    ├─ 地支关系得分（四柱六对合计）：{zhizhi:+d} 分\n")
                for _zl in score_breakdown.get('地支关系明细', []):
                    self._insert_colored_text(f"      • {_zl}\n")
                nayin = score_breakdown.get('纳音匹配得分', 0)
                if nayin != 0:
                    self._insert_colored_text(f"    └─ 纳音匹配得分：{nayin:+d} 分\n")
                    for _nl in score_breakdown.get('纳音匹配明细', []):
                        self._insert_colored_text(f"      • {_nl}\n")
                # 2026-09-10 归零透明化（2025-10-28坤山案例）：一票否决把五行评分强制
                # 归零时，在明细末尾明示归零前合计，避免"明细正常、结果归零"无从追溯
                # U1（2026-10-16 第6批拍板）：明细层归零注统一叙述式句式
                # 「五行明细合计 X 分，<机制>归零为 0 分」，机制名保留区分
                # （一票否决 vs 按规则负分），与嫁娶路径 L596x 同构。
                if wu_xing_result.get('he_ge') is False and wuxing_score == 0:
                    _bd_sum = 0
                    for _bk in ('基础分', '神煞得分', '宜事得分', '忌事得分',
                                '十二长生得分', '地支关系得分', '纳音匹配得分'):
                        _bv = score_breakdown.get(_bk, 0)
                        if isinstance(_bv, (int, float)):
                            _bd_sum += int(_bv)
                    self._insert_colored_text(f"    └─ 五行明细合计 {_bd_sum} 分，一票否决归零为 0 分\n")
            
            # 显示婚嫁评分详情（夫星受克等）
            marriage_details = result.get('marriage_details', [])
            if marriage_details:
                for detail_name, detail_score in marriage_details:
                    if detail_score != 0:
                        self._insert_colored_text(f"    {'├─' if score_breakdown else ''}{detail_name}：{detail_score:+d} 分\n")
                    else:
                        # 2026-10-11 B1：0 分＝信息行（本命三煞新郎未犯/新娘对照/
                        # 新郎生年缺失提示），只展示不标分值，不进忌项与神煞加减分。
                        self._insert_colored_text(f"    {'├─' if score_breakdown else ''}{detail_name}\n")
                # 2026-09-17 归零透明化：嫁娶明细合计可能为负（如 -2），算法按 max(0,…)
                # 兜底归零显示 0。此处明示归零前合计，避免"明细加总≠显示分"无法追溯。
                _raw_wx = score_details.get('五行原始分')
                if isinstance(_raw_wx, (int, float)) and _raw_wx < 0 and wuxing_score == 0:
                    _veto_tag = '（本日另触发一票否决，总分归零）' if score_details.get('否决原因') else ''
                    self._insert_colored_text(f"    └─ 五行明细合计 {int(_raw_wx):+d} 分，按规则负分归零为 0 分{_veto_tag}\n")
                # A4b 纳音说明（2026-10-16 第5批T4）：嫁娶评分体系（婚嫁评分算法
                # 基础60＋利月/神煞/合局）不含纳音匹配分项，纳音行仅存在于正五行
                # 路径（12 事项）。此处补一行说明，防审查把跨路径差异误读为渲染
                # 缺陷（属 #2 两套评分架构差异，算法变更归该议题，本批不动分值）。
                _mrx_prefix = '├─' if score_breakdown else ''
                self._insert_colored_text(f"    {_mrx_prefix}纳音匹配：嫁娶评分体系不含此分项，属评分架构差异\n")
            
            self._insert_colored_text(f"  月令得分：{yueling_score:+d} 分\n")
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                # 2026-10-16 第4批 L1：旺衰/支支得分补依据文案（取分口径来自评分器，纯展示拼接）
                _ws_note = yueling_detail.get('旺衰依据', '')
                _zz_note = yueling_detail.get('支支依据', '')
                self._insert_colored_text(f"    ├─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分{('（' + _ws_note + '）') if _ws_note else ''}\n")
                self._insert_colored_text(f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分{('（' + _zz_note + '）') if _zz_note else ''}\n")
            
            self._insert_colored_text(f"  喜用神得分：{xishen_score:+d} 分\n")
            
            # 生肖相主得分
            xiangzhu_score = score_details.get('相主得分', 0)
            xiangzhu_details = score_details.get('相主详情', [])
            if xiangzhu_score != 0 or xiangzhu_details:
                self._insert_colored_text(f"  生肖相主得分：{xiangzhu_score:+d} 分\n")
                for detail_item in xiangzhu_details:
                    self._insert_colored_text(f"    • {detail_item}\n")
            
            # 事主匹配得分（喜用神匹配明细）
            owner_matches = score_details.get('事主匹配', [])
            if owner_matches:
                self._insert_colored_text(f"  事主匹配（喜用神）：\n")
                for m in owner_matches:
                    if isinstance(m, dict):
                        name = m.get('name') or m.get('owner') or m.get('姓名', '事主')
                        # 2026-10-16 第4批 L2：渲染 details 明细（带分值），空则回退旧 remark 通道
                        _dets = m.get('details') or []
                        rmk = '，'.join(_dets) if _dets else (m.get('remark') or m.get('说明') or m.get('match_detail', ''))
                        sc  = m.get('score', m.get('得分', 0))
                        if sc or rmk:
                            _wt = m.get('weight', 1.0)
                            _wtag = '（辅·半权重）' if isinstance(_wt, (int, float)) and _wt < 1.0 else ''
                            self._insert_colored_text(f"    • {name}{_wtag}：（{sc:+d}分）{rmk}\n")
                    else:
                        self._insert_colored_text(f"    • {m}\n")
            
            has_hd_key = '黄道得分' in score_details
            if has_hd_key:
                self._insert_colored_text(f"  黄道得分：{huangdao_score:+d} 分\n")
            else:
                # 2026-02-26 校对：嫁娶路径黄道得分已并入五行评分（无'黄道得分'键），
                # 如实说明而非显示误导性的"+0 分"（口径同主程序详情页）
                self._insert_colored_text("  黄道得分：已并入五行评分（大黄道/小黄道明细见五行评分项内）\n")
            sun_moon_score = score_details.get('太阳太阴得分', 0) or 0
            # 001 §222/§223（2026-11-08）：与主程序【日课详情】同源——太阳太阴由单行
            # 数字升级为「位置 / 到山到向 / 时辰生效 / 实际加减分」四段式，并追加三段
            # 专业提示。旧版单显"太阳太阴得分：+0"与实际加分（已计入神煞得分）矛盾，
            # 是用户反馈"日课评分详情与日课详情不一致"的根因。
            _sm_detail = score_details.get('太阳太阴明细') or {}
            if not _sm_detail:
                _smi = (result.get('sun_moon_info') or {})
                _sm_detail = (_smi.get('taiyang_taiyin_detail') or {})
            _sm_shan = result.get('shan_xiang', '')
            if not _sm_shan:
                self._insert_colored_text("  【太阳太阴到山到向】\n")
                self._insert_colored_text(
                    "    （本事项未提供山向，日月到山到向不适用；"
                    "相关加分仅山向类事项单轨登记）\n")
            elif _sm_detail:
                self._insert_colored_text("  【太阳太阴到山到向】\n")
                self._insert_colored_text(f"    ☀️ {_sm_detail.get('sun_text', '')}\n")
                self._insert_colored_text(f"    🌙 {_sm_detail.get('moon_text', '')}\n")
                _sm_eff = bool(_sm_detail.get('sun_effective')
                               or _sm_detail.get('moon_effective'))
                self._insert_colored_text(
                    f"    {'✅' if _sm_eff else '⚠️'} 生效判定："
                    f"{_sm_detail.get('effective_text', '')}\n")
                _sm_applied = int(_sm_detail.get('score_applied') or 0)
                if _sm_applied:
                    _sm_items_txt = '、'.join(
                        '%s%+d' % (_i.get('name', ''), int(_i.get('score') or 0))
                        for _i in (_sm_detail.get('score_applied_items') or []))
                    self._insert_colored_text(
                        f"    💰 实际加减分：{_sm_applied:+d} 分"
                        f"（{_sm_items_txt}，已计入神煞得分，此分项不再重复累加）\n")
                else:
                    _sm_hit = bool(_sm_detail.get('sun_to_mountain')
                                   or _sm_detail.get('sun_to_direction')
                                   or _sm_detail.get('moon_to_mountain')
                                   or _sm_detail.get('moon_to_direction'))
                    self._insert_colored_text(
                        "    💰 实际加减分：0 分（时辰不匹配，日月吉力未计入）\n"
                        if _sm_hit else
                        "    💰 实际加减分：0 分（未触发日月到山到向加分）\n")
                self._insert_colored_text(
                    "    📌 权威警示：日月到山到向可化解大部分中低阶凶煞，"
                    "但不制岁破、三煞、五黄等结构性大凶。\n")
            else:
                self._insert_colored_text(
                    f"  太阳太阴得分：{sun_moon_score:+d} 分"
                    "（本日太阳太阴未到山到向）\n")
            # 三段专业提示为常驻区块：即使本日已被岁破/三煞/五黄一票否决，
            # 或日月根本未到山，也照样打印，与主程序详情页保持一致。
            self._insert_colored_text("  【📖 专业提示与禁忌】\n")
            self._insert_colored_text(
                "    ⚠️ 三不赦警示：岁破、三煞、五黄为择日公认的"
                "\u201c三不赦\u201d结构性大凶。即使太阳太阴到山到向，"
                "遇此三煞临山或临向，日月光辉亦难压制，绝不宜用事。\n")
            self._insert_colored_text(
                "    🌙 太阴到向争议：太阴到向存在流派争议。"
                "部分观点认为月建天帝到山为吉，到向形成\u201c冲山\u201d之势反凶；"
                "也有流派认为山向皆可。故非绝对百无禁忌，用事请结合师承。\n")
            self._insert_colored_text(
                "    👑 身份与承受力：《协纪辨方书》指明，太阳到山过于尊贵，"
                "多利国家修造，平民用事可能反招不利。相较之下，太阳到向或"
                "太阴到山到向，对平民更为稳妥。\n")
            # 时柱地支关系得分：分数本已含于五行评分·地支关系得分（四柱六对全局分），
            # 仅拆出时柱参与的三对供追溯，展示但不重复累加（2026-09-10勘正：
            # 旧版加进 raw_total 致"公式114≠总分108"误显"总分调整"）
            hour_rel_score = score_details.get('时柱关系得分', 0) or 0
            hour_rel_details = score_details.get('时柱关系明细', []) or []
            if hour_rel_score or hour_rel_details:
                self._insert_colored_text(f"  时柱地支关系（按时柱归集展示；时柱关系已计入五行评分·地支关系得分，非独立分项）：{hour_rel_score:+d} 分\n")
                for rl in hour_rel_details:
                    self._insert_colored_text(f"    • {rl}\n")
            sansha_penalty = score_details.get('三煞扣分', 0) or 0
            # §201：出行方位轻权重分项（仅出行通道有该键，其余事项恒 0）
            travel_dir_score = score_details.get('出行方位得分', 0) or 0
            # 各分项统一 `or 0`，杜绝 None 进入算术累加
            wuxing_score = wuxing_score or 0
            yueling_score = yueling_score or 0
            xishen_score = xishen_score or 0
            xiangzhu_score = xiangzhu_score or 0
            huangdao_score = huangdao_score or 0
            # 太阳太阴得分（score_details['太阳太阴得分']恒为 0；实际加分已计入
            # 五行评分·神煞得分，详见下方【太阳太阴到山到向】段，故公式行不另列
            # "+0"项，避免与"实际加减分+25"自相矛盾——001 §222/§223 对齐）
            sun_moon_score = sun_moon_score or 0
            # 2026-09-09：时柱关系分已含于五行评分·地支关系得分，公式行不得再加，
            # 否则公式合计≠总分（如 93-5+22-15=95 与总分110不符）。
            raw_total = wuxing_score + yueling_score + xishen_score + xiangzhu_score + huangdao_score + sun_moon_score + travel_dir_score
            _tds_term = f" {travel_dir_score:+d}(出行方位)" if travel_dir_score else ''
            self._insert_colored_text(f"  ─────────────────────────────────\n")
            if not has_hd_key:
                # 公式行不含黄道项（已并入五行评分），避免与"+0"重复列出的误读
                if sansha_penalty:
                    self._insert_colored_text(f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d}{_tds_term} {sansha_penalty:+d}(三煞扣分) = {raw_total + sansha_penalty} 分\n")
                else:
                    self._insert_colored_text(f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d}{_tds_term} = {raw_total} 分\n")
            else:
                if sansha_penalty:
                    # 总分含三煞扣分，公式行如实列出，避免误读为"满分上限"
                    self._insert_colored_text(f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d} {huangdao_score:+d}{_tds_term} {sansha_penalty:+d}(三煞扣分) = {raw_total + sansha_penalty} 分\n")
                else:
                    self._insert_colored_text(f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d} {huangdao_score:+d}{_tds_term} = {raw_total} 分\n")
            # _fc0915：一票否决日公式分项合计仅供追溯、总分强制归零，明示口径
            # 2026-10-16 U2：S2 公式层注统一为叙述式主句式（机制以括注保留）
            result_veto_reasons = result.get('veto_reasons') or []
            if result_veto_reasons:
                self._insert_colored_text(f"  注：总分强制归零（一票否决，明细如实保留，仅供追溯），详见【一票否决】。\n")
            # 2026-02-05：删除"满分上限限制：X → Y"提示行——分项键值已全部修正，
            # （五行评分取嫁娶评分、时柱关系得分注入同步总分分键），公式合计必然等于总分分；
            # 若仍有差额说明是代码缺陷，应在数据层修正，而非用"满分上限"措辞掩盖。
            # 玄空加权封顶/封底透明化（2026-09-10）：总分经加权产生时，
            # 在总分处同步明示原始加权值（与下方玄空飞星块加权公式同源同值）
            _cap_note = ''
            try:
                _fi_cap = result.get('feixing_info') or {}
                if _fi_cap:
                    _zw_cap = score_details.get('正五行总分', total_score)
                    _fx_cap = int(_fi_cap.get('feixing_score', 0) or 0)
                    _wx_cap = float(_zw_cap) * 0.7 + (50 + _fx_cap) * 0.3
                    if _wx_cap > 100 and int(total_score) == 100:
                        _cap_note = (f"  （玄空加权：{_zw_cap}×0.7 + "
                                     f"(50+飞星{_fx_cap:+d}={50+_fx_cap})×0.3 = {_wx_cap:.0f}，"
                                     f"超100，封顶100）\n")
                    elif _wx_cap < 0 and int(total_score) == 0:
                        _cap_note = (f"  （玄空加权：{_zw_cap}×0.7 + "
                                     f"(50+飞星{_fx_cap:+d}={50+_fx_cap})×0.3 = {_wx_cap:.0f}，"
                                     f"低于0，封底0）\n")
            except Exception:
                _cap_note = ''
            _ss_detail = score_details.get('三煞扣分明细') or (result.get('sansha_info') or {}).get('sansha_penalty_detail') or []
            if _ss_detail:
                self._insert_colored_text(f"    扣分构成：{'、'.join(str(_x) for _x in _ss_detail)}\n")
            # 三煞“上管下、下不犯上”反向组合提示（与主程序 6635-6655 行对齐）
            _ssz = result.get('sizhu') if isinstance(result.get('sizhu'), dict) else {}
            _yz = str(_ssz.get('年柱', '') or '')[1:2]
            _mz = str(_ssz.get('月柱', '') or '')[1:2]
            _ssi2 = result.get('sansha_info') if isinstance(result.get('sansha_info'), dict) else {}
            _msf = [] if event_type == '出行' else (_ssi2.get('month_sansha') or [])
            _dsf = [] if event_type == '出行' else (_ssi2.get('day_sansha') or [])
            _rev = []
            if _yz and _yz in _msf:
                _rev.append(f'年柱{_yz}临月柱三煞方（{"".join(_msf)}）')
            if _yz and _yz in _dsf:
                _rev.append(f'年柱{_yz}临日柱三煞方（{"".join(_dsf)}）')
            if _mz and _mz in _dsf:
                _rev.append(f'月柱{_mz}临日柱三煞方（{"".join(_dsf)}）')
            for _rv in _rev:
                self._insert_colored_text(f"    • {_rv}：三煞口径“上管下、下不犯上”，反向不查不扣分\n")
            self._insert_colored_text(f"  总分：{total_score} 分\n")
            if _cap_note:
                self._insert_colored_text(_cap_note)
            # 玄空飞星占位说明（与主程序 6723-6730 行对齐）
            _feixing_info = result.get('feixing_info') or {}
            if not _feixing_info:
                from modules.事项标准 import FEIXING_EVENTS
                if event_type not in FEIXING_EVENTS:
                    self._insert_colored_text("  玄空飞星：本事项非山向类，玄空飞星段不适用\n")
                elif not result.get('shan_xiang', ''):
                    self._insert_colored_text("  玄空飞星：本事项无坐山，玄空飞星段不适用\n")
                elif result.get('veto_reasons'):
                    self._insert_colored_text("  玄空飞星：本课已否决，玄空飞星段不展开\n")
                else:
                    self._insert_colored_text("  玄空飞星：本模式默认不显示玄空飞星段，如需查看请切换至对应模式\n")
        else:
            self._insert_colored_text("  暂无详细得分数据\n")
        
        # 一票否决 / 凶煞门槛（婚嫁大忌/三煞/相主硬门槛/正五行不合格直接❌凶）
        result_veto_reasons = result.get('veto_reasons') or []
        wu_xing = result.get('wu_xing_result') if isinstance(result.get('wu_xing_result'), dict) else {}
        wx_hege_false = bool(wu_xing) and (not wu_xing.get('he_ge', True)) \
            and ('计算错误' not in wu_xing.get('ji_yu', '')) and ('计算异常' not in wu_xing.get('ji_yu', ''))
        if result_veto_reasons or wx_hege_false:
                self._insert_colored_text("""
【⚠️ 一票否决】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                for _vr in result_veto_reasons:
                    self._insert_colored_text(f"  {_vr}\n")
                if wx_hege_false:
                    _jiyu_txt = wu_xing.get('ji_yu', wu_xing.get('reason', '不合格'))
                    if not any(str(_jiyu_txt) in str(_v)
                               for _v in (result.get('veto_reasons') or [])):
                        self._insert_colored_text(f"  正五行门槛未过：{_jiyu_txt}\n")
                # 与主程序对齐：仅有一票否决段时，段后多留一行（主程序 f-string 尾部空行）
                self._insert_colored_text("\n")

        # 月令分析
        self._insert_colored_text("""\n【月令分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        # 从reason中提取月令信息
        reason = result.get('reason', '') or ''
        yueling_info = ''
        # 与主程序 6756-6860 行对齐：月令分析始终由四柱旺相休囚死表现算拼装，
        # 不从 reason 截取片段（reason 中的月令句是简写，会与主程序措辞不一致）
        yueling_info = self._generate_yueling_analysis(result)
        if not yueling_info:
            _m_yl = re.search('月令(?:分析)?[：:]\s*([^；;\n]+)', reason)
            if _m_yl:
                yueling_info = _m_yl.group(1).strip()
        
        if yueling_info:
            self._insert_colored_text(f"  {yueling_info}\n")
        else:
            self._insert_colored_text("  月令分析：详见【综合评语】\n")
        
        self._insert_colored_text("\n")
        
        # 四柱信息
        if result.get('sizhu'):
            sizhu = result['sizhu']
            self._insert_colored_text(f"""【四柱八字】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  年柱: {sizhu['年柱']}    月柱: {sizhu['月柱']}
  日柱: {sizhu['日柱']}    时柱: {sizhu['时柱']}　（系统择定推荐时柱）

  【天干五行】
    年干: {sizhu['年柱'][0]}    月干: {sizhu['月柱'][0]}    日干: {sizhu['日柱'][0]}    时干: {sizhu['时柱'][0]}
  【地支五行】
    年支: {sizhu['年柱'][1]}    月支: {sizhu['月柱'][1]}    日支: {sizhu['日柱'][1]}    时支: {sizhu['时柱'][1]}

  💡 提示：时柱为系统择定的推荐用柱，实际用课请参考下方【十二时辰吉凶】做二次确认
""")
        
        # 五行分析
        if result.get('wu_xing_result'):
            wu_xing = result['wu_xing_result']
            self._insert_colored_text(f"""【五行分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  五行评分: {wu_xing.get('score', 'N/A')} 分
""")
            if wu_xing.get('reason'):
                self._insert_colored_text(f"  五行评语: {wu_xing['reason']}\n")
            if wu_xing.get('details'):
                details = wu_xing['details']
                
                # 1. 天干地支五行
                if details.get('天干五行'):
                    self._insert_colored_text("\n  【天干地支五行】\n")
                    for pillar, info in details['天干五行'].items():
                        self._insert_colored_text(f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n")
                
                # 2. 地支关系（三合、六合、六冲、六害、三刑）
                # 与主程序 6975-6993 行对齐：示例时柱→推荐时柱文案
                _is_mrg = event_type in MARRIAGE_EVENTS
                _hour_suffix = ('（推荐时柱，冲合刑害不计入日课总分，详见十二时辰吉凶）'
                                if _is_mrg else '（推荐时柱，已计入五行评分·地支关系得分，不重复累加）')
                _heju_suffix = ('（合局已计入日课总分；时柱参与助局不另计分，详见十二时辰吉凶）'
                                if _is_mrg else _hour_suffix)
                _dz_rels = []
                for _ln in (details.get('地支关系') or []):
                    if '示例时柱' in _ln:
                        _ln = _ln.replace('（示例时柱，不计分）', _hour_suffix)
                    elif '时柱' in _ln:
                        if _is_mrg and any(_k in _ln for _k in ('三合', '六合', '半合')):
                            _ln = _ln + _heju_suffix
                        else:
                            _ln = _ln + _hour_suffix
                    _dz_rels.append(_ln)
                if _dz_rels:
                    self._insert_colored_text("\n  【地支关系】\n")
                    for relation in _dz_rels:
                        self._insert_colored_text(f"    • {relation}\n")
                    # 合刑并存声明（与主程序 7019-7023 行对齐）
                    if any(any(_k in str(_r) for _k in ('三合', '六合', '半合'))
                           for _r in _dz_rels) and any('刑' in str(_r) for _r in _dz_rels):
                        self._insert_colored_text("    （合刑并存，各自计分，非只取一边）\n")
                else:
                    self._insert_colored_text("\n  【地支关系】\n    无明显合冲刑害关系\n")
                
                # 3. 十二长生
                if details.get('十二长生'):
                    self._insert_colored_text("\n  【十二长生】（日干在各柱地支的长生旺衰，分值计入五行评分）\n")
                    _zs_map = {}
                    for _zl in (score_breakdown.get('十二长生明细') or []):
                        if '：' in str(_zl):
                            _zs_map[str(_zl)[:2]] = str(_zl).split('：', 1)[1]
                    for pillar, state in details['十二长生'].items():
                        _zv = _zs_map.get(pillar, '')
                        self._insert_colored_text(f"    {pillar}: {state}" + (f"（{_zv}）" if _zv else "") + "\n")
                
                # 4. 纳音五行
                if details.get('纳音五行'):
                    self._insert_colored_text("\n  【纳音五行】\n")
                    for pillar, nayin in details['纳音五行'].items():
                        self._insert_colored_text(f"    {pillar}: {nayin}\n")
                
                # 5. 吉神（天德、月德）
                if details.get('吉神') and len(details['吉神']) > 0:
                    self._insert_colored_text("\n  【吉神】\n")
                    for jishen in details['吉神']:
                        self._insert_colored_text(f"    ✓ {jishen}\n")
                else:
                    # 2026-09-08：贵人吉神为空时，若【神煞信息】有加分吉神，
                    # 不再写"无天德月德等吉神"以免与神煞信息矛盾。
                    _has_shensha_ji = any(
                        (isinstance(_s, dict) and _s.get('score', 0) > 0)
                        for _s in (result.get('shensha_list') or [])
                    )
                    if _has_shensha_ji:
                        self._insert_colored_text("\n  【吉神】\n    有吉神（详见神煞信息）\n")
                    else:
                        self._insert_colored_text("\n  【吉神】\n    无天德月德等吉神\n")
                
                # 6. 日主旺衰
                if details.get('日主旺衰'):
                    self._insert_colored_text(f"\n  【日主旺衰】\n    {details['日主旺衰']}\n")
                
                # 7. 五行生克
                if details.get('五行生克') and len(details['五行生克']) > 0:
                    self._insert_colored_text("\n  【五行生克】\n")
                    for relation in details['五行生克']:
                        self._insert_colored_text(f"    • {relation}\n")
            if wu_xing.get('wang_xiang'):
                self._insert_colored_text(f"  旺相分析: {wu_xing['wang_xiang']}\n")
            if wu_xing.get('ke_zhi'):
                self._insert_colored_text(f"  克制关系: {wu_xing['ke_zhi']}\n")
            self._insert_colored_text("\n")

        # 001 §251（2026-11-10 用户指令）：五行偏枯分析（纯展示，不改分）
        # 与主程序日课详情/导出文本/反推详情四处同源共用同一格式函数
        try:
            from modules.评分器 import (build_wuxing_bias_report,
                                        format_wuxing_bias_text)
            _pk_report = (result.get('score_details') or {}).get('五行偏枯分析')
            if not _pk_report and isinstance(result.get('sizhu'), dict):
                _pk_report = build_wuxing_bias_report(result['sizhu'])
            if _pk_report:
                self._insert_colored_text(format_wuxing_bias_text(_pk_report))
        except Exception as _e:
            print('五行偏枯分析渲染失败（不影响详情正文）：%s' % _e)

        # 黄道信息
        if result.get('huangdao_info'):
            huangdao = result['huangdao_info']
            self._insert_colored_text("""【黄道信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            if huangdao.get('da_huang_dao'):
                da_hd = huangdao['da_huang_dao']
                self._insert_colored_text(f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})")
                if da_hd.get('score'): self._insert_colored_text(f"  {da_hd['score']:+d}分")
                self._insert_colored_text("\n")
                if da_hd.get('description'):
                    self._insert_colored_text(f"    说明: {da_hd['description']}\n")
            if huangdao.get('xiao_huang_dao'):
                xiao_hd = huangdao['xiao_huang_dao']
                _xn = xiao_hd.get('name', '')
                _xs = xiao_hd.get('score', 0)
                _xt = xiao_hd.get('type', 'N/A')
                _xd = xiao_hd.get('description', '')
                # _yj0915：嫁娶场景除/危/执虽为吉但忌嫁娶，显示口径与评分详情一致
                from modules.事项标准 import MARRIAGE_EVENTS as _mrg_evts
                if event_type in _mrg_evts and _xn in ('除', '危', '执'):
                    _xs = -5
                    _xt = '凶'
                    _xd = f'{_xn}日忌嫁娶'
                self._insert_colored_text(f"  小黄道: {_xn} ({_xt})")
                if _xs: self._insert_colored_text(f"  {_xs:+d}分")
                self._insert_colored_text("\n")
                if _xd:
                    self._insert_colored_text(f"    说明: {_xd}\n")
            # 注意："时辰黄道"基于示例午时，不计入黄道综合分，
            # 且分值与说明可能误导用户认为推荐示例时，改由下方【十二时辰吉凶】
            # 逐时辰显示大黄道/建除，此处不再展示。
            self._insert_colored_text(f"  黄道等级: {huangdao.get('huang_dao_level', 'N/A')}\n")
            _hd_total = huangdao.get('huang_dao_score', 0)
            # _yj0915：嫁娶场景除/危/执小黄道+5→-5，综合分相应-10
            _xn_for_total = (huangdao.get('xiao_huang_dao') or {}).get('name', '') if isinstance(huangdao.get('xiao_huang_dao'), dict) else ''
            if event_type in _mrg_evts and _xn_for_total in ('除', '危', '执'):
                _hd_total -= 10
            self._insert_colored_text(f"  黄道综合分: {_hd_total:+d} 分\n")
            if huangdao.get('description'):
                self._insert_colored_text(f"  综合说明: {huangdao['description']}\n")
            # 2026-10-02 修8：嫁娶场景黄道等级"大吉"但总等级被降平时，须说明降级原因
            if event_type in _mrg_evts and _xn_for_total in ('除', '危', '执'):
                self._insert_colored_text(
                    "  注：黄道虽大吉，然小黄道执/除/危日忌嫁娶，"
                    "嫁娶场景整体降格，须慎用并择吉时。\n"
                )
            self._insert_colored_text("\n")
        
        # 二十四山方位吉凶段已按主程序口径改为「头部插入」（见 _insert_shan_head），
        # 不再在正文中重复渲染；此处直接进入宜忌信息。
        # 宜忌信息（与主程序同源：口径说明 + marriage_details 负分项并入忌项）
        yi_list = result.get('yi_list', [])
        ji_list = result.get('ji_list', [])
        # 婚嫁路径：评分扣分项（如大黄道凶日、日主较旺耗夫星）同步到"忌"，
        # 与综合评语保持一致（marriage_details 为 (名称, 分值) 列表，负分为避忌项）
        _md_items = result.get('marriage_details') or []
        if isinstance(_md_items, list) and _md_items:
            _ji_base = list(ji_list) if isinstance(ji_list, list) else ([ji_list] if ji_list else [])
            for _d in _md_items:
                try:
                    _nm, _sc = _d[0], _d[1]
                except Exception:
                    continue
                if isinstance(_sc, (int, float)) and _sc < 0 and _nm not in _ji_base:
                    _ji_base.append(_nm)
            ji_list = _ji_base
        if yi_list or ji_list:
            self._insert_colored_text("""【宜忌信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  口径：宜项来自通书黄历/吉神/建除宜等多层；遇冲突时硬门槛优先——
  相主（事主生肖、日柱冲刑）、三煞、山家封禁、建除当日之忌优先于通书宜项，
  通书宜项不覆盖硬性禁忌（硬门槛未犯时方以通书宜项为用）。
""")
            if yi_list:
                yi_items = yi_list if isinstance(yi_list, list) else yi_list.split(', ')
                self._insert_colored_text(f"  宜: {', '.join(yi_items)}\n")
            if ji_list:
                ji_items = ji_list if isinstance(ji_list, list) else ji_list.split(', ')
                self._insert_colored_text(f"  忌: {', '.join(ji_items)}\n")
            self._insert_colored_text("\n")
        
        # 神煞信息
        if result.get('shensha_list'):
            self._insert_colored_text("""【神煞信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            # 按分值排序显示，并分别显示吉神与凶煞
            raw = result['shensha_list']
            sorted_shensha = sorted(raw, key=lambda x: x.get('score', 0) if isinstance(x, dict) else 0, reverse=True)
            ji_shen = []
            xiong_shen = []
            ping_shen = []
            for shensha in sorted_shensha:
                if isinstance(shensha, dict):
                    score = shensha.get('score', 0)
                    if score > 0: ji_shen.append(shensha)
                    elif score < 0: xiong_shen.append(shensha)
                    else: ping_shen.append(shensha)
                else:
                    ping_shen.append(shensha)
            
            if ji_shen:
                self._insert_colored_text("【吉神(加分项)】\n")
                for shensha in ji_shen:
                    if isinstance(shensha, dict):
                        name = shensha.get('name', '')
                        desc = shensha.get('description', '')
                        score = shensha.get('score', 0)
                        self._insert_colored_text(f"  ✓ {name}（+{score}分）: {desc}\n")
                    else:
                        self._insert_colored_text(f"  ✓ {shensha}\n")
            
            if xiong_shen:
                self._insert_colored_text("\n【凶煞(减分项)】\n")
                for shensha in xiong_shen:
                    if isinstance(shensha, dict):
                        name = shensha.get('name', '')
                        desc = shensha.get('description', '')
                        score = shensha.get('score', 0)
                        self._insert_colored_text(f"  ✗ {name}（{score}分）: {desc}\n")
                    else:
                        self._insert_colored_text(f"  ✗ {shensha}\n")
            
            if ping_shen:
                self._insert_colored_text("\n【其他神煞】\n")
                for shensha in ping_shen:
                    if isinstance(shensha, dict):
                        name = shensha.get('name', '')
                        desc = shensha.get('description', '')
                        score = shensha.get('score', 0)
                        self._insert_colored_text(f"  ○ {name}（+0分）: {desc}\n")
                    else:
                        self._insert_colored_text(f"  ○ {shensha}\n")
            # 2026-10-21 口径收口批（001 §153 拍板6）：轻重层待证提示语——
            # 下列神煞分值为软件经验权重（三库无分值原文），弱化绝对参考性。
            from modules.事项标准 import SHENSHA_WEIGHT_PENDING
            _wpend = sorted({sh.get('name') for sh in result.get('shensha_list', [])
                             if isinstance(sh, dict)
                             and sh.get('name') in SHENSHA_WEIGHT_PENDING})
            if _wpend:
                self._insert_colored_text(
                    "  注：%s 的分值为软件经验权重（轻重层待证·典籍无分值原文），"
                    "仅供参考，待轻重层裁断后校准。\n" % '、'.join(_wpend))
            self._insert_colored_text("\n")
        
        # B2 山向年运参考（未计分）（与主程序同源）
        _myref = result.get('mountain_year_ref') or []
        if _myref:
            self._insert_colored_text("""
【山向年运参考（未计分）】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  以下为二十四山年运表的原文提示，仅供参详，不计入评分与忌项：
""")
            for _mr in _myref:
                self._insert_colored_text(f"  • {_mr}\n")

        # 评语（主程序：山向年运参考 → 综合评语 → 修造/嫁娶分析）
        if result.get('reason'):
            self._insert_colored_text(f"""\n【综合评语】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {result['reason']}

""")

        # 二十四山动土方位吉凶（仅限修造相关事件）
        event_type = result.get('event_type', '')
        from modules.事项标准 import CONSTRUCTION_DETAIL_UI_EVENTS as construction_events

        if result.get('sizhu') and event_type in construction_events:
            from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
            # 坐山/主命须在建 checker 之前取到（主程序 7324 行：
            # ConstructionShenShaCheckerExt(zuoshan=..., zhuming=...)），否则十二时辰
            # 表缺「冲/合坐山」项，与主程序不一致
            zuoshan = None
            zhuming = None
            _zx = (result.get('shan_xiang') or '').strip()
            if _zx:
                zuoshan = _zx[0]
            owners_detail = result.get('owners_detail', [])
            if owners_detail and owners_detail[0].get('sizhu'):
                zhuming = owners_detail[0]['sizhu']
            construction_shensha = ConstructionShenShaCheckerExt(zuoshan=zuoshan, zhuming=zhuming)
            try:
                from modules.事项标准 import canonical_event as _canonical_event
                construction_shensha._std_event = _canonical_event(event_type)
            except Exception:
                pass
            lucky_directions = construction_shensha.get_lucky_directions(result['sizhu'])
            
            # 修造专属信息（扶山相主补龙、山家吉凶、时辰吉凶、建除十二神等）
            if event_type in construction_events and result.get('shensha_list'):
                self._insert_colored_text("""【修造择日分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                
                # 从owners_detail中获取事主信息

                if zuoshan:
                    self._insert_colored_text(f"  坐山：{zuoshan}")
                    _xiangshan_list = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                                       '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
                    try:
                        _idx = _xiangshan_list.index(zuoshan)
                        self._insert_colored_text(f"  向方：{_xiangshan_list[(_idx + 12) % 24]}\n")
                    except Exception:
                        self._insert_colored_text("\n")
                if zhuming:
                    self._insert_colored_text(f"  主命：{zhuming}\n")
                
                # 显示神煞分类
                shensha_items = result.get('shensha_list', [])
                fushan_items = []
                xiangzhu_items = []
                shanjia_items = []
                direction_items = []
                hour_items = []
                jianchu_items = []
                other_items = []
                
                for s in shensha_items:
                    # 处理s可能是字符串或字典的情况
                    if isinstance(s, dict):
                        name = s.get('name', '')
                        desc = s.get('description', '')
                        score = s.get('score', 0)
                        tag = f"{name}: {desc}（{score:+.0f}分）"
                    else:
                        # 如果是字符串，直接使用
                        name = str(s)
                        desc = ''
                        score = 0
                        tag = name
                    
                    if '扶山' in name or '相主' in name or '补龙' in name or '冲主' in name or '克山' in name:
                        fushan_items.append(tag)
                    elif '山家' in name or '冲山' in name:
                        shanjia_items.append(tag)
                    elif '方位' in name or '到方' in name:
                        direction_items.append(tag)
                    elif '时' in name:
                        hour_items.append(tag)
                    elif '建除' in name:
                        jianchu_items.append(tag)
                    else:
                        other_items.append(tag)
                
                if fushan_items:
                    self._insert_colored_text("\n  【扶山·相主·补龙】\n")
                    for item in fushan_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if shanjia_items:
                    self._insert_colored_text("\n  【山家吉凶】\n")
                    for item in shanjia_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if direction_items:
                    self._insert_colored_text("\n  【动土方位凶煞】\n")
                    for item in direction_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if hour_items:
                    self._insert_colored_text("\n  【时辰吉凶】\n")
                    for item in hour_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if jianchu_items:
                    self._insert_colored_text("\n  【建除十二神】\n")
                    for item in jianchu_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                self._insert_colored_text("\n")
            
            # 整理方位数据，按方向分组
            direction_groups = {
                '北方': ['壬', '子', '癸'],
                '东北': ['丑', '艮', '寅'],
                '东方': ['甲', '卯', '乙'],
                '东南': ['辰', '巽', '巳'],
                '南方': ['丙', '午', '丁'],
                '西南': ['未', '坤', '申'],
                '西方': ['庚', '酉', '辛'],
                '西北': ['戌', '乾', '亥']
            }
            
            # 创建方位分数映射
            direction_scores = {item['方位']: item['分值'] for item in lucky_directions}
            
            # 与主程序 7416-7456 行逐字对齐
            _direction_map = {d['方位']: d for d in lucky_directions}
            self._insert_colored_text("  【二十四山动土方位吉凶】\n")
            self._insert_colored_text("  （0分=安全可用，负分=犯煞不宜）\n")
            self._insert_colored_text("  注：四柱不犯三煞不代表所有方位安全，动土方位仍需避犯煞方位\n")
            for direction, shan_list in direction_groups.items():
                self._insert_colored_text(f"\n    {direction}：")
                _dir_infos = []
                for shan in shan_list:
                    _d = _direction_map.get(shan, {'分值': 0, '说明': ['无煞']})
                    if _d['分值'] == 0:
                        _dir_infos.append(f"{shan}(0分)")
                    else:
                        _dir_infos.append(f"{shan}({_d['分值']}分:{'、'.join(_d['说明'])})")
                self._insert_colored_text('  '.join(_dir_infos) + '\n')

            # 显示犯煞方位的具体说明
            bad_directions = [item for item in lucky_directions if item['分值'] < 0]
            safe_directions = [item for item in lucky_directions if item['分值'] == 0]

            if safe_directions:
                safe_names = '、'.join([f"{d['方位']}({d['分值']}分)" for d in safe_directions])
                self._insert_colored_text(f"\n  ★ 安全方位（共{len(safe_directions)}个）：{safe_names}\n")

            if bad_directions:
                self._insert_colored_text(f"  ✗ 犯煞方位（共{len(bad_directions)}个）：")
                for d in bad_directions:
                    self._insert_colored_text(f"\n    {d['方位']}（{d['分值']}分）：{'、'.join(d['说明'])}")
                self._insert_colored_text("\n")

            # 十二时辰动土吉凶（不依赖坐山，始终显示）—— 与主程序 7458-7489 行对齐
            _lucky_hours_dt = construction_shensha.get_lucky_hours(result['sizhu'])
            lucky_hours = _lucky_hours_dt  # 供日课校验器 E004/E102 使用（与主程序同名变量）
            _good_hours = [h for h in _lucky_hours_dt if h['分值'] > 0]
            _bad_hours = [h for h in _lucky_hours_dt if h['分值'] < 0]
            self._insert_colored_text("\n  【十二时辰动土吉凶】\n")
            self._insert_colored_text("  （正分=吉时，0分=平，负分=凶时）\n")
            for _zhi in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
                for _h in _lucky_hours_dt:
                    if _h['地支'] == _zhi:
                        if _h['分值'] > 0:
                            self._insert_colored_text(
                                f"    ★ {_h['天干']}{_h['地支']}时 {_h['时辰']}  {_h['分值']:+d}分  [{'、'.join(_h['说明'])}]\n")
                        elif _h['分值'] < 0:
                            self._insert_colored_text(
                                f"    ✗ {_h['天干']}{_h['地支']}时 {_h['时辰']}  {_h['分值']:+d}分  [{'、'.join(_h['说明'])}]\n")
                        else:
                            self._insert_colored_text(f"      {_h['天干']}{_h['地支']}时 {_h['时辰']}  平\n")
                        break
            if _good_hours:
                _good_names = '、'.join([f"{h['天干']}{h['地支']}" for h in _good_hours])
                self._insert_colored_text(f"\n  ★ 吉利时辰（共{len(_good_hours)}个）：{_good_names}\n")
            if _bad_hours:
                _bad_names = '、'.join([f"{h['天干']}{h['地支']}" for h in _bad_hours])
                self._insert_colored_text(f"  ✗ 凶时（共{len(_bad_hours)}个）：{_bad_names}\n")
            self._insert_colored_text("\n")
        
        # B1 山家警告·已制化（与主程序同源）
        _ssi_mit = result.get('sansha_info') if isinstance(result.get('sansha_info'), dict) else {}
        _mit_warnings = _ssi_mit.get('mountain_warnings_mitigated', []) or [] if _ssi_mit else []
        if _mit_warnings:
            self._insert_colored_text("""【山家警告 · 已制化】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  以下凶煞本日原有吉神制化，按制化口径不禁用、不作忌项扣分：
""")
            for _mw in _mit_warnings:
                self._insert_colored_text(f"  • {_mw}\n")
            self._insert_colored_text("\n")

        # B3 嫁娶择日分析（与主程序同源）
        from modules.事项标准 import MARRIAGE_EVENTS
        if event_type in MARRIAGE_EVENTS:
            try:
                from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt

                bride_gan = bride_zhi = groom_gan = groom_zhi = None
                bride_m_gan = bride_m_zhi = groom_m_gan = groom_m_zhi = None
                # 001 §236 B2：时支冲事主日支（夫妻宫）→ 禁用该时辰
                bride_d_zhi = groom_d_zhi = None

                owners_detail = result.get('owners_detail', [])
                for owner in owners_detail:
                    gender = owner.get('gender', '') or owner.get('性别', '')
                    sizhu_str = owner.get('sizhu', '')
                    if not sizhu_str:
                        continue
                    _parts = sizhu_str.split()
                    if len(_parts) < 2:
                        continue
                    _yzhu = _parts[0]
                    _mzhu = _parts[1]
                    _rzhu = _parts[2] if len(_parts) >= 3 else ''
                    if gender == '女':
                        bride_gan = _yzhu[:1] if len(_yzhu) >= 1 else ''
                        bride_zhi = _yzhu[1:] if len(_yzhu) >= 2 else ''
                        bride_m_gan = _mzhu[:1] if len(_mzhu) >= 1 else ''
                        bride_m_zhi = _mzhu[1:] if len(_mzhu) >= 2 else ''
                        bride_d_zhi = _rzhu[1:] if len(_rzhu) >= 2 else None
                    elif gender == '男':
                        groom_gan = _yzhu[:1] if len(_yzhu) >= 1 else ''
                        groom_zhi = _yzhu[1:] if len(_yzhu) >= 2 else ''
                        groom_m_gan = _mzhu[:1] if len(_mzhu) >= 1 else ''
                        groom_m_zhi = _mzhu[1:] if len(_mzhu) >= 2 else ''
                        groom_d_zhi = _rzhu[1:] if len(_rzhu) >= 2 else None

                _sizhu_src = result.get('sizhu', {}) if isinstance(result.get('sizhu'), dict) else {}
                _detail_date = _sizhu_src.get('date') if isinstance(_sizhu_src, dict) else None
                if not hasattr(_detail_date, 'year'):
                    _d_alt = result.get('date')
                    if hasattr(_d_alt, 'year'):
                        _detail_date = _d_alt
                    elif isinstance(_d_alt, str) and len(_d_alt) >= 10:
                        try:
                            from datetime import datetime as _dt
                            _detail_date = _dt.strptime(_d_alt[:10], '%Y-%m-%d').date()
                        except Exception:
                            _detail_date = None
                detail_sizhu = {
                    'date': _detail_date,
                    'year_gan': _sizhu_src.get('年柱', '')[:1] if _sizhu_src.get('年柱') else '',
                    'year_zhi': _sizhu_src.get('年柱', '')[1:] if _sizhu_src.get('年柱') else '',
                    'month_gan': _sizhu_src.get('月柱', '')[:1] if _sizhu_src.get('月柱') else '',
                    'month_zhi': _sizhu_src.get('月柱', '')[1:] if _sizhu_src.get('月柱') else '',
                    'day_gan': _sizhu_src.get('日柱', '')[:1] if _sizhu_src.get('日柱') else '',
                    'day_zhi': _sizhu_src.get('日柱', '')[1:] if _sizhu_src.get('日柱') else '',
                    'hour_gan': _sizhu_src.get('时柱', '')[:1] if _sizhu_src.get('时柱') else '',
                    'hour_zhi': _sizhu_src.get('时柱', '')[1:] if _sizhu_src.get('时柱') else '',
                }

                checker = MarriageShenShaCheckerExt(
                    bride_gan=bride_gan, bride_zhi=bride_zhi,
                    groom_gan=groom_gan, groom_zhi=groom_zhi,
                    bride_month_gan=bride_m_gan, bride_month_zhi=bride_m_zhi,
                    groom_month_gan=groom_m_gan, groom_month_zhi=groom_m_zhi,
                    bride_day_zhi=bride_d_zhi, groom_day_zhi=groom_d_zhi
                )

                self._insert_colored_text("""【嫁娶择日分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                             '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}

                if bride_gan and bride_zhi:
                    bride_zodiac = zodiac_map.get(bride_zhi, '')
                    self._insert_colored_text(f"  新娘：{bride_gan}{bride_zhi}年生")
                    if bride_zodiac:
                        self._insert_colored_text(f"（{bride_zodiac}）")
                    self._insert_colored_text("\n")
                if groom_gan and groom_zhi:
                    groom_zodiac = zodiac_map.get(groom_zhi, '')
                    self._insert_colored_text(f"  新郎：{groom_gan}{groom_zhi}年生")
                    if groom_zodiac:
                        self._insert_colored_text(f"（{groom_zodiac}）")
                    self._insert_colored_text("\n")

                daliyue_info = checker.get_daliyue_info(detail_sizhu)
                self._insert_colored_text(f"\n  【利月分析】\n")
                self._insert_colored_text(f"    大利月：{'、'.join(daliyue_info['大利月']) if daliyue_info['大利月'] else '无'}\n")
                self._insert_colored_text(f"    小利月：{'、'.join(daliyue_info['小利月']) if daliyue_info['小利月'] else '无'}\n")
                self._insert_colored_text(f"    当前月份：{daliyue_info['当前月份状态']}\n")
                _cur_status = daliyue_info.get('当前月份状态', '')
                if '大利月' not in _cur_status and '小利月' not in _cur_status:
                    self._insert_colored_text(f"    说明：当前为非大利月，无加分\n")

                shensha_items = result.get('shensha_list', [])
                jiri_items = []
                xiongri_items = []
                chonghe_items = []
                liyue_items = []

                for s in shensha_items:
                    name = s.get('name', '')
                    _sc = s.get('score', 0)
                    desc = s.get('description', '')
                    tag = f"{name}（{_sc:+.0f}分）: {desc}"
                    if '大利月' in name or '小利月' in name:
                        tag = f"{name}（{_sc:+.0f}分，已计入五行评分）: {desc}"
                        liyue_items.append(tag)
                    elif '日' in name and '吉' in desc:
                        jiri_items.append(tag)
                    elif '日' in name and ('忌' in desc or '凶' in desc or '大忌' in desc):
                        xiongri_items.append(tag)
                    elif '冲' in name or '合' in name:
                        chonghe_items.append(tag)
                    elif '煞' in name or '忌' in name:
                        xiongri_items.append(tag)

                if liyue_items:
                    self._insert_colored_text("\n  【利月神煞】\n")
                    for item in liyue_items:
                        self._insert_colored_text(f"    • {item}\n")
                if jiri_items:
                    self._insert_colored_text("\n  【吉日神煞】\n")
                    for item in jiri_items:
                        self._insert_colored_text(f"    ✓ {item}\n")
                if xiongri_items:
                    self._insert_colored_text("\n  【凶日神煞】\n")
                    for item in xiongri_items:
                        self._insert_colored_text(f"    ✗ {item}\n")
                if chonghe_items:
                    self._insert_colored_text("\n  【冲合关系】\n")
                    for item in chonghe_items:
                        self._insert_colored_text(f"    • {item}\n")

                lucky_hours = checker.get_lucky_hours(detail_sizhu)
                good_hours = [h for h in lucky_hours if h['分值'] > 0 and not h.get('禁用', False)]
                bad_hours = [h for h in lucky_hours if h['分值'] < 0 or h.get('禁用', False)]

                self._insert_colored_text("\n  【十二时辰婚嫁吉凶】\n")
                self._insert_colored_text("  （正分=吉时，0分=平，负分=凶时，禁用=不可用）\n")
                hour_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                for zhi in hour_order:
                    for h in lucky_hours:
                        if h['地支'] == zhi:
                            _raw = list(h.get('说明', []))
                            _has_ribo = any('日破时' in r for r in _raw)
                            _chong_targets = [r for r in _raw if '冲新娘' in r or '冲新郎' in r]
                            if _has_ribo and _chong_targets:
                                _keep = [r for r in _raw if r not in _chong_targets]
                                _suffix = '/'.join(r.split('（')[0] for r in _chong_targets)
                                _merged = []
                                for r in _keep:
                                    if '日破时' in r:
                                        _merged.append(f'日破时/{_suffix}（禁用）')
                                    else:
                                        _merged.append(r)
                                _raw = _merged
                            reasons_str = '、'.join(_raw)
                            if h.get('禁用', False):
                                self._insert_colored_text(f"    ✗ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n")
                            elif h['分值'] > 0:
                                self._insert_colored_text(f"    ★ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n")
                            elif h['分值'] < 0:
                                self._insert_colored_text(f"    ✗ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n")
                            else:
                                self._insert_colored_text(f"      {h['天干']}{h['地支']}时 {h['时辰']}  平\n")
                            break
                if good_hours:
                    good_names = '、'.join([f"{h['天干']}{h['地支']}" for h in good_hours])
                    self._insert_colored_text(f"\n  ★ 吉利时辰（共{len(good_hours)}个）：{good_names}\n")
                if bad_hours:
                    bad_names = '、'.join([f"{h['天干']}{h['地支']}" for h in bad_hours])
                    self._insert_colored_text(f"  ✗ 凶时/禁用（共{len(bad_hours)}个）：{bad_names}\n")
                self._insert_colored_text("\n")
            except Exception as e:
                self._insert_colored_text(f"\n【嫁娶分析】\n  分析出错：{str(e)}\n")

        # B4 通用十二时辰吉凶（与主程序同源；非修造非嫁娶事项）
        from modules.事项标准 import BUILD_SECTION_UI_EVENTS as construction_events
        if event_type not in construction_events and event_type not in MARRIAGE_EVENTS:
            try:
                from modules.推荐时柱 import build_checker as _build_hour_checker
                _dsrc = result.get('sizhu', {}) if isinstance(result.get('sizhu'), dict) else {}
                def _split_gz(_s):
                    return (_s[:1], _s[1:]) if isinstance(_s, str) and len(_s) >= 2 else ('', '')
                _ddate = _dsrc.get('date') if isinstance(_dsrc, dict) else None
                if not hasattr(_ddate, 'year'):
                    _dalt = result.get('date')
                    if hasattr(_dalt, 'year'):
                        _ddate = _dalt
                    elif isinstance(_dalt, str) and len(_dalt) >= 10:
                        try:
                            from datetime import datetime as _dtx
                            _ddate = _dtx.strptime(_dalt[:10], '%Y-%m-%d').date()
                        except Exception:
                            _ddate = None
                _yg, _yz = _split_gz(_dsrc.get('年柱', ''))
                _mg, _mz = _split_gz(_dsrc.get('月柱', ''))
                _dg, _dz = _split_gz(_dsrc.get('日柱', ''))
                _norm = {
                    'date': _ddate,
                    'year_gan': _yg, 'year_zhi': _yz,
                    'month_gan': _mg, 'month_zhi': _mz,
                    'day_gan': _dg, 'day_zhi': _dz,
                }
                _hour_checker, _ = _build_hour_checker(event_type, None, '')
                lucky_hours = _hour_checker.get_lucky_hours(_norm)
                good_hours = [h for h in lucky_hours if h['分值'] > 0 and not h.get('禁用', False)]
                bad_hours = [h for h in lucky_hours if h['分值'] < 0 or h.get('禁用', False)]
                self._insert_colored_text("\n  【十二时辰吉凶】\n")
                self._insert_colored_text("  （正分=吉时，0分=平，负分=凶时，禁用=不可用）\n")
                hour_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                for zhi in hour_order:
                    for h in lucky_hours:
                        if h['地支'] == zhi:
                            reasons_str = '、'.join(h.get('说明', []))
                            if h.get('禁用', False):
                                self._insert_colored_text(f"    ✗ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n")
                            elif h['分值'] > 0:
                                self._insert_colored_text(f"    ★ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n")
                            elif h['分值'] < 0:
                                self._insert_colored_text(f"    ✗ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n")
                            else:
                                self._insert_colored_text(f"      {h['天干']}{h['地支']}时 {h['时辰']}  平\n")
                            break
                if good_hours:
                    good_names = '、'.join([f"{h['天干']}{h['地支']}" for h in good_hours])
                    self._insert_colored_text(f"\n  ★ 吉利时辰（共{len(good_hours)}个）：{good_names}\n")
                if bad_hours:
                    bad_names = '、'.join([f"{h['天干']}{h['地支']}" for h in bad_hours])
                    self._insert_colored_text(f"  ✗ 凶时/禁用（共{len(bad_hours)}个）：{bad_names}\n")
                self._insert_colored_text("  注：四柱中的推荐时柱由系统按日课全局综合择优（四柱五行、地支合冲、\n")
                self._insert_colored_text("事主生肖相合、神煞等整体计分）；本时辰吉凶表仅评单时干支与日柱关系，\n")
                self._insert_colored_text("两套标准不同，故推荐时柱在表中可能为“平”，请以推荐时柱为主、本表供择时参考。\n")
                self._insert_colored_text("\n")
            except Exception as e:
                self._insert_colored_text(f"\n【十二时辰吉凶】\n  分析出错：{str(e)}\n")

        # B5/B6/B7 二十四山分析（分金五行/正体五行）（与主程序同源）
        shan_xiang_val = result.get('shan_xiang', '')
        if shan_xiang_val and event_type != '出行':
            try:
                from modules.二十四山 import ZhengTiWuXingSelectorDB, shan_xiang_to_shan
                selector = ZhengTiWuXingSelectorDB()
                shan_name = shan_xiang_to_shan(shan_xiang_val)
                _sizhu_src = result.get('sizhu')
                if isinstance(_sizhu_src, dict):
                    year_gz = _sizhu_src.get('年柱', '')
                    month_gz = _sizhu_src.get('月柱', '')
                    day_gz = _sizhu_src.get('日柱', '')
                    hour_gz = _sizhu_src.get('时柱', '')
                else:
                    _sz_parts = str(_sizhu_src).split() if _sizhu_src else []
                    year_gz = _sz_parts[0] if len(_sz_parts) > 0 else ''
                    month_gz = _sz_parts[1] if len(_sz_parts) > 1 else ''
                    day_gz = _sz_parts[2] if len(_sz_parts) > 2 else ''
                    hour_gz = _sz_parts[3] if len(_sz_parts) > 3 else ''
                jianxiang = result.get('jian_xiang', '') or ''
                if jianxiang and jianxiang != "正中":
                    result_fengjin = selector.evaluate_with_fengjin(
                        shan_name, jianxiang, year_gz, month_gz, day_gz, hour_gz,
                        use_fengjin_wuxing=True
                    )
                    self._insert_colored_text(f"\n\n【分金五行分析】\n")
                    self._insert_colored_text(f"山向：{shan_xiang_val}（坐山：{shan_name}）\n")
                    self._insert_colored_text(f"兼向：{jianxiang}\n")
                    self._insert_colored_text(f"分金：第{result_fengjin.get('fengjin_index', '?')}分金（{result_fengjin.get('fengjin_ganzhi', '?')}）\n")
                    self._insert_colored_text(f"分金五行：{result_fengjin.get('fengjin_wuxing', '?')}（{result_fengjin.get('nayin_name', '?')}）\n")
                    self._insert_colored_text(f"正体五行：{result_fengjin.get('zhengti_wuxing', '?')}\n")
                    self._insert_colored_text(f"等级：{result_fengjin.get('level', '?')}\n")
                    self._insert_colored_text(f"得分：{result_fengjin.get('score', '?')}\n")
                    if result_fengjin.get('details'):
                        self._insert_colored_text("详情：\n")
                        for d in result_fengjin['details']:
                            self._insert_colored_text(f"  {d}\n")
                else:
                    result_24 = selector.evaluate_by_name(
                        shan_name, year_gz, month_gz, day_gz, hour_gz
                    )
                    if result_24.get('success'):
                        self._insert_colored_text(f"\n\n【正体五行分析】\n")
                        self._insert_colored_text(f"山向：{shan_xiang_val}（坐山：{shan_name}）\n")
                        self._insert_colored_text("兼向：正中（正向）\n")
                        self._insert_colored_text(f"等级：{result_24.get('level', '?')}\n")
                        self._insert_colored_text(f"得分：{result_24.get('score', '?')}\n")
                        if 'summary' in result_24:
                            summary = result_24['summary']
                            self._insert_colored_text(f"坐山得分：{summary.get('mountain_score', 'N/A')}\n")
                    else:
                        self._insert_colored_text(f"\n\n【正体五行分析】\n")
                        self._insert_colored_text(f"山向：{shan_xiang_val}（坐山：{shan_name}）\n")
                        self._insert_colored_text(f"分析失败：{result_24.get('error', '未知错误')}\n")
            except Exception as e:
                self._insert_colored_text(f"\n\n【二十四山分析】\n分析出错：{str(e)}\n")

        # 日课校验器（与主程序同源：lint_lesson + LLM 审查 + ERROR 置顶否决提示）
        try:
            from modules.日课校验器 import lint_lesson
            # rendered_content 只取【评分详情】及之后的内容（与主程序 content 范围一致）
            _full = self.detail_text.get(1.0, tk.END)
            _sp = _full.find('【评分详情】')
            _rendered = _full[_sp:] if _sp >= 0 else _full
            # 提取新娘年支（与主程序 get_bride_year_zhi 同源）
            _bride_yz = None
            for _o in (result.get('owners_detail') or []):
                if isinstance(_o, dict) and _o.get('gender') == '女':
                    _sz = _o.get('sizhu', '')
                    if isinstance(_sz, str) and len(_sz.split()) >= 1:
                        _yz = _sz.split()[0]
                        if len(_yz) >= 2:
                            _bride_yz = _yz[1]
                    break
            _lint = lint_lesson(result, lucky_hours=locals().get('lucky_hours'), rendered_content=_rendered, bride_year_zhi=_bride_yz)
            self._insert_colored_text(_lint.format_text())
            # LLM 语义审查（默认关闭）
            try:
                import os as _os
                _enable_llm = (
                    _os.environ.get('ENABLE_LLM_REVIEW', '').lower() in ('1', 'true', 'yes')
                    and (_os.environ.get('OPENAI_API_KEY') or _os.environ.get('DASHSCOPE_API_KEY'))
                )
                if _enable_llm:
                    from modules.日课校验器 import llm_review as _llm_review
                    _llm_issues = _llm_review(result, _rendered, cache={})
                    if _llm_issues:
                        self._insert_colored_text("\n\n【语义审查（LLM 辅助）】\n")
                        self._insert_colored_text("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                        for _li in _llm_issues:
                            self._insert_colored_text(f"  {_li.rule_id} [{_li.severity}] {_li.message}\n")
                            if _li.suggestion:
                                self._insert_colored_text(f"      建议：{_li.suggestion}\n")
            except Exception:
                pass
            # ERROR 否决提示：插入到【评分详情】段之前（与主程序 content = _warn + content 对齐）
            if _lint.has_error:
                # 主程序 content 开头为 \n\n【评分详情】，否决提示末尾 \n\n 拼接后产生 3 个空行
                _warn = ('⛔ 本报告未通过日课校验（ERROR 项见文末），不应直接交付\n'
                         '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n')
                # 主程序为 content = _warn + "\n\n【评分详情】"，
                # 即否决提示紧贴前一文本插入点（\n\n 在提示之后），此处须插到 \n\n 之前
                _pos = self.detail_text.search('\n\n【评分详情】', '1.0')
                if not _pos:
                    _pos = self.detail_text.search('【评分详情】', '1.0')
                if _pos:
                    self.detail_text.insert(_pos, _warn)
        except Exception as _lint_err:
            self._insert_colored_text(
                '\n\n【日课校验】\n'
                '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                f'  校验器自身执行异常：{type(_lint_err).__name__}: {_lint_err}\n'
                '  （校验通道故障，不影响报告内容，但须排查校验器）')

        # §190/§191 顶层警示（如入宅未填山向）—— 红字块置顶，与主程序对齐
        try:
            _warns = list((result.get('warnings') if isinstance(result, dict) else None) or [])
        except Exception:
            _warns = []
        if _warns:
            _wblock = ('【⚠ 重要警示】\n'
                       + '\n'.join(str(_w) for _w in _warns)
                       + '\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n')
            try:
                self.detail_text.insert("1.0", _wblock)
            except Exception:
                pass

    def _insert_shan_head(self, result):
        """[二十四山方位吉凶] / [出发方向吉凶] 头部段。

        逐字对齐主程序 on_result_double_click 的 6200-6379 行：
        该段在主程序里是用 text.insert 插入到正文【评分详情】之前的，
        不是正文 content 的一部分，因此必须在 show_single_result 的头部显式还原。
        """
        event_type = result.get('event_type', '')
        sansha_info = result.get('sansha_info') or {}
        shan_xiang = result.get('shan_xiang', '') or ''
        _ins = self._insert_colored_text
        from modules.事项标准 import MARRIAGE_EVENTS as _MARRIAGE_EVENTS

        _is_travel_event = (event_type == '出行')
        _show_shan_section = False
        if not _is_travel_event:
            if shan_xiang:
                _show_shan_section = True
            elif sansha_info and event_type not in _MARRIAGE_EVENTS:
                _show_shan_section = True

        if _show_shan_section:
            _ins("\n\n[二十四山方位吉凶]")
            _ins("\n ----------------------------------------")
            if shan_xiang:
                _ins(f"\n   坐山：{shan_xiang}")

            year_sansha = sansha_info.get('year_sansha', [])
            month_sansha = sansha_info.get('month_sansha', [])
            day_sansha = sansha_info.get('day_sansha', [])
            if year_sansha:
                _ins(f"\n   年三煞：{'、'.join(year_sansha)}")
            if month_sansha:
                _ins(f"\n   月三煞：{'、'.join(month_sansha)}")
            if day_sansha:
                _ins(f"\n   日三煞：{'、'.join(day_sansha)}")

            _ins("\n\n   【三煞避忌原则】")
            _ins("\n   ──")
            _ins("\n   三煞为方道神：占山/修方/坐向方忌（「三煞可向不可坐」）")
            _ins("\n   年三煞：论坐山/修方与向首（四柱月日时柱不作判定）")
            _ins("\n   月三煞：论坐山/修方、向首与日、时柱临方（扣分不否决）")
            _ins("\n   日三煞：论坐山/修方、向首与时柱临方（扣分不否决）")

            _ins("\n\n   【三煞检查】")
            _ins("\n   ──")
            _pv = sansha_info.get('sansha_pillar_veto', True)
            _kj = sansha_info.get('sansha_koujing', '')
            if _kj:
                _ins(f"\n   判定口径：{_kj}")

            def _fan_mark(fan, label, is_shan=False):
                if not fan:
                    return
                if is_shan or _pv:
                    _ins(f"\n   ❌ {label}")
                else:
                    _ins(f"\n   ⚠ {label}（临三煞方，扣分不否决）")

            def _fan_mark_xiang(fan, label, penalty):
                if fan:
                    _ins(f"\n   ⚠ {label}（向方，-{penalty}分，不否决）")

            year_fan_shan = sansha_info.get('year_sansha_fan', False)
            year_fan_xiang = sansha_info.get('year_sansha_xiang_fan', False)
            _fan_mark(year_fan_shan, '年三煞犯山向', is_shan=True)
            _fan_mark_xiang(year_fan_xiang, '年三煞犯向首', 10)
            if not year_fan_shan and not year_fan_xiang:
                _ins("\n   ✅ 年三煞不犯")

            month_fan_day = sansha_info.get('month_sansha_day_fan', False)
            month_fan_hour = sansha_info.get('month_sansha_hour_fan', False)
            month_fan_shan = sansha_info.get('month_sansha_fan', False)
            month_fan_xiang = sansha_info.get('month_sansha_xiang_fan', False)
            _fan_mark(month_fan_day, '月三煞犯日柱')
            _fan_mark(month_fan_hour, '月三煞犯时柱')
            _fan_mark(month_fan_shan, '月三煞犯山向', is_shan=True)
            _fan_mark_xiang(month_fan_xiang, '月三煞犯向首', 6)
            if not (month_fan_day or month_fan_hour or month_fan_shan or month_fan_xiang):
                _ins("\n   ✅ 月三煞不犯")

            day_fan_hour = sansha_info.get('day_sansha_hour_fan', False)
            day_fan_shan = sansha_info.get('day_sansha_fan', False)
            day_fan_xiang = sansha_info.get('day_sansha_xiang_fan', False)
            _fan_mark(day_fan_hour, '日三煞犯时柱')
            _fan_mark(day_fan_shan, '日三煞犯山向', is_shan=True)
            _fan_mark_xiang(day_fan_xiang, '日三煞犯向首', 3)
            if not day_fan_hour and not day_fan_shan and not day_fan_xiang:
                _ins("\n   ✅ 日三煞不犯")

            wuhuang_info = sansha_info.get('wuhuang_info') or {}
            if wuhuang_info.get('宫位'):
                _ins("\n\n   【年家五黄】")
                _ins("\n   ──")
                if wuhuang_info.get('入中'):
                    _ins(f"\n   {wuhuang_info.get('年份', '')}年五黄入中宫，无固定凶方")
                else:
                    _ins(f"\n   {wuhuang_info.get('年份', '')}年五黄在{wuhuang_info['宫位']}宫（{wuhuang_info.get('三山', '')}）")
                if shan_xiang:
                    _wu_level = wuhuang_info.get('级别', '')
                    if _wu_level == '凶煞':
                        _ins("\n   ❌ 坐山犯五黄，宜静不宜动，不可动土修造安葬（详见山家封禁）")
                    elif _wu_level == '警告':
                        _ins("\n   ⚠ 兼向犯五黄，须谨慎制化（详见山家警告）")
                    else:
                        _ins("\n   ✅ 坐山不犯五黄")

            sansha_penalty = sansha_info.get('sansha_penalty', 0)
            if sansha_penalty != 0:
                _ins(f"\n\n   三煞总扣分：{sansha_penalty}")
                # 001 §238.13：三煞扣分通道同时承载自刑伏吟(-7/-15)、合局克山
                # (-20/-40)、伐日(-40)、山家封禁(-15) 等不在上方 ⚠ 行内的扣分，
                # 逐项列出「另计项」，否则用户会看到「明细 -19、总额 -26」对不上。
                _sp_det = sansha_info.get('sansha_penalty_detail') or []
                _sp_extra = [str(d) for d in _sp_det
                             if not str(d).startswith(
                                 ('年三煞(', '月三煞(', '日三煞('))]
                if _sp_extra:
                    _ins("\n   另计项（与上方三煞各项合计得出总额）：")
                    for _it in _sp_extra:
                        _ins(f"\n     · {_it}")

            blocked = sansha_info.get('mountain_blocked', False)
            blocked_reasons = sansha_info.get('mountain_block_reasons', [])
            mountain_warnings = sansha_info.get('mountain_warnings', [])
            mountain_jishen = sansha_info.get('mountain_jishen', [])
            mountain_day_type = sansha_info.get('mountain_day_type', sansha_info.get('day_type', ''))

            if blocked or blocked_reasons:
                _ins("\n\n   【⛔ 山家封禁 · 绝对不能用】")
                _ins("\n   ──")
                for r in blocked_reasons:
                    _ins(f"\n   ❌ {r}")
                    if '月冲山' in str(r):
                        _ins("\n        （协纪辨方书：月破山方皆凶，坐山尤凶，造葬皆不可犯）")
            if mountain_warnings:
                _ins("\n\n   【⚠️ 山家警告 · 须谨慎】")
                _ins("\n   ──")
                for w in mountain_warnings:
                    if isinstance(w, dict):
                        msg = w.get('说明') or w.get('msg') or str(w)
                    else:
                        msg = str(w)
                    _ins(f"\n   ⚠ {msg}")
            if mountain_jishen:
                _ins("\n\n   【✅ 山家吉神 · 加分项】")
                _ins("\n   ──")
                for js in mountain_jishen:
                    _ins(f"\n   ✓ {js}")
            if mountain_day_type and mountain_day_type not in ('', '普通日'):
                _ins(f"\n\n   【日期类别】：{mountain_day_type}")

        if _is_travel_event:
            _tdi = result.get('travel_dir_info') or {}
            _ins("\n\n[出发方向吉凶]")
            _ins("\n ----------------------------------------")
            _tdir = _tdi.get('direction') or ''
            if _tdir:
                _ins(f"\n   出发方向：{_tdir}")
                for _it in (_tdi.get('ji_items') or []):
                    _ins(f"\n   ✅ {_it}")
                for _it in (_tdi.get('xiong_items') or []):
                    _ins(f"\n   ⚠ {_it}")
                if not (_tdi.get('ji_items') or _tdi.get('xiong_items')):
                    _ins("\n   本日诸吉凶方位均不在所行方向，方位不计分")
                _tdi_score = _tdi.get('score', 0) or 0
                _ins(f"\n   出行方位得分：{_tdi_score:+d} 分")
                _tdi_map = _tdi.get('details') or {}
                if isinstance(_tdi_map, dict) and _tdi_map:
                    _ins("\n   【本日吉凶方参照】")
                    for _k, _v in _tdi_map.items():
                        _vtxt = _v if _v not in (None, '') else '—（本日无固定方位）'
                        _ins(f"\n   · {_k}：{_vtxt}")
            else:
                _ins("\n   未填出发方向，方位吉凶不参与计分")

    def compare_analysis(self):
        """对比分析 - 对比多个日课的评分结果"""
        # 从Treeview获取日期列表
        dates = []
        for item in self.date_treeview.get_children():
            values = self.date_treeview.item(item, 'values')
            if values:
                dates.append(values[0])
        
        if len(dates) < 2:
            messagebox.showwarning("提示", "请至少添加两个日课进行对比")
            return
        
        # 检查是否所有日课都已评分
        scored_dates = [result['date'] for result in self.scoring_results]
        unscored_dates = [date for date in dates if date not in scored_dates]
        
        # 如果有未评分的日课，自动进行评分
        if unscored_dates:
            # 提示用户将使用当前界面事主信息进行自动评分
            if unscored_dates:
                msg = f"发现有 {len(unscored_dates)} 个日课未评分。\n将使用当前界面输入的事主信息进行自动评分。\n\n如需使用其他事主信息，请先在界面中修改事主资料。"
                messagebox.showinfo("自动评分提示", msg)

            # 自动评分未评分的日课
            event_type = self.event_var.get()
            
            # 获取事主信息
            owners_detail = []
            for info in self.owners_info:
                try:
                    # 注意：self.owners_info 的键名是 solar_year/solar_month/solar_day/hour/minute
                    # （import_results 和 start_scoring 都是按这个命名结构写入的），不能用 info['year']，否则 AttributeError 被吞
                    year_val = info['solar_year'].get() if hasattr(info.get('solar_year'), 'get') else info.get('solar_year', '')
                    month_val = info['solar_month'].get() if hasattr(info.get('solar_month'), 'get') else info.get('solar_month', '')
                    day_val = info['solar_day'].get() if hasattr(info.get('solar_day'), 'get') else info.get('solar_day', '')
                    hour_val = info['hour'].get() if hasattr(info.get('hour'), 'get') else info.get('hour', '12')
                    minute_val = info['minute'].get() if hasattr(info.get('minute'), 'get') else info.get('minute', '0')
                    
                    if not (year_val and month_val and day_val):
                        continue
                    
                    year = int(year_val)
                    month = int(month_val)
                    day = int(day_val)
                    hour = int(hour_val)
                    minute = int(minute_val)
                    
                    target_date = date(year, month, day)
                    sizhu = calculate_sizhu(target_date, hour, minute, longitude=info.get('longitude'))
                    analysis = analyze_sizhu(sizhu)
                    
                    # 姓名（StringVar + 裸字符串双兼容）
                    name = info['name']
                    if hasattr(name, 'get'):
                        name = name.get()
                    
                    owner_detail = {
                        'name': name,
                        'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                        'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                        'xishen': info['xishen_var'].get() if hasattr(info.get('xishen_var'), 'get') else '',
                        'yongshen': info['yongshen_var'].get() if hasattr(info.get('yongshen_var'), 'get') else '',
                        'fu_xing': '',
                        'zi_xing': ''
                    }
                    
                    if event_type == "嫁娶" and info.get('fuzi_var'):
                        fuzi_str = info['fuzi_var'].get() if hasattr(info.get('fuzi_var'), 'get') else ''
                        if '夫星:' in fuzi_str:
                            parts = fuzi_str.split(', ')
                            owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                            if len(parts) > 1:
                                owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                    
                    owners_detail.append(owner_detail)
                except Exception as e:
                    import traceback
                    # 对比分析时事主解析异常也打印到控制台，避免被默默吞掉后整行返回『❌ 计算错误』且看不到原因
                    print(f"[对比分析事主解析异常] {str(e)}\n{traceback.format_exc()}")
                    continue
            
            # 对每个未评分的日课进行评分
            for date_str in unscored_dates:
                try:
                    # 判断是日期还是四柱
                    if len(date_str.split()) == 4 and all(len(zhu) == 2 for zhu in date_str.split()):
                        # 这是四柱格式（如：甲子 乙丑 丙寅 丁卯）
                        parts = date_str.split()
                        sizhu = {
                            '年柱': parts[0],
                            '月柱': parts[1],
                            '日柱': parts[2],
                            '时柱': parts[3],
                            'year_gan': parts[0][0],
                            'year_zhi': parts[0][1],
                            'month_gan': parts[1][0],
                            'month_zhi': parts[1][1],
                            'day_gan': parts[2][0],
                            'day_zhi': parts[2][1],
                            'hour_gan': parts[3][0],
                            'hour_zhi': parts[3][1]
                        }
                        display_date = f"四柱: {date_str}"
                    else:
                        # 这是日期时间格式（如：2025-03-03 14:30）
                        parts = date_str.split()
                        if len(parts) == 2:
                            date_part = parts[0]
                            time_part = parts[1]
                            hour, minute = map(int, time_part.split(':'))
                            score_date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                            sizhu = calculate_sizhu(score_date_obj, hour, minute)
                            display_date = date_str
                        else:
                            # 兼容旧格式（只有日期）
                            score_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            sizhu = calculate_sizhu(score_date_obj, 12, 0)
                            display_date = date_str
                    
                    # 获取宅型和山向（如果是修造、动土、入宅事项）
                    house_type = None
                    shan_xiang = None
                    if event_type in ["修造", "动土", "入宅"]:
                        # 获取宅型
                        house_type = getattr(self, 'house_type', None)
                        if house_type:
                            house_type = house_type.get()
                        # 获取山向
                        shan_xiang = getattr(self, 'shan_xiang', None)
                        if shan_xiang:
                            shan_xiang = shan_xiang.get()
                        # 获取兼向
                        jian_xiang = getattr(self, 'jian_xiang', None)
                        if jian_xiang:
                            jian_xiang = jian_xiang.get()
                    
                    # 使用calculate_score进行评分
                    score_result = calculate_score(sizhu, event_type, owners_detail, house_type, shan_xiang, None, None, None, jian_xiang)
                    result = {
                        'date': display_date,
                        'score': score_result['score'],
                        'level': score_result['level'],
                        'reason': score_result.get('reason', ''),
                        'sizhu': sizhu,
                        'event_type': event_type,
                        'owners_detail': owners_detail,
                        'huangdao_info': score_result.get('huangdao_info', {}),
                        'wu_xing_result': score_result.get('wu_xing_result', {}),
                        'yi_list': score_result.get('yi_list', []),
                        'ji_list': score_result.get('ji_list', []),
                        'shensha_list': score_result.get('shensha_list', []),
                        'score_details': score_result.get('score_details', {}),
                        'sansha_info': score_result.get('sansha_info', {}),
                        'shan_xiang': shan_xiang or ''
                    }
                    
                    # 添加到评分结果
                    self.scoring_results.append(result)
                except Exception as e:
                    continue
        
        # 再次检查评分结果数量
        if not self.scoring_results or len(self.scoring_results) < 2:
            messagebox.showinfo("提示", "请先点击'日课评分'按钮对至少两个日课进行评分，然后再进行对比分析")
            return
        
        # 创建对比分析窗口
        compare_window = tk.Toplevel(self.window)
        compare_window.title("日课对比分析")
        compare_window.geometry("900x700")
        
        # 创建主框架和滚动条
        main_frame = ttk.Frame(compare_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果显示
        result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.CHAR, font=("微软雅黑", 10))
        result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        
        # 按评分排序
        sorted_results = sorted(self.scoring_results, key=lambda x: x['score'], reverse=True)
        
        # 按钮区域
        button_frame = ttk.Frame(compare_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="保存分析", command=lambda: self.save_analysis(result_text, sorted_results, self.event_var.get())).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="关闭窗口", command=compare_window.destroy).pack(side=tk.RIGHT, padx=10)
        
        result_text.insert(tk.END, "=" * 70 + "\n")
        result_text.insert(tk.END, "                    日课对比分析报告\n")
        result_text.insert(tk.END, "=" * 70 + "\n\n")
        
        result_text.insert(tk.END, f"对比日课数量: {len(sorted_results)}\n")
        result_text.insert(tk.END, f"事项类型: {self.event_var.get()}\n")
        result_text.insert(tk.END, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 显示事主信息
        if self.owners_info:
            result_text.insert(tk.END, "【事主信息】\n\n")
            for info in self.owners_info:
                year = info['solar_year'].get()
                month = info['solar_month'].get()
                day = info['solar_day'].get()
                if year and month and day:
                    result_text.insert(tk.END, f"  {info['name']}: ")
                    result_text.insert(tk.END, f"{year}年{month}月{day}日 ")
                    if info.get('sizhu_var'):
                        result_text.insert(tk.END, f"四柱: {info['sizhu_var'].get()} ")
                    if info.get('xishen_var') and info['xishen_var'].get():
                        result_text.insert(tk.END, f"喜神: {info['xishen_var'].get()} ")
                    if info.get('yongshen_var') and info['yongshen_var'].get():
                        result_text.insert(tk.END, f"用神: {info['yongshen_var'].get()} ")
                    if info.get('fuzi_var') and info['fuzi_var'].get():
                        result_text.insert(tk.END, f"{info['fuzi_var'].get()}")
                    result_text.insert(tk.END, "\n")
        
        # 显示排名概览
        result_text.insert(tk.END, "【评分排名概览】\n\n")
        result_text.insert(tk.END, f"{'排名':<6}{'日期/四柱':<25}{'评分':<10}{'等级':<15}\n")
        result_text.insert(tk.END, "-" * 70 + "\n")
        for i, result in enumerate(sorted_results, 1):
            date_display = result['date'][:22] if len(result['date']) > 22 else result['date']
            level = result['level']
            
            # 插入排名、日期、评分
            result_text.insert(tk.END, f"第{i}名  {date_display:<25}{result['score']:<10}")
            
            # 如果有星星，用金色显示
            if '★' in level:
                star_count = level.count('★')
                other_text = level.replace('★', '').strip()
                result_text.insert(tk.END, '★' * star_count, "gold_star")
                if other_text:
                    result_text.insert(tk.END, f" {other_text}")
            else:
                result_text.insert(tk.END, level)
            result_text.insert(tk.END, "\n")
        result_text.insert(tk.END, "\n")
        
        # 显示详细信息
        result_text.insert(tk.END, "=" * 70 + "\n")
        result_text.insert(tk.END, "【详细分析报告】\n")
        result_text.insert(tk.END, "=" * 70 + "\n\n")
        
        for i, result in enumerate(sorted_results, 1):
            result_text.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════╗\n")
            result_text.insert(tk.END, f"║  第 {i} 名{' ' * (58 - len(str(i)))}║\n")
            result_text.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════╝\n\n")
            
            result_text.insert(tk.END, f"【基本信息】\n")
            result_text.insert(tk.END, "-" * 70 + "\n")
            result_text.insert(tk.END, f"  日期: {result['date']}\n")
            result_text.insert(tk.END, f"  综合评分: {result['score']} 分\n")
            result_text.insert(tk.END, f"  等级评定: ")
            
            # 如果有星星，用金色显示
            level = result['level']
            if '★' in level:
                star_count = level.count('★')
                other_text = level.replace('★', '').strip()
                result_text.insert(tk.END, '★' * star_count, "gold_star")
                if other_text:
                    result_text.insert(tk.END, f" {other_text}")
            else:
                result_text.insert(tk.END, level)
            result_text.insert(tk.END, "\n\n")
            
            # 四柱信息
            if result.get('sizhu'):
                sizhu = result['sizhu']
                result_text.insert(tk.END, "【四柱八字】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  年柱: {sizhu['年柱']}    月柱: {sizhu['月柱']}\n")
                result_text.insert(tk.END, f"  日柱: {sizhu['日柱']}    时柱: {sizhu['时柱']}\n\n")
                
                # 天干地支五行
                result_text.insert(tk.END, "  【天干五行】\n")
                result_text.insert(tk.END, f"    年干: {sizhu['年柱'][0]}    月干: {sizhu['月柱'][0]}    日干: {sizhu['日柱'][0]}    时干: {sizhu['时柱'][0]}\n")
                result_text.insert(tk.END, "  【地支五行】\n")
                result_text.insert(tk.END, f"    年支: {sizhu['年柱'][1]}    月支: {sizhu['月柱'][1]}    日支: {sizhu['日柱'][1]}    时支: {sizhu['时柱'][1]}\n\n")
            
            # 五行分析
            if result.get('wu_xing_result'):
                wu_xing = result['wu_xing_result']
                result_text.insert(tk.END, "【五行分析】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  五行评分: {wu_xing.get('score', 'N/A')} 分\n")
                if wu_xing.get('reason'):
                    result_text.insert(tk.END, f"  五行评语: {wu_xing['reason']}\n")
                
                # 显示详细分析
                if wu_xing.get('details'):
                    details = wu_xing['details']
                    
                    # 1. 天干地支五行
                    if details.get('天干五行'):
                        result_text.insert(tk.END, "\n  【天干地支五行】\n")
                        for pillar, info in details['天干五行'].items():
                            result_text.insert(tk.END, f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n")
                    
                    # 2. 地支关系（三合、六合、六冲、六害、三刑）
                    if details.get('地支关系') and len(details['地支关系']) > 0:
                        result_text.insert(tk.END, "\n  【地支关系】\n")
                        for relation in details['地支关系']:
                            result_text.insert(tk.END, f"    • {relation}\n")
                    else:
                        result_text.insert(tk.END, "\n  【地支关系】\n    无明显合冲刑害关系\n")
                    
                    # 3. 十二长生状态
                    if details.get('十二长生') and len(details['十二长生']) > 0:
                        result_text.insert(tk.END, "\n  【十二长生状态】\n")
                        for pillar, state in details['十二长生'].items():
                            result_text.insert(tk.END, f"    {pillar}: {state}\n")
                    
                    # 4. 纳音五行
                    if details.get('纳音五行') and len(details['纳音五行']) > 0:
                        result_text.insert(tk.END, "\n  【纳音五行】\n")
                        for pillar, nayin in details['纳音五行'].items():
                            result_text.insert(tk.END, f"    {pillar}: {nayin}\n")
                    
                    # 5. 吉神（天德、月德）
                    if details.get('吉神') and len(details['吉神']) > 0:
                        result_text.insert(tk.END, "\n  【吉神】\n")
                        for jishen in details['吉神']:
                            result_text.insert(tk.END, f"    ✓ {jishen}\n")
                    
                    # 6. 日主旺衰
                    if details.get('日主旺衰'):
                        result_text.insert(tk.END, "\n  【日主旺衰】\n")
                        result_text.insert(tk.END, f"    {details['日主旺衰']}\n")
                    
                    # 7. 五行生克
                    if details.get('五行生克') and len(details['五行生克']) > 0:
                        result_text.insert(tk.END, "\n  【五行生克关系】\n")
                        for relation in details['五行生克']:
                            result_text.insert(tk.END, f"    • {relation}\n")

                result_text.insert(tk.END, "\n")

            # 001 §251（2026-11-10 用户指令）：五行偏枯分析（纯展示）
            try:
                from modules.评分器 import (build_wuxing_bias_report,
                                            format_wuxing_bias_text)
                _pk_report = (result.get('score_details') or {}).get('五行偏枯分析')
                if not _pk_report and isinstance(result.get('sizhu'), dict):
                    _pk_report = build_wuxing_bias_report(result['sizhu'])
                if _pk_report:
                    result_text.insert(tk.END, format_wuxing_bias_text(_pk_report))
                    result_text.insert(tk.END, "\n")
            except Exception as _e:
                print('五行偏枯分析渲染失败（不影响导出正文）：%s' % _e)

            # 黄道信息
            if result.get('huangdao_info'):
                huangdao = result['huangdao_info']
                result_text.insert(tk.END, "【黄道信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                if huangdao.get('da_huang_dao'):
                    da_hd = huangdao['da_huang_dao']
                    result_text.insert(tk.END, f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})\n")
                    if da_hd.get('description'):
                        result_text.insert(tk.END, f"    说明: {da_hd['description']}\n")
                if huangdao.get('xiao_huang_dao'):
                    xiao_hd = huangdao['xiao_huang_dao']
                    result_text.insert(tk.END, f"  小黄道: {xiao_hd.get('name', 'N/A')} ({xiao_hd.get('type', 'N/A')})\n")
                    if xiao_hd.get('description'):
                        result_text.insert(tk.END, f"    说明: {xiao_hd['description']}\n")
                result_text.insert(tk.END, f"  黄道等级: {huangdao.get('huang_dao_level', 'N/A')}\n\n")
            
            # 宜忌信息
            if result.get('yi_list') or result.get('ji_list'):
                result_text.insert(tk.END, "【宜忌信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                if result.get('yi_list'):
                    yi_items = result['yi_list'] if isinstance(result['yi_list'], list) else result['yi_list'].split(', ')
                    result_text.insert(tk.END, f"  宜: {', '.join(yi_items)}\n")
                if result.get('ji_list'):
                    ji_items = result['ji_list'] if isinstance(result['ji_list'], list) else result['ji_list'].split(', ')
                    result_text.insert(tk.END, f"  忌: {', '.join(ji_items)}\n")
                result_text.insert(tk.END, "\n")
            
            # 神煞信息
            if result.get('shensha_list'):
                result_text.insert(tk.END, "【神煞信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                for shensha in result['shensha_list']:
                    name = shensha.get('name', '')
                    desc = shensha.get('description', '')
                    result_text.insert(tk.END, f"  • {name}: {desc}\n")
                result_text.insert(tk.END, "\n")
            
            # 评语
            if result.get('reason'):
                result_text.insert(tk.END, "【综合评语】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  {result['reason']}\n\n")
            
            # 事主匹配分析
            if result.get('owners_detail'):
                result_text.insert(tk.END, "【事主匹配分析】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                for owner in result['owners_detail']:
                    result_text.insert(tk.END, f"  【{owner.get('name', '事主')}】\n")
                    result_text.insert(tk.END, f"    出生日期: {owner.get('birth_date', 'N/A')}\n")
                    result_text.insert(tk.END, f"    四柱: {owner.get('sizhu', 'N/A')}\n")
                    if owner.get('xishen'):
                        result_text.insert(tk.END, f"    喜神: {owner['xishen']}\n")
                    if owner.get('yongshen'):
                        result_text.insert(tk.END, f"    用神: {owner['yongshen']}\n")
                    if owner.get('fu_xing'):
                        result_text.insert(tk.END, f"    夫星: {owner['fu_xing']}\n")
                    if owner.get('zi_xing'):
                        result_text.insert(tk.END, f"    子星: {owner['zi_xing']}\n")
                    if owner.get('match_result'):
                        result_text.insert(tk.END, f"    匹配结果: {owner['match_result']}\n")
                    result_text.insert(tk.END, "\n")
    
    def export_report(self):
        """导出评分报告"""
        if not self.scoring_results:
            messagebox.showwarning("提示", "没有评分结果可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导出评分报告"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("日课评分报告\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"事项类型: {self.event_var.get()}\n")
                f.write(f"评分日课数量: {len(self.scoring_results)}\n\n")
                
                # 按评分排序
                sorted_results = sorted(self.scoring_results, key=lambda x: x['score'], reverse=True)
                
                for i, result in enumerate(sorted_results, 1):
                    f.write(f"【第 {i} 名】\n")
                    f.write(f"日期: {result['date']}\n")
                    f.write(f"评分: {result['score']} 分\n")
                    f.write(f"等级: {result['level']}\n")
                    
                    if result.get('sizhu'):
                        sizhu = result['sizhu']
                        f.write(f"四柱: {sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}\n")
                    
                    if result.get('reason'):
                        f.write(f"评语: {result['reason']}\n")
                    
                    f.write("-" * 40 + "\n\n")
            
            messagebox.showinfo("成功", f"报告已导出到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def import_file(self):
        """从文件导入日期"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="导入日期文件"
        )
        
        if not file_path:
            return
        
        imported_count = 0
        
        try:
            if file_path.endswith('.json'):
                # 导入JSON格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理主程序导出的格式
                    if isinstance(data, dict) and 'results' in data:
                        for item in data['results']:
                            if isinstance(item, dict) and 'date' in item:
                                date_str = item['date']
                                try:
                                    datetime.strptime(date_str, '%Y-%m-%d')
                                    if date_str not in self.date_list:
                                        self.date_list.append(date_str)
                                        self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                        imported_count += 1
                                except ValueError:
                                    continue
                    # 处理其他格式
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                date_str = item
                            elif isinstance(item, dict) and 'date' in item:
                                date_str = item['date']
                            else:
                                continue
                            
                            try:
                                datetime.strptime(date_str, '%Y-%m-%d')
                                if date_str not in self.date_list:
                                    self.date_list.append(date_str)
                                    self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                    imported_count += 1
                            except ValueError:
                                continue
            else:
                # 导入文本格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 尝试提取日期（格式：YYYY-MM-DD）
                        date_match = re.search(r'日期：(\d{4}-\d{2}-\d{2})', line) or re.search(r'\d{4}-\d{2}-\d{2}', line)
                        if date_match:
                            date_str = date_match.group(1)
                            if date_str not in self.date_list:
                                self.date_list.append(date_str)
                                self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                imported_count += 1
            
            if imported_count > 0:
                messagebox.showinfo("成功", f"成功导入 {imported_count} 个日期")
            else:
                messagebox.showinfo("提示", "没有找到有效的日期")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")
            
    def save_single_analysis(self):
        """保存单个日课分析结果"""
        try:
            # 获取当前显示的内容
            content = self.result_text.get(1.0, tk.END)
            
            if not content.strip():
                messagebox.showwarning("提示", "没有分析结果可保存")
                return
            
            # 弹出文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存日课分析结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
            # 保存为JSON文件
            elif file_path.endswith('.json'):
                # 尝试从当前显示的内容中提取关键信息
                # 这里简化处理，实际项目中可以更详细地解析
                json_data = {
                    'analysis_type': '单个日课分析',
                    'event_type': self.event_var.get(),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'content': content
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_analysis(self, result_text, sorted_results, event_type):
        """保存对比分析结果"""
        try:
            # 获取当前显示的内容
            content = result_text.get(1.0, tk.END)
            
            if not content.strip():
                messagebox.showwarning("提示", "没有分析结果可保存")
                return
            
            # 弹出文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存日课对比分析结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
            # 保存为JSON文件
            elif file_path.endswith('.json'):
                # 构建JSON数据
                json_data = {
                    'analysis_type': '对比分析',
                    'event_type': event_type,
                    'comparison_count': len(sorted_results),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results': [
                        {
                            'date': result['date'],
                            'score': result['score'],
                            'level': result['level'],
                            'reason': result.get('reason', ''),
                            'sizhu': result.get('sizhu', {})
                        }
                        for result in sorted_results
                    ],
                    'content': content
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        日课评分系统使用说明：
        
        1. 选择事项类型：根据需要选择对应的事项类型
        2. 输入日课：可以选择按日期输入或按四柱输入
        3. 填写事主信息：根据事项类型填写相关人员信息
        4. 添加日课：将日课添加到列表中
        5. 日课评分：对当前输入的日课进行评分
        6. 对比分析：对多个日课进行对比分析
        7. 保存分析：保存当前分析结果
        8. 导出报告：导出所有评分结果
        9. 导入文件：从文件导入日期
        10. 保存评分结果：保存当前显示的评分结果
        
        注意事项：
        - 事主信息为可选，可根据实际情况填写
        - 对比分析需要至少两个日课
        - 保存功能支持文本和JSON格式
        """
        messagebox.showinfo("帮助", help_text)
    
    def save_score_result(self):
        """保存当前评分结果"""
        try:
            # 检查是否有评分结果
            if not self.scoring_results:
                messagebox.showwarning("提示", "请先进行日课评分")
                return
            
            # 获取当前显示的结果
            current_text = self.result_text.get(1.0, tk.END).strip()
            if not current_text:
                messagebox.showwarning("提示", "没有评分结果可保存")
                return
            
            # 打开文件保存对话框
            import tkinter.filedialog as filedialog
            
            # 定义文件类型
            file_types = [
                ("文本文件", "*.txt"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
            
            # 获取保存路径
            file_path = filedialog.asksaveasfilename(
                title="保存评分结果",
                filetypes=file_types,
                defaultextension=".txt",
                initialfile=f"日课评分结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if not file_path:
                return  # 用户取消保存
            
            # 根据文件扩展名保存
            if file_path.endswith('.json'):
                # 保存为JSON格式
                # 获取最新的评分结果
                latest_result = self.scoring_results[-1]
                
                json_data = {
                    'score_result': latest_result,
                    'save_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'event_type': self.event_var.get(),
                    'content': current_text
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            else:
                # 保存为文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_text)
                    f.write('\n\n')
                    f.write(f"保存时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"事项类型：{self.event_var.get()}\n")
            
            messagebox.showinfo("成功", f"评分结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")



# 独立运行入口
if __name__ == '__main__':
    app = DayScoreWindow()
    app.run()

# 2026-09-14 补丁指纹 nayin-jishen-zaoxiang：纳音齐备明细/吉神口径/灶向依据
