# -*- coding: utf-8 -*-
"""
================================================================================
电子罗盘模块
================================================================================
提供电子罗盘的完整功能，包括：
- 二十四山罗盘绘制（Canvas）
- 度数与山向的双向转换
- 分金显示与选择
- 与主程序山向同步
- 交互式操作（拖拽、点击选择）

使用方法:
    from modules.电子罗盘 import CompassFrame, CompassWidget
    
    # 在tkinter窗口中使用
    root = tk.Tk()
    compass = CompassFrame(root)
    compass.pack()
    
    # 设置山向
    compass.set_shan_xiang("子山午向")
    
    # 获取当前度数
    degree = compass.get_degree()
    
    # 设置同步回调
    compass.set_sync_callback(on_shan_xiang_changed)
================================================================================
"""

import tkinter as tk
from tkinter import ttk
import math
import sys
import os
from typing import Callable, Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

# 添加项目根目录到路径（支持直接运行）
if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from modules.二十四山 import (
    TwentyFourMountains, TWENTY_FOUR_MOUNTAINS_DATA,
    SHAN_XIANG_24, SHAN_XIANG_24_TO_SHAN, SHAN_TO_SHAN_XIANG,
    shan_xiang_to_shan, shan_to_shan_xiang,
    WuxingRelation, TIANGAN_WUXING, DIZHI_WUXING
)


@dataclass
class MountainDegree:
    """山向度数信息"""
    name: str           # 山名
    start_degree: float # 起始度数
    end_degree: float   # 结束度数
    wuxing: str         # 五行
    center_degree: float # 中心度数
    fengjin_list: List[Dict]  # 分金列表


