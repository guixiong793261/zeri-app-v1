# -*- coding: utf-8 -*-
"""
================================================================================
择日大师 · 精准择时版（独立版）v1.0
================================================================================
定位：从主程序剥离的「精准择时（反推 Top-N）」独立交付物。

铁律：底层算法必须与主仓共享，严禁新建一套计分逻辑。
- 反推引擎 / 评分器 / 四柱计算器 / 今日黄历 / 玄空飞星等一律 import 现有模块；
- 事主 owners_data 与 context 组装口径严格对齐主程序
  （_collect_owners_data / open_reverse_panel），含真太阳时经度透传；
- 独立版只做「参数收集 + 调用 modules.反推UI.open_reverse_window」的瘦壳。

数据隔离：配置写入 APP_DIR/精准择时版_配置.json，与主程序记录互不干扰。
（frozen 时 APP_DIR = exe 所在目录；源码运行时 = 项目根目录——与主程序 L110 同口径）
================================================================================
"""

import json
import os
import sys
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

# ----- 路径与 APP_DIR（口径同主程序 L95-110） -----
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
    PROJECT_ROOT = APP_DIR
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = PROJECT_ROOT
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CONFIG_PATH = os.path.join(APP_DIR, '精准择时版_配置.json')

# ----- 底层模块：严格复用主仓，不新建计分逻辑 -----
from modules.事项标准 import UI_EVENTS, MOUNTAIN_CENTERED_EVENTS
from modules.二十四山 import get_shan_xiang_list, shan_xiang_to_shan
from modules.城市经度 import CITY_NAMES, get_longitude
from modules.四柱计算器 import calculate_sizhu
from modules.反推UI import open_reverse_window

VERSION = 'v1.0'
# 宅型适用事项（与主程序 L1401 同口径）
HOUSE_TYPE_EVENTS = {"修造", "动土", "拆舍", "入宅"}
# 山向适用事项（山家核心事项 + 修造/动土/拆舍/入宅/安葬，同主程序 special_frame 口径）
SHAN_XIANG_EVENTS = set(MOUNTAIN_CENTERED_EVENTS) | {"修造", "动土", "拆舍", "入宅"}
# 双事主事项（嫁娶族需新郎新娘双方年命）
DUAL_OWNER_EVENTS = {"嫁娶", "订婚", "纳采"}


def _city_to_longitude(city_text):
    """城市名/经度串 → 经度 float。空值回退 120.0（北京时间基准，同主程序 §48 口径）。"""
    raw = (city_text or '').strip()
    if not raw:
        return 120.0
    lon = get_longitude(raw)
    if lon is not None:
        return float(lon)
    try:
        v = float(raw)
        return v if 60.0 <= v <= 150.0 else 120.0
    except (TypeError, ValueError):
        return 120.0


