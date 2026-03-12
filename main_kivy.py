# -*- coding: utf-8 -*-
"""
================================================================================
择日软件 Kivy版本
================================================================================
用于Android APK打包的Kivy版本
================================================================================
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

# 设置窗口大小（模拟手机屏幕）
Window.size = (400, 700)

# 导入原有的计算模块
from datetime import date, datetime, timedelta

# 天干地支基础数据（从原文件复制）
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

class ZeriAppKivy(App):
    """择日软件Kivy版本"""
    
    def build(self):
        """构建应用界面"""
        self.title = '专业级正五行择日软件'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_label = Label(
            text='专业级正五行择日软件',
            font_size='24sp',
            size_hint_y=None,
            height=50,
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # 创建标签页
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # 择日标签页
        tab_zeri = TabbedPanelHeader(text='择日')
        tab_zeri.content = self.create_zeri_tab()
        tab_panel.add_widget(tab_zeri)
        
        # 日课评分标签页
        tab_score = TabbedPanelHeader(text='日课评分')
        tab_score.content = self.create_score_tab()
        tab_panel.add_widget(tab_score)
        
        # 设置标签页
        tab_settings = TabbedPanelHeader(text='设置')
        tab_settings.content = self.create_settings_tab()
        tab_panel.add_widget(tab_settings)
        
        main_layout.add_widget(tab_panel)
        
        return main_layout
    
    def create_zeri_tab(self):
        """创建择日标签页"""
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 事项类型选择
        layout.add_widget(Label(text='事项类型:', size_hint_y=None, height=30))
        self.event_spinner = Spinner(
            text='嫁娶',
            values=['嫁娶', '修造', '动土', '入宅', '开业', '出行', '安床', '作灶', '安葬'],
            size_hint_y=None,
            height=44
        )
        layout.add_widget(self.event_spinner)
        
        # 日期范围
        layout.add_widget(Label(text='开始日期 (YYYY-MM-DD):', size_hint_y=None, height=30))
        self.start_date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.start_date_input)
        
        layout.add_widget(Label(text='结束日期 (YYYY-MM-DD):', size_hint_y=None, height=30))
        self.end_date_input = TextInput(
            text=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.end_date_input)
        
        # 计算按钮
        calc_btn = Button(
            text='开始择日',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1)
        )
        calc_btn.bind(on_press=self.on_calculate)
        layout.add_widget(calc_btn)
        
        # 结果显示区域
        layout.add_widget(Label(text='择日结果:', size_hint_y=None, height=30))
        self.result_label = Label(
            text='点击"开始择日"查看结果',
            size_hint_y=None,
            height=200,
            markup=True,
            halign='left',
            valign='top'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        layout.add_widget(self.result_label)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_score_tab(self):
        """创建日课评分标签页"""
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(Label(
            text='日课评分系统',
            font_size='20sp',
            size_hint_y=None,
            height=40,
            bold=True
        ))
        
        layout.add_widget(Label(
            text='此功能需要导入择日结果进行评分',
            size_hint_y=None,
            height=30
        ))
        
        # 评分按钮
        score_btn = Button(
            text='开始评分',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        score_btn.bind(on_press=self.on_score)
        layout.add_widget(score_btn)
        
        # 评分结果
        self.score_result_label = Label(
            text='评分结果将显示在这里',
            size_hint_y=None,
            height=300,
            markup=True,
            halign='left',
            valign='top'
        )
        self.score_result_label.bind(size=self.score_result_label.setter('text_size'))
        layout.add_widget(self.score_result_label)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_settings_tab(self):
        """创建设置标签页"""
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(Label(
            text='设置',
            font_size='20sp',
            size_hint_y=None,
            height=40,
            bold=True
        ))
        
        # 版本信息
        layout.add_widget(Label(
            text='版本: 1.0 (Kivy版)',
            size_hint_y=None,
            height=30
        ))
        
        # 关于按钮
        about_btn = Button(
            text='关于',
            size_hint_y=None,
            height=50
        )
        about_btn.bind(on_press=self.show_about)
        layout.add_widget(about_btn)
        
        scroll.add_widget(layout)
        return scroll
    
    def on_calculate(self, instance):
        """计算择日"""
        try:
            start_str = self.start_date_input.text
            end_str = self.end_date_input.text
            
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            # 简化的择日计算（示例）
            results = []
            current = start
            while current <= end:
                # 这里应该调用原有的计算逻辑
                day_score = self.calculate_day_score(current)
                results.append({
                    'date': current,
                    'score': day_score,
                    'sizhu': self.get_simple_sizhu(current)
                })
                current += timedelta(days=1)
            
            # 排序并显示前10个结果
            results.sort(key=lambda x: x['score'], reverse=True)
            top_results = results[:10]
            
            result_text = '[b]择日结果（前10名）:[/b]\n\n'
            for i, r in enumerate(top_results, 1):
                result_text += f"{i}. {r['date']}\n"
                result_text += f"   评分: {r['score']}/100\n"
                result_text += f"   四柱: {r['sizhu']}\n\n"
            
            self.result_label.text = result_text
            
        except Exception as e:
            self.show_popup('错误', f'计算失败: {str(e)}')
    
    def calculate_day_score(self, target_date):
        """计算日期评分（简化版）"""
        # 这里应该调用原有的评分逻辑
        # 现在使用简单的示例算法
        day_of_year = target_date.timetuple().tm_yday
        base_score = 60 + (day_of_year % 40)
        return min(100, max(0, base_score))
    
    def get_simple_sizhu(self, target_date):
        """获取简化四柱（示例）"""
        # 这里应该调用原有的四柱计算
        year_gan = TIAN_GAN[target_date.year % 10]
        year_zhi = DI_ZHI[target_date.year % 12]
        return f"{year_gan}{year_zhi}年"
    
    def on_score(self, instance):
        """日课评分"""
        self.score_result_label.text = '[b]评分功能[/b]\n\n请先进行择日计算，然后导入结果进行评分。'
    
    def show_about(self, instance):
        """显示关于信息"""
        self.show_popup('关于', '专业级正五行择日软件\n版本: 1.0 (Kivy版)\n\n用于Android设备的择日工具')
    
    def show_popup(self, title, message):
        """显示弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()


if __name__ == '__main__':
    ZeriAppKivy().run()