class CompassConverter:
    """罗盘度数转换器"""
    
    def __init__(self):
        self.mountains_data = {}
        self._init_mountains()
    
    def _init_mountains(self):
        """初始化二十四山度数数据"""
        for data in TWENTY_FOUR_MOUNTAINS_DATA:
            mid, name, mtype, start_deg, end_deg, wuxing, yinyang = data
            
            # 处理跨0度的情况
            if end_deg < start_deg:
                end_deg += 360
            
            center_deg = (start_deg + end_deg) / 2
            if center_deg >= 360:
                center_deg -= 360
            
            # 生成分金列表（每山5个分金，每个3度）
            fengjin_list = []
            for i in range(5):
                fj_start = start_deg + i * 3
                fj_end = fj_start + 3
                fj_center = fj_start + 1.5
                if fj_start >= 360:
                    fj_start -= 360
                if fj_end >= 360:
                    fj_end -= 360
                if fj_center >= 360:
                    fj_center -= 360
                fengjin_list.append({
                    'index': i,
                    'start': fj_start if fj_start < 360 else fj_start - 360,
                    'end': fj_end if fj_end < 360 else fj_end - 360,
                    'center': fj_center,
                    'name': f'{name}山第{i+1}分金'
                })
            
            self.mountains_data[name] = MountainDegree(
                name=name,
                start_degree=start_deg,
                end_degree=end_deg,
                wuxing=wuxing,
                center_degree=center_deg,
                fengjin_list=fengjin_list
            )
    
    def degree_to_mountain(self, degree: float) -> Tuple[str, str, Optional[Dict]]:
        """
        将度数转换为山向
        
        Args:
            degree: 度数（0-360）
            
        Returns:
            (山名, 山向, 分金信息)
        """
        degree = degree % 360
        
        for name, data in self.mountains_data.items():
            start = data.start_degree
            end = data.end_degree
            
            # 处理跨0度的情况
            if end > 360:
                if degree >= start or degree < (end - 360):
                    shan_xiang = shan_to_shan_xiang(name)
                    fengjin = self._get_fengjin(degree, data)
                    return name, shan_xiang, fengjin
            else:
                if start <= degree < end:
                    shan_xiang = shan_to_shan_xiang(name)
                    fengjin = self._get_fengjin(degree, data)
                    return name, shan_xiang, fengjin
        
        return "子", "子山午向", None
    
    def _get_fengjin(self, degree: float, mountain_data: MountainDegree) -> Optional[Dict]:
        """获取分金信息"""
        for fj in mountain_data.fengjin_list:
            start = fj['start']
            end = fj['end']
            
            if end > start:
                if start <= degree < end:
                    return fj
            else:
                if degree >= start or degree < end:
                    return fj
        return None
    
    def get_jianxiang(self, mountain_name: str, degree: float) -> Optional[str]:
        """
        获取兼向信息
        
        Args:
            mountain_name: 主山名
            degree: 当前度数
            
        Returns:
            兼向名称，如"兼丙"或None
        """
        mountain_data = self.mountains_data.get(mountain_name)
        if not mountain_data:
            return None
        
        # 获取当前分金
        fengjin = self._get_fengjin(degree, mountain_data)
        if not fengjin:
            return None
        
        # 根据分金索引判断兼向
        # 分金1-2：兼左（逆时针方向的山）
        # 分金3：正中（不兼）
        # 分金4-5：兼右（顺时针方向的山）
        fj_index = fengjin['index']
        
        # 获取相邻的山
        mountains = list(self.mountains_data.keys())
        current_idx = mountains.index(mountain_name)
        
        if fj_index in [0, 1]:
            # 兼左（逆时针）
            left_idx = (current_idx - 1) % len(mountains)
            jian_shan = mountains[left_idx]
            return f"兼{jian_shan}"
        elif fj_index == 2:
            # 正中，不兼
            return None
        else:  # fj_index in [3, 4]
            # 兼右（顺时针）
            right_idx = (current_idx + 1) % len(mountains)
            jian_shan = mountains[right_idx]
            return f"兼{jian_shan}"
    
    def get_jianxiang_options(self, mountain_name: str) -> List[str]:
        """
        获取某山的所有兼向选项
        
        Args:
            mountain_name: 山名
            
        Returns:
            兼向选项列表
        """
        if mountain_name not in self.mountains_data:
            return []
        
        mountains = list(self.mountains_data.keys())
        current_idx = mountains.index(mountain_name)
        
        # 获取左右相邻的山
        left_idx = (current_idx - 1) % len(mountains)
        right_idx = (current_idx + 1) % len(mountains)
        
        left_shan = mountains[left_idx]
        right_shan = mountains[right_idx]
        
        return [
            f"{mountain_name}山兼{left_shan}",
            f"{mountain_name}山（正中）",
            f"{mountain_name}山兼{right_shan}",
        ]
    
    def jianxiang_to_degree(self, mountain_name: str, jianxiang: str) -> float:
        """
        将兼向转换为度数
        
        Args:
            mountain_name: 主山名
            jianxiang: 兼向，如"兼丙"
            
        Returns:
            度数
        """
        mountain_data = self.mountains_data.get(mountain_name)
        if not mountain_data:
            return 0.0
        
        if not jianxiang or jianxiang == "正中":
            # 正中，取第3分金（中间）
            return mountain_data.fengjin_list[2]['center']
        
        # 解析兼向
        jian_shan = jianxiang.replace("兼", "")
        
        mountains = list(self.mountains_data.keys())
        current_idx = mountains.index(mountain_name)
        left_idx = (current_idx - 1) % len(mountains)
        right_idx = (current_idx + 1) % len(mountains)
        
        if mountains[left_idx] == jian_shan:
            # 兼左，取第1分金
            return mountain_data.fengjin_list[0]['center']
        elif mountains[right_idx] == jian_shan:
            # 兼右，取第5分金
            return mountain_data.fengjin_list[4]['center']
        
        return mountain_data.center_degree
    
    def mountain_to_degree(self, mountain_name: str, fengjin_index: int = None) -> float:
        """
        将山名转换为度数
        
        Args:
            mountain_name: 山名
            fengjin_index: 分金索引（可选，0-4）
            
        Returns:
            度数
        """
        if mountain_name not in self.mountains_data:
            return 0.0
        
        data = self.mountains_data[mountain_name]
        
        if fengjin_index is not None and 0 <= fengjin_index < 5:
            return data.fengjin_list[fengjin_index]['center']
        
        return data.center_degree
    
    def shan_xiang_to_degree(self, shan_xiang: str) -> float:
        """
        将山向转换为度数
        
        Args:
            shan_xiang: 山向，如"子山午向"
            
        Returns:
            度数
        """
        shan = shan_xiang_to_shan(shan_xiang)
        return self.mountain_to_degree(shan)
    
    def get_mountain_info(self, mountain_name: str) -> Optional[MountainDegree]:
        """获取山向详细信息"""
        return self.mountains_data.get(mountain_name)
    
    def get_all_mountains(self) -> List[str]:
        """获取所有山名列表"""
        return list(self.mountains_data.keys())


