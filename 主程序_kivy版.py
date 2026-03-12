# -*- coding: utf-8 -*-
"""
================================================================================
专业级正五行择日软件 - Kivy手机版
================================================================================
【系统概述】
本软件是一款基于传统正五行择日理论的专业择日工具

【版本信息】
版本: 1.0.0 (Kivy手机版)
更新日期: 2026年
作者: 专业择日团队
================================================================================
"""

import os
import sys
from datetime import date, datetime, timedelta

# 设置Kivy环境变量，避免某些平台问题
os.environ['KIVY_TEXT'] = 'pil'
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.config import Config

# 配置Kivy
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '1')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score

# 事项类型列表
EVENT_TYPES = ['嫁娶', '安葬', '修造', '开业', '作灶', '安床', '出行', '入宅', '开市', '动土', '破土']

# 星级等级
STAR_LEVELS = {
    5: '★★★★★ 上吉',
    4: '★★★★ 大吉',
    3: '★★★ 吉',
    2: '★★ 中吉',
    1: '★ 平',
    0: 'X 凶'
}


class ZeriScreen(Screen):
    """择日主界面"""
    
    def __init__(self, **kwargs):
        super(ZeriScreen, self).__init__(**kwargs)
        self.results = []
        self.owners_info = []
        self.create_ui()
    
    def create_ui(self):
        """创建用户界面"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 标题
        title_label = Label(
            text='Zeri App',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            bold=True,
            color=(0.2, 0.4, 0.8, 1)
        )
        main_layout.add_widget(title_label)
        
        # 滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # 事项选择
        content_layout.add_widget(self.create_event_selection())
        
        # 日期范围设置
        content_layout.add_widget(self.create_date_range())
        
        # 事主信息
        content_layout.add_widget(self.create_owner_info())
        
        # 操作按钮
        content_layout.add_widget(self.create_action_buttons())
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        # 结果区域
        self.result_label = Label(
            text='Click "Start" to view results',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(150),
            halign='left',
            valign='top',
            text_size=(Window.width - dp(40), None),
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(self.result_label)
        
        self.add_widget(main_layout)
    
    def create_event_selection(self):
        """创建事项选择区域"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70), spacing=dp(5))
        
        label = Label(
            text='Select Event Type:',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(0, 0, 0, 1)
        )
        layout.add_widget(label)
        
        self.event_spinner = Spinner(
            text='Marry',
            values=['Marry', 'Burial', 'Build', 'Open', 'Cook', 'Bed', 'Travel', 'Move', 'Market', 'Dig', 'Break'],
            size_hint=(1, None),
            height=dp(35),
            font_size=dp(14)
        )
        layout.add_widget(self.event_spinner)
        
        return layout
    
    def create_date_range(self):
        """创建日期范围设置区域"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(5))
        
        label = Label(
            text='Date Range (YYYY-MM-DD):',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(0, 0, 0, 1)
        )
        layout.add_widget(label)
        
        # 开始日期
        start_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        start_label = Label(text='Start:', font_size=dp(12), size_hint_x=None, width=dp(50), color=(0, 0, 0, 1))
        self.start_date_input = TextInput(
            text=date.today().strftime('%Y-%m-%d'),
            font_size=dp(12),
            multiline=False
        )
        start_layout.add_widget(start_label)
        start_layout.add_widget(self.start_date_input)
        layout.add_widget(start_layout)
        
        # 结束日期
        end_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        end_label = Label(text='End:', font_size=dp(12), size_hint_x=None, width=dp(50), color=(0, 0, 0, 1))
        self.end_date_input = TextInput(
            text=(date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            font_size=dp(12),
            multiline=False
        )
        end_layout.add_widget(end_label)
        end_layout.add_widget(self.end_date_input)
        layout.add_widget(end_layout)
        
        return layout
    
    def create_owner_info(self):
        """创建事主信息区域"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150), spacing=dp(5))
        
        label = Label(
            text='Owner Info (Optional, YYYY-MM-DD HH:MM):',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            color=(0, 0, 0, 1)
        )
        layout.add_widget(label)
        
        # 事主1
        owner1_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60), spacing=dp(5))
        owner1_label = Label(text='Owner 1:', font_size=dp(12), size_hint_y=None, height=dp(20), halign='left', color=(0, 0, 0, 1))
        self.owner1_input = TextInput(
            text='1990-01-01 08:00',
            font_size=dp(12),
            multiline=False
        )
        owner1_layout.add_widget(owner1_label)
        owner1_layout.add_widget(self.owner1_input)
        layout.add_widget(owner1_layout)
        
        # 事主2
        owner2_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60), spacing=dp(5))
        owner2_label = Label(text='Owner 2:', font_size=dp(12), size_hint_y=None, height=dp(20), halign='left', color=(0, 0, 0, 1))
        self.owner2_input = TextInput(
            text='',
            font_size=dp(12),
            multiline=False,
            hint_text='Optional'
        )
        owner2_layout.add_widget(owner2_label)
        owner2_layout.add_widget(self.owner2_input)
        layout.add_widget(owner2_layout)
        
        return layout
    
    def create_action_buttons(self):
        """创建操作按钮区域"""
        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        
        start_button = Button(
            text='Start Zeri',
            font_size=dp(14),
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        start_button.bind(on_press=self.start_zeri)
        layout.add_widget(start_button)
        
        clear_button = Button(
            text='Clear',
            font_size=dp(14),
            background_color=(0.8, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        clear_button.bind(on_press=self.clear_all)
        layout.add_widget(clear_button)
        
        return layout
    
    def start_zeri(self, instance):
        """开始择日计算"""
        try:
            # 获取输入信息
            event_type = self.event_spinner.text
            start_date_str = self.start_date_input.text.strip()
            end_date_str = self.end_date_input.text.strip()
            
            # 解析日期
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # 验证日期范围
            if end_date < start_date:
                self.show_popup('Error', 'End date must be after start date')
                return
            
            # 获取事主信息
            owners = []
            if self.owner1_input.text.strip():
                owners.append(self.parse_owner_info(self.owner1_input.text.strip()))
            if self.owner2_input.text.strip():
                owners.append(self.parse_owner_info(self.owner2_input.text.strip()))
            
            # 计算择日
            self.calculate_zeri(event_type, start_date, end_date, owners)
            
        except ValueError as e:
            self.show_popup('Error', f'Date format error. Use YYYY-MM-DD format\n{str(e)}')
        except Exception as e:
            self.show_popup('Error', f'Calculation failed: {str(e)}')
    
    def parse_owner_info(self, info_str):
        """解析事主信息"""
        try:
            parts = info_str.split()
            date_str = parts[0]
            time_str = parts[1] if len(parts) > 1 else '12:00'
            
            dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
            return {
                'year': dt.year,
                'month': dt.month,
                'day': dt.day,
                'hour': dt.hour,
                'minute': dt.minute
            }
        except:
            return None
    
    def calculate_zeri(self, event_type, start_date, end_date, owners):
        """计算择日"""
        self.results = []
        current_date = start_date
        
        # 映射英文到中文
        event_map = {
            'Marry': '嫁娶',
            'Burial': '安葬',
            'Build': '修造',
            'Open': '开业',
            'Cook': '作灶',
            'Bed': '安床',
            'Travel': '出行',
            'Move': '入宅',
            'Market': '开市',
            'Dig': '动土',
            'Break': '破土'
        }
        chinese_event = event_map.get(event_type, event_type)
        
        while current_date <= end_date:
            try:
                # 计算四柱
                sizhu = calculate_sizhu(current_date.year, current_date.month, current_date.day, 12, 0)
                
                # 计算评分
                score_result = calculate_score(
                    event_type=chinese_event,
                    sizhu=sizhu,
                    owners=owners
                )
                
                # 添加到结果列表
                self.results.append({
                    'date': current_date,
                    'sizhu': sizhu,
                    'score': score_result.get('total_score', 0),
                    'level': score_result.get('level', 0),
                    'yi': score_result.get('yi', []),
                    'ji': score_result.get('ji', []),
                    'details': score_result
                })
                
            except Exception as e:
                print(f"Error calculating date {current_date}: {e}")
            
            current_date += timedelta(days=1)
        
        # 排序结果
        self.results.sort(key=lambda x: (-x['score'], -x['level']))
        
        # 显示结果
        self.display_results()
    
    def display_results(self):
        """显示择日结果"""
        if not self.results:
            self.result_label.text = 'No suitable dates found'
            return
        
        result_text = f'Found {len(self.results)} dates\n\n'
        
        # 显示前10个结果
        for i, result in enumerate(self.results[:10], 1):
            date_str = result['date'].strftime('%Y-%m-%d')
            score = result['score']
            level = result['level']
            star_level = STAR_LEVELS.get(level, 'Unknown')
            
            sizhu = result['sizhu']
            sizhu_str = f"{sizhu['year']}{sizhu['month']}{sizhu['day']}{sizhu['hour']}"
            
            yi = ', '.join(result['yi'][:2]) if result['yi'] else 'None'
            ji = ', '.join(result['ji'][:2]) if result['ji'] else 'None'
            
            result_text += f'{i}. {date_str}\n'
            result_text += f'   {sizhu_str}\n'
            result_text += f'   Score: {score} | {star_level}\n'
            result_text += f'   Yi: {yi}\n'
            result_text += f'   Ji: {ji}\n\n'
        
        if len(self.results) > 10:
            result_text += f'\n... and {len(self.results) - 10} more'
        
        self.result_label.text = result_text
    
    def clear_all(self, instance):
        """清空所有输入"""
        self.start_date_input.text = date.today().strftime('%Y-%m-%d')
        self.end_date_input.text = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.owner1_input.text = '1990-01-01 08:00'
        self.owner2_input.text = ''
        self.result_label.text = 'Click "Start" to view results'
        self.results = []
    
    def show_popup(self, title, message):
        """显示弹出窗口"""
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=dp(12)),
            size_hint=(0.8, 0.4)
        )
        popup.open()


class ZeriApp(App):
    """择日应用主类"""
    
    def build(self):
        """构建应用界面"""
        Window.title = 'Zeri App'
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加主屏幕
        zeri_screen = ZeriScreen(name='zeri')
        sm.add_widget(zeri_screen)
        
        return sm


if __name__ == '__main__':
    ZeriApp().run()