class 精准择时版App:
    """独立版瘦壳：参数区（事项/山向/事主/城市经度）+ 工具栏 + 启动反推面板。"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"择日大师 · 精准择时版 {VERSION}")
        self.root.geometry("920x560")
        self.reverse_window = None
        self.owner_rows = []

        self._build_toolbar()
        self._build_param_area()
        self._build_owner_area()
        self._build_action_area()
        self._build_statusbar()
        self._load_config()
        self._on_event_change()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- UI 构建 ----------
    def _build_toolbar(self):
        bar = ttk.LabelFrame(self.root, text="扩展工具", padding=6)
        bar.pack(fill=tk.X, padx=10, pady=(8, 4))
        ttk.Button(bar, text="🧭 电子罗盘", command=self._open_compass).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="📅 今日黄历", command=self._open_today_huangli).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="📊 八字排盘", command=self._open_bazi).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="🔮 玄空飞星排盘", command=self._open_xuankong).pack(side=tk.LEFT, padx=6)

    def _build_param_area(self):
        frm = ttk.LabelFrame(self.root, text="择时参数", padding=8)
        frm.pack(fill=tk.X, padx=10, pady=4)

        ttk.Label(frm, text="事项：").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.event_var = tk.StringVar(value="修造")
        ev = ttk.Combobox(frm, textvariable=self.event_var, values=UI_EVENTS,
                          width=10, state="readonly")
        ev.grid(row=0, column=1, sticky=tk.W, padx=4)
        ev.bind("<<ComboboxSelected>>", lambda e: self._on_event_change())

        ttk.Label(frm, text="宅型：").grid(row=0, column=2, sticky=tk.W, padx=4)
        self.house_type_var = tk.StringVar(value="阳宅")
        self.house_combo = ttk.Combobox(frm, textvariable=self.house_type_var,
                                        values=["阳宅", "阴宅"], width=8, state="readonly")
        self.house_combo.grid(row=0, column=3, sticky=tk.W, padx=4)

        ttk.Label(frm, text="山向：").grid(row=0, column=4, sticky=tk.W, padx=4)
        self.shan_xiang_var = tk.StringVar()
        self.shan_combo = ttk.Combobox(frm, textvariable=self.shan_xiang_var,
                                       values=get_shan_xiang_list(use_24_shan=True),
                                       width=12, state="readonly")
        self.shan_combo.grid(row=0, column=5, sticky=tk.W, padx=4)

        ttk.Label(frm, text="兼向：").grid(row=0, column=6, sticky=tk.W, padx=4)
        self.jian_xiang_var = tk.StringVar(value="正中")
        # 同主程序 §59.13：可下拉选环序兼向，也可手动输入"兼X"
        self.jian_combo = ttk.Combobox(frm, textvariable=self.jian_xiang_var,
                                       values=["正中", "兼左", "兼右"], width=8)
        self.jian_combo.grid(row=0, column=7, sticky=tk.W, padx=4)

        ttk.Button(frm, text="罗盘", width=6,
                   command=self._open_compass).grid(row=0, column=8, sticky=tk.W, padx=6)

        hint = ("山向仅对修造/动土/拆舍/入宅/安葬/作灶/安床等山家事项生效；"
                "城市决定真太阳时（留空按北京时间 120°E）。")
        ttk.Label(frm, text=hint, foreground="#666").grid(
            row=1, column=0, columnspan=9, sticky=tk.W, padx=4, pady=(6, 0))

    def _build_owner_area(self):
        self.owner_frame = ttk.LabelFrame(self.root, text="事主信息（嫁娶请同时填新郎新娘）", padding=8)
        self.owner_frame.pack(fill=tk.X, padx=10, pady=4)
        head = ["角色", "姓名", "性别", "出生年", "月", "日", "时", "分", "出生城市/经度"]
        for c, t in enumerate(head):
            ttk.Label(self.owner_frame, text=t).grid(row=0, column=c, padx=3, sticky=tk.W)
        self._add_owner_row(1, "事主")
        self._add_owner_row(2, "家人")

    def _add_owner_row(self, idx, default_role):
        r = idx
        role = ttk.Combobox(self.owner_frame, values=["事主", "新郎", "新娘", "家人"],
                            width=6)
        role.set(default_role)
        role.grid(row=r, column=0, padx=3)
        name = ttk.Entry(self.owner_frame, width=10)
        name.grid(row=r, column=1, padx=3)
        gender = ttk.Combobox(self.owner_frame, values=["男", "女"], width=4, state="readonly")
        gender.set("男")
        gender.grid(row=r, column=2, padx=3)
        year = ttk.Entry(self.owner_frame, width=7)
        year.grid(row=r, column=3, padx=3)
        month = ttk.Entry(self.owner_frame, width=4)
        month.grid(row=r, column=4, padx=3)
        day = ttk.Entry(self.owner_frame, width=4)
        day.grid(row=r, column=5, padx=3)
        hour = ttk.Entry(self.owner_frame, width=4)
        hour.insert(0, "12")
        hour.grid(row=r, column=6, padx=3)
        minute = ttk.Entry(self.owner_frame, width=4)
        minute.insert(0, "0")
        minute.grid(row=r, column=7, padx=3)
        city = ttk.Combobox(self.owner_frame, values=sorted(CITY_NAMES), width=14)
        city.grid(row=r, column=8, padx=3)
        self.owner_rows.append({
            'role': role, 'name': name, 'gender': gender,
            'year': year, 'month': month, 'day': day,
            'hour': hour, 'minute': minute, 'city': city,
        })

    def _build_action_area(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill=tk.X, padx=10, pady=4)
        ttk.Button(frm, text="开始精准择时（反推 Top-N 榜单）",
                   command=self.open_reverse_panel).pack(side=tk.LEFT, padx=4)
        ttk.Button(frm, text="保存当前参数", command=self._save_config).pack(side=tk.LEFT, padx=4)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="就绪：填写参数后点击「开始精准择时」。")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                  anchor=tk.W, padding=4).pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- 事项联动 ----------
    def _on_event_change(self):
        ev = self.event_var.get()
        # 宅型仅对修造/动土/拆舍/入宅生效（主程序 L1401 口径）
        self.house_combo.configure(state="readonly" if ev in HOUSE_TYPE_EVENTS else "disabled")
        # 山向/兼向仅山家事项生效
        st = "readonly" if ev in SHAN_XIANG_EVENTS else "disabled"
        self.shan_combo.configure(state=st)
        self.jian_combo.configure(state="normal" if ev in SHAN_XIANG_EVENTS else "disabled")
        # 嫁娶族：两位事主角色默认新郎/新娘
        if ev in DUAL_OWNER_EVENTS:
            self.owner_rows[0]['role'].set("新郎")
            self.owner_rows[1]['role'].set("新娘")
        self.status_var.set(f"当前事项：{ev}")

    # ---------- owners_data / context 组装（严格对齐主程序口径） ----------
    def _collect_owners_data(self):
        """与主程序 _collect_owners_data 同口径：空生日跳过、无效生日回退当月末日、
        真太阳时经度透传 calculate_sizhu(longitude=...)。"""
        owners_data = []
        import calendar
        for row in self.owner_rows:
            try:
                year_str = row['year'].get().strip()
                month_str = row['month'].get().strip()
                day_str = row['day'].get().strip()
                if not (year_str and month_str and day_str):
                    continue
                year = int(year_str)
                month = int(month_str)
                day = int(day_str)
                hour = int(row['hour'].get().strip() or '12')
                minute = int(row['minute'].get().strip() or '0')
                gender = row['gender'].get()
                try:
                    birth_date = date(year, month, day)
                except ValueError:
                    last_day = calendar.monthrange(year, month)[1]
                    birth_date = date(year, month, last_day)
                    messagebox.showwarning(
                        "日期修正",
                        f"您输入的日期 {year}-{month}-{day} 无效，已自动修正为 {year}-{month}-{last_day}")
                birth_longitude = _city_to_longitude(row['city'].get())
                owner_sizhu = calculate_sizhu(birth_date, hour, minute, longitude=birth_longitude)
                owner_data = {
                    'name': row['name'].get().strip(),
                    'role': row['role'].get().strip(),
                    'birth_date': birth_date,
                    'birth_hour': hour,
                    'birth_minute': minute,
                    'birth_longitude': birth_longitude,
                    '性别': gender,
                    '年干': owner_sizhu.get('year_gan', ''),
                    '年支': owner_sizhu.get('year_zhi', ''),
                    '日干': owner_sizhu.get('day_gan', ''),
                    '日支': owner_sizhu.get('day_zhi', ''),
                    '生肖': owner_sizhu.get('year_zhi', ''),
                }
                owners_data.append(owner_data)
            except (ValueError, TypeError):
                continue
        return owners_data

    def _build_context(self):
        """与主程序 open_reverse_panel 同口径：兼向拼接 + zeli_mode='pure'。"""
        _shan = self.shan_xiang_var.get() or ''
        _jx = self.jian_xiang_var.get() or ''
        if _shan and _jx and _jx != '正中':
            if not str(_jx).startswith('兼'):
                _jx = '兼' + str(_jx)
            _shan = f"{_shan}{_jx}"
        ev = self.event_var.get()
        return {
            'house_type': self.house_type_var.get() if ev in HOUSE_TYPE_EVENTS else '',
            'shan_xiang': (_shan or None) if ev in SHAN_XIANG_EVENTS else None,
            'zao_xiang': None,
            'zao_wei': None,
            'chuang_wei': None,
            'zaozhu_mode': None,
            'zeli_mode': 'pure',
        }

    def _focus_params(self):
        """反推窗口「修改事主与山向」回调：把焦点交回参数面板首事主姓名框。"""
        try:
            self.root.deiconify()
            self.root.lift()
            self.owner_rows[0]['name'].focus_set()
        except Exception as e:
            self.status_var.set(f"焦点回退失败：{e}")

    # ---------- 打开反推面板 ----------
    def open_reverse_panel(self):
        try:
            owners = self._collect_owners_data()
            ctx = self._build_context()
            self.reverse_window = open_reverse_window(
                self.root, self.event_var.get(), owners, ctx,
                modify_callback=self._focus_params,
                add_tie_callback=None,  # 独立版不接择日贴，复用反推UI内置中文降级提示
            )
            self.status_var.set("精准择时面板已打开。修改参数后可再次点击重新反推。")
            self._save_config()
        except Exception as e:
            messagebox.showerror("错误", f"打开精准择时面板失败：{e}")

    # ---------- 扩展工具 ----------
    def _open_compass(self):
        """电子罗盘：选择山向后回写参数区，并按度数自动识别兼向（口径同主程序 L3000-3023）。"""
        try:
            from modules.电子罗盘 import show_compass_dialog, CompassConverter

            def on_compass_select(shan_xiang, degree):
                if shan_xiang:
                    self.shan_xiang_var.set(shan_xiang)
                    converter = CompassConverter()
                    mountain = shan_xiang_to_shan(shan_xiang)
                    jianxiang = converter.get_jianxiang(mountain, degree)
                    self.jian_xiang_var.set(jianxiang if jianxiang else "正中")

            show_compass_dialog(self.root, self.shan_xiang_var.get() or None, on_compass_select)
        except Exception as e:
            messagebox.showerror("电子罗盘", f"打开电子罗盘失败：{e}")

    def _open_today_huangli(self):
        try:
            from modules.今日黄历 import show_today_huangli
            show_today_huangli(self.root)
        except Exception as e:
            messagebox.showerror("今日黄历", f"打开今日黄历失败：{e}")

    def _open_bazi(self):
        try:
            from modules.八字可视化模块 import show_bazi_input_dialog
            show_bazi_input_dialog(self.root)
        except Exception as e:
            messagebox.showerror("八字排盘", f"打开八字排盘失败：{e}")

    def _open_xuankong(self):
        """玄空飞星排盘：自动带入当前山向/兼向（口径同主程序 open_xuankong）。"""
        try:
            import datetime as _dt
            import importlib
            xk_mod = importlib.import_module('玄空飞星_日课展示')
            today = _dt.date.today()
            mountain = None
            sx_v = self.shan_xiang_var.get() or ''
            if sx_v and '山' in sx_v:
                mountain = sx_v.split('山')[0].strip()
            jianxiang = '正向'
            jx_v = self.jian_xiang_var.get() or ''
            mcw = getattr(xk_mod, 'MOUNTAINS_CW', None)
            if mountain and jx_v and jx_v != '正中' and mcw and mountain in mcw:
                idx = mcw.index(mountain)
                left_m = mcw[(idx - 1) % 24]
                right_m = mcw[(idx + 1) % 24]
                if jx_v.startswith('兼') and len(jx_v) >= 2:
                    jx_shan = jx_v[1:]
                    if jx_shan in (left_m, right_m):
                        jianxiang = f"兼{jx_shan}"
                    elif jx_v == '兼左':
                        jianxiang = f"兼{left_m}"
                    elif jx_v == '兼右':
                        jianxiang = f"兼{right_m}"
                elif jx_v == '兼左':
                    jianxiang = f"兼{left_m}"
                elif jx_v == '兼右':
                    jianxiang = f"兼{right_m}"
            preset = {'year': today.year, 'month': today.month, 'day': today.day,
                      'hour': 12, 'minute': 0,
                      'mountain': mountain, 'jianxiang': jianxiang}
            win = tk.Toplevel(self.root)
            xk_mod.XuanKongApp(win, preset=preset)
        except Exception as e:
            messagebox.showerror("玄空飞星", f"打开玄空飞星失败：{e}")

    # ---------- 配置持久化（独立文件，与主程序隔离） ----------
    def _save_config(self):
        try:
            data = {
                'event': self.event_var.get(),
                'house_type': self.house_type_var.get(),
                'shan_xiang': self.shan_xiang_var.get(),
                'jian_xiang': self.jian_xiang_var.get(),
                'owners': [{
                    'role': r['role'].get(), 'name': r['name'].get(),
                    'gender': r['gender'].get(),
                    'year': r['year'].get(), 'month': r['month'].get(),
                    'day': r['day'].get(), 'hour': r['hour'].get(),
                    'minute': r['minute'].get(), 'city': r['city'].get(),
                } for r in self.owner_rows],
            }
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"参数已保存：{CONFIG_PATH}")
        except Exception as e:
            messagebox.showwarning("配置保存", f"保存配置失败：{e}")

    def _load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                return
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('event') in UI_EVENTS:
                self.event_var.set(data['event'])
            if data.get('house_type'):
                self.house_type_var.set(data['house_type'])
            if data.get('shan_xiang'):
                self.shan_xiang_var.set(data['shan_xiang'])
            if data.get('jian_xiang'):
                self.jian_xiang_var.set(data['jian_xiang'])
            for row, saved in zip(self.owner_rows, data.get('owners', [])):
                for key, widget in row.items():
                    val = saved.get(key)
                    if val is None:
                        continue
                    if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                        widget.delete(0, tk.END)
                        widget.insert(0, str(val))
        except Exception as e:
            self.status_var.set(f"读取配置失败（已忽略）：{e}")

    def _on_close(self):
        self._save_config()
        self.root.destroy()


def main():
    root = tk.Tk()
    精准择时版App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