class CompassWidget(tk.Canvas):
    """罗盘绘制组件"""
    
    # 颜色配置
    COLORS = {
        'background': '#1a1a2e',
        'ring_outer': '#16213e',
        'ring_24shan': '#0f3460',
        'ring_8gua': '#1a1a2e',
        'ring_center': '#0f3460',
        'text_light': '#e8e8e8',
        'text_highlight': '#ff6b6b',
        'highlight': '#e94560',
        'highlight_alpha': 0.3,
        'needle': '#ff6b6b',
        'needle_center': '#ffd700',
        'grid': '#2d4a6e',
        'wuxing_wood': '#4caf50',
        'wuxing_fire': '#f44336',
        'wuxing_earth': '#8d6e63',
        'wuxing_metal': '#ffc107',
        'wuxing_water': '#2196f3',
    }
    
    # 八卦名称（按后天八卦顺序）
    BAGUA_NAMES = ['坎', '艮', '震', '巽', '离', '坤', '兑', '乾']
    
    # 八卦对应的起始度数
    BAGUA_DEGREES = {
        '坎': 352.5, '艮': 37.5, '震': 67.5, '巽': 127.5,
        '离': 172.5, '坤': 217.5, '兑': 262.5, '乾': 307.5
    }
    
    def __init__(self, parent, size: int = 400, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        bg=self.COLORS['background'], highlightthickness=0, **kwargs)
        
        self.size = size
        self.center = size // 2
        self.converter = CompassConverter()
        
        # 当前状态
        self.current_degree = 0.0
        self.current_mountain = "子"
        self.current_shan_xiang = "子山午向"
        self.current_fengjin = None
        
        # 回调函数
        self.on_change_callback: Optional[Callable] = None
        
        # 绑定事件
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<MouseWheel>', self._on_scroll)
        
        # 初始绘制
        self.draw_compass()
    
    def draw_compass(self):
        """绘制完整罗盘"""
        self.delete('all')
        
        # 绘制各层
        self._draw_background()
        self._draw_outer_ring()      # 外圈：360度刻度
        self._draw_24shan_ring()     # 二十四山圈
        self._draw_8gua_ring()       # 八卦圈
        self._draw_fengjin_ring()    # 分金圈
        self._draw_center()          # 天池
        self._draw_needle()          # 指针
        self._draw_highlight()       # 高亮当前山向
    
    def _draw_background(self):
        """绘制背景"""
        self.create_oval(5, 5, self.size-5, self.size-5, 
                        fill=self.COLORS['background'], outline='')
    
    def _draw_outer_ring(self):
        """绘制外圈（360度刻度）"""
        r = self.size // 2 - 10
        
        # 绘制外圈背景
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_outer'], outline=self.COLORS['grid'], width=1)
        
        # 绘制度数刻度
        for i in range(360):
            angle = math.radians(i - 90)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            if i % 15 == 0:
                # 主刻度（每15度）
                inner_r = r - 15
                color = self.COLORS['text_light']
                width = 2
            elif i % 5 == 0:
                # 次刻度（每5度）
                inner_r = r - 8
                color = self.COLORS['grid']
                width = 1
            else:
                # 小刻度
                inner_r = r - 5
                color = self.COLORS['grid']
                width = 1
            
            x1 = self.center + inner_r * cos_a
            y1 = self.center + inner_r * sin_a
            x2 = self.center + r * cos_a
            y2 = self.center + r * sin_a
            
            self.create_line(x1, y1, x2, y2, fill=color, width=width)
        
        # 绘制主要度数标签
        for deg in [0, 90, 180, 270]:
            angle = math.radians(deg - 90)
            x = self.center + (r - 25) * math.cos(angle)
            y = self.center + (r - 25) * math.sin(angle)
            
            labels = {0: '北\n0°', 90: '东\n90°', 180: '南\n180°', 270: '西\n270°'}
            self.create_text(x, y, text=labels[deg], fill=self.COLORS['text_light'],
                           font=('微软雅黑', 8), justify='center')
    
    def _draw_24shan_ring(self):
        """绘制二十四山圈"""
        r = self.size // 2 - 50
        
        # 绘制背景环
        self.create_oval(self.center-r-5, self.center-r-5,
                        self.center+r+5, self.center+r+5,
                        fill=self.COLORS['ring_24shan'], outline=self.COLORS['grid'], width=1)
        
        # 绘制二十四山
        mountains = self.converter.get_all_mountains()
        
        for i, name in enumerate(mountains):
            # 计算角度（从北开始顺时针）
            mountain_data = self.converter.get_mountain_info(name)
            if not mountain_data:
                continue
            
            center_deg = mountain_data.center_degree
            angle = math.radians(center_deg - 90)
            
            # 绘制山名
            x = self.center + (r - 15) * math.cos(angle)
            y = self.center + (r - 15) * math.sin(angle)
            
            # 根据五行设置颜色
            wuxing = mountain_data.wuxing
            color = self.COLORS.get(f'wuxing_{wuxing}', self.COLORS['text_light'])
            
            # 当前选中的山向高亮
            if name == self.current_mountain:
                color = self.COLORS['text_highlight']
            
            self.create_text(x, y, text=name, fill=color,
                           font=('微软雅黑', 10, 'bold'))
            
            # 绘制分隔线
            start_angle = mountain_data.start_degree - 90
            end_angle = mountain_data.end_degree - 90
            
            for deg in [start_angle, end_angle]:
                rad = math.radians(deg)
                x1 = self.center + (r - 30) * math.cos(rad)
                y1 = self.center + (r - 30) * math.sin(rad)
                x2 = self.center + r * math.cos(rad)
                y2 = self.center + r * math.sin(rad)
                self.create_line(x1, y1, x2, y2, fill=self.COLORS['grid'], width=1)
    
    def _draw_8gua_ring(self):
        """绘制八卦圈"""
        r = self.size // 2 - 100
        
        # 绘制背景环
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_8gua'], outline=self.COLORS['grid'], width=1)
        
        # 绘制八卦
        for name, deg in self.BAGUA_DEGREES.items():
            angle = math.radians(deg - 90 + 11.25)  # 偏移到八卦中心
            x = self.center + (r - 10) * math.cos(angle)
            y = self.center + (r - 10) * math.sin(angle)
            
            self.create_text(x, y, text=name, fill=self.COLORS['text_light'],
                           font=('微软雅黑', 9))
    
    def _draw_fengjin_ring(self):
        """绘制分金圈（120分金）"""
        r = self.size // 2 - 130
        
        if r < 30:
            return  # 空间太小不绘制
        
        # 绘制背景环
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_outer'], outline=self.COLORS['grid'], width=1)
        
        # 绘制分金刻度（每山5个分金）
        mountains = self.converter.get_all_mountains()
        for name in mountains:
            mountain_data = self.converter.get_mountain_info(name)
            if not mountain_data:
                continue
            
            for fj in mountain_data.fengjin_list:
                start_deg = fj['start']
                end_deg = fj['end']
                
                # 绘制分金分隔线
                for deg in [start_deg, end_deg]:
                    angle = math.radians(deg - 90)
                    x1 = self.center + (r - 10) * math.cos(angle)
                    y1 = self.center + (r - 10) * math.sin(angle)
                    x2 = self.center + r * math.cos(angle)
                    y2 = self.center + r * math.sin(angle)
                    self.create_line(x1, y1, x2, y2, fill=self.COLORS['grid'], width=1)
    
    def _draw_center(self):
        """绘制天池（中心）"""
        r = 25
        
        # 绘制中心圆
        self.create_oval(self.center-r, self.center-r,
                        self.center+r, self.center+r,
                        fill=self.COLORS['ring_center'], outline=self.COLORS['grid'], width=2)
        
        # 绘制太极图（简化版）
        self.create_arc(self.center-r+5, self.center-r+5,
                       self.center+r-5, self.center+r-5,
                       start=0, extent=180, fill='#ffffff', outline='')
        self.create_arc(self.center-r+5, self.center-r+5,
                       self.center+r-5, self.center+r-5,
                       start=180, extent=180, fill='#000000', outline='')
    
    def _draw_needle(self):
        """绘制指针"""
        # 指针长度
        needle_length = self.size // 2 - 60
        
        # 指针角度（指向当前度数）
        angle = math.radians(self.current_degree - 90)
        
        # 指针尖端坐标
        tip_x = self.center + needle_length * math.cos(angle)
        tip_y = self.center + needle_length * math.sin(angle)
        
        # 指针尾部坐标
        tail_x = self.center - (needle_length * 0.3) * math.cos(angle)
        tail_y = self.center - (needle_length * 0.3) * math.sin(angle)
        
        # 绘制指针主体（红色指向北方）
        self.create_line(tail_x, tail_y, tip_x, tip_y,
                        fill=self.COLORS['needle'], width=3, arrow=tk.LAST)
        
        # 绘制指针中心点
        self.create_oval(self.center-5, self.center-5,
                        self.center+5, self.center+5,
                        fill=self.COLORS['needle_center'], outline='')
    
    def _draw_highlight(self):
        """高亮当前选中的山向"""
        mountain_data = self.converter.get_mountain_info(self.current_mountain)
        if not mountain_data:
            return
        
        # 计算高亮扇形
        start_deg = mountain_data.start_degree
        end_deg = mountain_data.end_degree
        
        # 处理跨0度的情况
        if end_deg > 360:
            # 绘制两段
            self._draw_highlight_arc(start_deg, 360)
            self._draw_highlight_arc(0, end_deg - 360)
        else:
            self._draw_highlight_arc(start_deg, end_deg)
    
    def _draw_highlight_arc(self, start_deg: float, end_deg: float):
        """绘制高亮弧形"""
        r = self.size // 2 - 50
        
        # 使用多边形近似扇形
        points = [self.center, self.center]
        
        for deg in range(int(start_deg), int(end_deg) + 1, 2):
            angle = math.radians(deg - 90)
            x = self.center + r * math.cos(angle)
            y = self.center + r * math.sin(angle)
            points.extend([x, y])
        
        if len(points) > 4:
            # 使用半透明效果（通过stipple模拟）
            self.create_polygon(points, fill=self.COLORS['highlight'],
                              stipple='gray50', outline='')
    
    def _on_click(self, event):
        """点击事件处理"""
        self._update_from_position(event.x, event.y)
    
    def _on_drag(self, event):
        """拖拽事件处理"""
        self._update_from_position(event.x, event.y)
    
    def _on_scroll(self, event):
        """滚轮事件处理"""
        delta = event.delta / 120  # Windows
        if hasattr(event, 'delta'):
            delta = event.delta / 120
        else:
            delta = 1 if event.num == 4 else -1  # Linux/Mac
        
        new_degree = (self.current_degree + delta) % 360
        self.set_degree(new_degree)
    
    def _update_from_position(self, x: int, y: int):
        """根据鼠标位置更新度数"""
        dx = x - self.center
        dy = y - self.center
        
        # 计算角度
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0:
            angle += 360
        
        self.set_degree(angle)
    
    def set_degree(self, degree: float, notify: bool = True):
        """
        设置当前度数
        
        Args:
            degree: 度数（0-360）
            notify: 是否触发回调
        """
        self.current_degree = degree % 360
        
        # 更新山向信息
        self.current_mountain, self.current_shan_xiang, self.current_fengjin = \
            self.converter.degree_to_mountain(self.current_degree)
        
        # 重绘罗盘
        self.draw_compass()
        
        # 触发回调
        if notify and self.on_change_callback:
            self.on_change_callback(self.current_degree, self.current_shan_xiang,
                                   self.current_mountain, self.current_fengjin)
    
    def set_shan_xiang(self, shan_xiang: str, notify: bool = True):
        """
        设置当前山向
        
        Args:
            shan_xiang: 山向，如"子山午向"
            notify: 是否触发回调
        """
        degree = self.converter.shan_xiang_to_degree(shan_xiang)
        self.set_degree(degree, notify)
    
    def set_mountain(self, mountain_name: str, fengjin_index: int = None, notify: bool = True):
        """
        设置当前山
        
        Args:
            mountain_name: 山名
            fengjin_index: 分金索引
            notify: 是否触发回调
        """
        degree = self.converter.mountain_to_degree(mountain_name, fengjin_index)
        self.set_degree(degree, notify)
    
    def get_degree(self) -> float:
        """获取当前度数"""
        return self.current_degree
    
    def get_shan_xiang(self) -> str:
        """获取当前山向"""
        return self.current_shan_xiang
    
    def get_mountain(self) -> str:
        """获取当前山名"""
        return self.current_mountain
    
    def get_fengjin(self) -> Optional[Dict]:
        """获取当前分金"""
        return self.current_fengjin
    
    def set_on_change(self, callback: Callable):
        """设置变化回调函数"""
        self.on_change_callback = callback


class CompassFrame(ttk.Frame):
    """电子罗盘框架（包含罗盘和输入控件）"""
    
    def __init__(self, parent, size: int = 400, sync_callback: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.size = size
        self.sync_callback = sync_callback
        self.converter = CompassConverter()
        
        # 预设列表
        self.presets: List[Dict] = []
        
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        # 罗盘组件
        self.compass = CompassWidget(self, size=self.size)
        self.compass.set_on_change(self._on_compass_change)
        
        # 输入框架
        self.input_frame = ttk.LabelFrame(self, text="坐向输入")
        
        # 度数输入
        ttk.Label(self.input_frame, text="度数：").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.degree_var = tk.StringVar(value="0.00")
        self.degree_entry = ttk.Entry(self.input_frame, textvariable=self.degree_var, width=10)
        self.degree_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.degree_entry.bind('<Return>', self._on_degree_input)
        self.degree_entry.bind('<FocusOut>', self._on_degree_input)
        ttk.Label(self.input_frame, text="°").grid(row=0, column=2, sticky='w')
        
        # 山向选择
        ttk.Label(self.input_frame, text="山向：").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.shan_xiang_var = tk.StringVar()
        self.shan_xiang_combo = ttk.Combobox(self.input_frame, textvariable=self.shan_xiang_var,
                                             values=SHAN_XIANG_24, width=15, state='readonly')
        self.shan_xiang_combo.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.shan_xiang_combo.bind('<<ComboboxSelected>>', self._on_shan_xiang_select)
        
        # 分金选择（方式一：最精确）
        ttk.Label(self.input_frame, text="分金：").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.fengjin_var = tk.StringVar()
        self.fengjin_combo = ttk.Combobox(self.input_frame, textvariable=self.fengjin_var,
                                          width=15, state='readonly')
        self.fengjin_combo.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.fengjin_combo.bind('<<ComboboxSelected>>', self._on_fengjin_select)
        
        # 兼向选择（方式二：最常见）
        ttk.Label(self.input_frame, text="兼向：").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.jianxiang_var = tk.StringVar()
        self.jianxiang_combo = ttk.Combobox(self.input_frame, textvariable=self.jianxiang_var,
                                            width=15, state='readonly')
        self.jianxiang_combo.grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.jianxiang_combo.bind('<<ComboboxSelected>>', self._on_jianxiang_select)
        
        # 手动输入兼向（方式三：最基础）
        ttk.Label(self.input_frame, text="手动：").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.manual_jian_var = tk.StringVar()
        self.manual_jian_entry = ttk.Entry(self.input_frame, textvariable=self.manual_jian_var, width=15)
        self.manual_jian_entry.grid(row=4, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.manual_jian_entry.bind('<Return>', self._on_manual_jian_input)
        self.manual_jian_entry.bind('<FocusOut>', self._on_manual_jian_input)
        
        # 输入模式选择
        ttk.Label(self.input_frame, text="模式：").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        self.input_mode_var = tk.StringVar(value="自动识别")
        self.input_mode_combo = ttk.Combobox(self.input_frame, textvariable=self.input_mode_var,
                                             values=["自动识别", "分金模式", "兼向模式", "手动模式"],
                                             width=12, state='readonly')
        self.input_mode_combo.grid(row=5, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.input_mode_combo.bind('<<ComboboxSelected>>', self._on_input_mode_change)
        
        # 信息显示框架
        self.info_frame = ttk.LabelFrame(self, text="坐山信息")
        
        # 正体五行
        ttk.Label(self.info_frame, text="正体五行：").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.wuxing_label = ttk.Label(self.info_frame, text="水")
        self.wuxing_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # 分金五行（纳音）
        ttk.Label(self.info_frame, text="分金五行：").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.fengjin_wuxing_label = ttk.Label(self.info_frame, text="金（海中金）")
        self.fengjin_wuxing_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # 阴阳
        ttk.Label(self.info_frame, text="阴阳：").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.yinyang_label = ttk.Label(self.info_frame, text="阳")
        self.yinyang_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # 度数范围
        ttk.Label(self.info_frame, text="范围：").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.range_label = ttk.Label(self.info_frame, text="352.5° - 7.5°")
        self.range_label.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # 分金干支
        ttk.Label(self.info_frame, text="分金干支：").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.fengjin_ganzhi_label = ttk.Label(self.info_frame, text="甲子")
        self.fengjin_ganzhi_label.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        
        # 预设管理框架
        self.preset_frame = ttk.LabelFrame(self, text="预设管理")
        
        # 预设列表
        self.preset_listbox = tk.Listbox(self.preset_frame, height=4, width=20)
        self.preset_listbox.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=2)
        self.preset_listbox.bind('<Double-1>', self._on_preset_double_click)
        
        # 预设按钮
        ttk.Button(self.preset_frame, text="添加预设", command=self._add_preset).grid(
            row=1, column=0, sticky='ew', padx=5, pady=2)
        ttk.Button(self.preset_frame, text="删除预设", command=self._delete_preset).grid(
            row=1, column=1, sticky='ew', padx=5, pady=2)
        
        # 同步按钮
        self.sync_button = ttk.Button(self, text="同步到主程序", command=self._sync_to_main)
    
    def _layout_widgets(self):
        """布局控件"""
        self.compass.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        
        self.input_frame.grid(row=0, column=1, sticky='new', padx=10, pady=5)
        self.info_frame.grid(row=1, column=1, sticky='new', padx=10, pady=5)
        self.preset_frame.grid(row=2, column=1, sticky='new', padx=10, pady=5)
        self.sync_button.grid(row=3, column=0, columnspan=2, pady=10)
    
    def _on_compass_change(self, degree: float, shan_xiang: str, mountain: str, fengjin: Dict):
        """罗盘变化回调"""
        # 更新输入控件
        self.degree_var.set(f"{degree:.2f}")
        self.shan_xiang_var.set(shan_xiang)
        
        # 更新分金选项
        self._update_fengjin_options(mountain)
        if fengjin:
            self.fengjin_var.set(fengjin['name'])
        
        # 更新兼向显示
        self._update_jianxiang_display()
        
        # 更新信息显示
        self._update_info_display(mountain)
    
    def _on_degree_input(self, event=None):
        """度数输入处理"""
        try:
            degree = float(self.degree_var.get())
            self.compass.set_degree(degree)
        except ValueError:
            pass
    
    def _on_shan_xiang_select(self, event=None):
        """山向选择处理"""
        shan_xiang = self.shan_xiang_var.get()
        if shan_xiang:
            self.compass.set_shan_xiang(shan_xiang)
    
    def _on_fengjin_select(self, event=None):
        """分金选择处理（方式一：最精确）"""
        fengjin_name = self.fengjin_var.get()
        if fengjin_name:
            # 解析分金索引
            try:
                index = int(fengjin_name.split('第')[1].split('分金')[0]) - 1
                mountain = self.compass.get_mountain()
                self.compass.set_mountain(mountain, index)
                # 更新兼向显示
                self._update_jianxiang_display()
            except (IndexError, ValueError):
                pass
    
    def _on_jianxiang_select(self, event=None):
        """兼向选择处理（方式二：最常见）"""
        jianxiang_full = self.jianxiang_var.get()
        if not jianxiang_full:
            return
        
        # 解析兼向
        if "（正中）" in jianxiang_full:
            mountain = jianxiang_full.replace("山（正中）", "")
            jianxiang = "正中"
        elif "兼" in jianxiang_full:
            parts = jianxiang_full.split("兼")
            mountain = parts[0].replace("山", "")
            jianxiang = f"兼{parts[1]}"
        else:
            return
        
        # 计算度数
        degree = self.converter.jianxiang_to_degree(mountain, jianxiang)
        self.compass.set_degree(degree)
        
        # 更新手动输入框
        self.manual_jian_var.set(jianxiang_full)
    
    def _on_manual_jian_input(self, event=None):
        """手动输入兼向处理（方式三：最基础）"""
        manual_input = self.manual_jian_var.get().strip()
        if not manual_input:
            return
        
        # 解析输入
        # 支持格式："午山兼丙"、"午兼丙"、"兼丙"
        mountain = None
        jianxiang = None
        
        if "兼" in manual_input:
            if "山" in manual_input:
                # 格式："午山兼丙"
                parts = manual_input.split("兼")
                mountain = parts[0].replace("山", "").strip()
                jianxiang = f"兼{parts[1].strip()}"
            else:
                # 格式："午兼丙" 或 "兼丙"
                if manual_input.startswith("兼"):
                    # 只有兼向，使用当前山
                    mountain = self.compass.get_mountain()
                    jianxiang = manual_input
                else:
                    # 格式："午兼丙"
                    parts = manual_input.split("兼")
                    mountain = parts[0].strip()
                    jianxiang = f"兼{parts[1].strip()}"
        else:
            # 没有兼向，可能是纯山名
            mountain = manual_input.replace("山", "").strip()
            jianxiang = "正中"
        
        if mountain:
            degree = self.converter.jianxiang_to_degree(mountain, jianxiang)
            self.compass.set_degree(degree)
            
            # 更新兼向下拉框
            self._update_jianxiang_options(mountain)
    
    def _on_input_mode_change(self, event=None):
        """输入模式改变处理"""
        mode = self.input_mode_var.get()
        
        if mode == "分金模式":
            self.fengjin_combo.config(state='readonly')
            self.jianxiang_combo.config(state='disabled')
            self.manual_jian_entry.config(state='disabled')
        elif mode == "兼向模式":
            self.fengjin_combo.config(state='disabled')
            self.jianxiang_combo.config(state='readonly')
            self.manual_jian_entry.config(state='disabled')
        elif mode == "手动模式":
            self.fengjin_combo.config(state='disabled')
            self.jianxiang_combo.config(state='disabled')
            self.manual_jian_entry.config(state='normal')
        else:  # 自动识别
            self.fengjin_combo.config(state='readonly')
            self.jianxiang_combo.config(state='readonly')
            self.manual_jian_entry.config(state='normal')
    
    def _update_jianxiang_options(self, mountain: str):
        """更新兼向选项"""
        options = self.converter.get_jianxiang_options(mountain)
        self.jianxiang_combo['values'] = options
    
    def _update_jianxiang_display(self):
        """更新兼向显示"""
        mountain = self.compass.get_mountain()
        degree = self.compass.get_degree()
        
        # 获取兼向
        jianxiang = self.converter.get_jianxiang(mountain, degree)
        
        # 更新兼向选项
        self._update_jianxiang_options(mountain)
        
        # 设置当前兼向
        if jianxiang:
            current_text = f"{mountain}山{jianxiang}"
        else:
            current_text = f"{mountain}山（正中）"
        
        self.jianxiang_var.set(current_text)
        self.manual_jian_var.set(current_text)
    
    def _update_fengjin_options(self, mountain: str):
        """更新分金选项"""
        mountain_data = self.converter.get_mountain_info(mountain)
        if mountain_data:
            fengjin_names = [fj['name'] for fj in mountain_data.fengjin_list]
            self.fengjin_combo['values'] = fengjin_names
    
    def _update_info_display(self, mountain: str):
        """更新信息显示"""
        mountain_data = self.converter.get_mountain_info(mountain)
        if mountain_data:
            # 正体五行
            self.wuxing_label.config(text=mountain_data.wuxing)
            
            # 获取阴阳
            for data in TWENTY_FOUR_MOUNTAINS_DATA:
                if data[1] == mountain:
                    yinyang = '阳' if data[6].value == '阳' else '阴'
                    self.yinyang_label.config(text=yinyang)
                    break
            
            # 显示度数范围
            start = mountain_data.start_degree
            end = mountain_data.end_degree
            if end > 360:
                end -= 360
            self.range_label.config(text=f"{start:.1f}° - {end:.1f}°")
            
            # 更新分金五行（纳音）
            fengjin = self.compass.get_fengjin()
            if fengjin:
                from modules.二十四山 import get_fengjin_wuxing, FENGJIN_GANZHI
                fj_index = fengjin['index']
                wuxing, nayin_name = get_fengjin_wuxing(mountain, fj_index)
                self.fengjin_wuxing_label.config(text=f"{wuxing}（{nayin_name}）")
                
                # 显示分金干支
                if mountain in FENGJIN_GANZHI:
                    ganzhi = FENGJIN_GANZHI[mountain][fj_index]
                    self.fengjin_ganzhi_label.config(text=ganzhi)
    
    def _add_preset(self):
        """添加预设"""
        shan_xiang = self.compass.get_shan_xiang()
        degree = self.compass.get_degree()
        
        preset = {
            'name': f"{shan_xiang} ({degree:.1f}°)",
            'shan_xiang': shan_xiang,
            'degree': degree
        }
        
        self.presets.append(preset)
        self.preset_listbox.insert(tk.END, preset['name'])
    
    def _delete_preset(self):
        """删除预设"""
        selection = self.preset_listbox.curselection()
        if selection:
            index = selection[0]
            self.preset_listbox.delete(index)
            del self.presets[index]
    
    def _on_preset_double_click(self, event=None):
        """预设双击调用"""
        selection = self.preset_listbox.curselection()
        if selection:
            index = selection[0]
            preset = self.presets[index]
            self.compass.set_shan_xiang(preset['shan_xiang'])
    
    def _sync_to_main(self):
        """同步到主程序"""
        if self.sync_callback:
            shan_xiang = self.compass.get_shan_xiang()
            degree = self.compass.get_degree()
            mountain = self.compass.get_mountain()
            self.sync_callback(shan_xiang, degree, mountain)
    
    def set_shan_xiang(self, shan_xiang: str):
        """设置山向"""
        self.compass.set_shan_xiang(shan_xiang)
    
    def set_degree(self, degree: float):
        """设置度数"""
        self.compass.set_degree(degree)
    
    def get_shan_xiang(self) -> str:
        """获取当前山向"""
        return self.compass.get_shan_xiang()
    
    def get_degree(self) -> float:
        """获取当前度数"""
        return self.compass.get_degree()
    
    def get_full_shan_xiang(self) -> str:
        """
        获取完整山向（含兼向）
        
        Returns:
            如"午山兼丙"、"子山（正中）"
        """
        mountain = self.compass.get_mountain()
        degree = self.compass.get_degree()
        
        # 获取兼向
        jianxiang = self.converter.get_jianxiang(mountain, degree)
        
        if jianxiang:
            return f"{mountain}山{jianxiang}"
        else:
            return f"{mountain}山（正中）"
    
    def get_jianxiang_info(self) -> Dict[str, Any]:
        """
        获取兼向详细信息
        
        Returns:
            {
                'mountain': 主山,
                'jianxiang': 兼向,
                'degree': 度数,
                'fengjin': 分金信息,
                'full_name': 完整名称
            }
        """
        mountain = self.compass.get_mountain()
        degree = self.compass.get_degree()
        fengjin = self.compass.get_fengjin()
        jianxiang = self.converter.get_jianxiang(mountain, degree)
        
        return {
            'mountain': mountain,
            'jianxiang': jianxiang,
            'degree': degree,
            'fengjin': fengjin,
            'full_name': f"{mountain}山{jianxiang}" if jianxiang else f"{mountain}山（正中）"
        }


class CompassDialog(tk.Toplevel):
    """电子罗盘对话框"""
    
    def __init__(self, parent, initial_shan_xiang: str = None, 
                 on_select: Callable = None, size: int = 450):
        super().__init__(parent)
        
        self.title("电子罗盘")
        self.geometry(f"{size + 250}x{size + 100}")
        self.resizable(False, False)
        
        self.on_select = on_select
        self.selected_shan_xiang = None
        self.selected_degree = None
        
        # 创建罗盘框架
        self.compass_frame = CompassFrame(self, size=size, sync_callback=self._on_sync)
        self.compass_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 设置初始山向
        if initial_shan_xiang:
            self.compass_frame.set_shan_xiang(initial_shan_xiang)
        
        # 确认按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="确定", command=self._on_confirm).pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
    
    def _on_sync(self, shan_xiang: str, degree: float, mountain: str):
        """同步回调"""
        self.selected_shan_xiang = shan_xiang
        self.selected_degree = degree
    
    def _on_confirm(self):
        """确认选择"""
        self.selected_shan_xiang = self.compass_frame.get_shan_xiang()
        self.selected_degree = self.compass_frame.get_degree()
        
        if self.on_select:
            self.on_select(self.selected_shan_xiang, self.selected_degree)
        
        self.destroy()


def show_compass_dialog(parent, initial_shan_xiang: str = None, 
                        on_select: Callable = None) -> Tuple[str, float]:
    """
    显示电子罗盘对话框
    
    Args:
        parent: 父窗口
        initial_shan_xiang: 初始山向
        on_select: 选择回调
        
    Returns:
        (山向, 度数)
    """
    dialog = CompassDialog(parent, initial_shan_xiang, on_select)
    parent.wait_window(dialog)
    return dialog.selected_shan_xiang, dialog.selected_degree


if __name__ == '__main__':
    # 测试代码
    root = tk.Tk()
    root.title("电子罗盘测试")
    root.geometry("700x550")
    
    def on_sync(shan_xiang, degree, mountain):
        print(f"同步: {shan_xiang}, {degree:.2f}°, {mountain}")
    
    compass = CompassFrame(root, size=400, sync_callback=on_sync)
    compass.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 设置初始山向
    compass.set_shan_xiang("子山午向")
    
    root.mainloop()
