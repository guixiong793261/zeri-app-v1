# -*- coding: utf-8 -*-
"""
verify: P1-② 八字排盘——.calculate()→.get_panpan_result() 对接 + 删遗留 print
退出码：全过 0 / 有失败 1；结尾打印 FAIL N。
"""
import sys, os, inspect, importlib, datetime
import tkinter as tk
import tkinter.messagebox as mb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILS = []
def check(name, cond):
    print(("[OK] " if cond else "[FAIL] ") + name)
    if not cond:
        FAILS.append(name)

mod = importlib.import_module('modules.八字可视化模块')

# ---------- 1. 源码级断言 ----------
import 主程序 as main_app
# open_bazi_panpan 所属类：搜索其所在类
owner_cls = None
for name in dir(main_app):
    obj = getattr(main_app, name)
    if inspect.isclass(obj) and hasattr(obj, 'open_bazi_panpan'):
        owner_cls = obj; break
check("找到 open_bazi_panpan 所属类", owner_cls is not None)
op_src = inspect.getsource(owner_cls.open_bazi_panpan)
check("open_bazi_panpan 不再含 print", "print(" not in op_src)
check("open_bazi_panpan 仍调用 show_bazi_input_dialog", "show_bazi_input_dialog" in op_src)

sp_src = inspect.getsource(mod.BaZiInputDialog._start_panpan)
check("_start_panpan 不再调用 bazi.calculate()", "bazi.calculate(" not in sp_src)
check("_start_panpan 已对接 get_panpan_result", "get_panpan_result()" in sp_src)

# ---------- 2. 接口返回结构 + 独立四柱黄金值（1990-05-15 10:30 男） ----------
bazi = mod.BaZiPanPan(1990, 5, 15, 10, 30, '男')
data = bazi.get_panpan_result()
required = ['基本信息', '四柱', '藏干', '十神', '五行统计', '五行分数',
            '纳音', '十二长生', '起运年龄', '起运年份', '大运']
check("get_panpan_result 键齐全", all(k in data for k in required))
sz = data['四柱']
# 独立核验（sxtwl 天文历，与 BaZiPanPan 实现分离）
try:
    import sxtwl
    day = sxtwl.fromSolar(1990, 5, 15)
    G, Z = "甲乙丙丁戊己庚辛壬癸", "子丑寅卯辰巳午未申酉戌亥"
    def gz(t): return G[t.tg] + Z[t.dz]
    y = gz(day.getYearGZ()); m = gz(day.getMonthGZ()); d = gz(day.getDayGZ())
    # 巳时：日干庚 → 五鼠遁 乙庚日丙子时起：丙子丁丑戊寅己卯庚辰辛巳
    h = '辛巳'
    expect = (y, m, d, h)
except Exception:
    expect = ('庚午', '辛巳', '庚辰', '辛巳')
got = (sz['年柱'], sz['月柱'], sz['日柱'], sz['时柱'])
check(f"四柱与独立天文历一致：{got} == {expect}", got == expect)

# ---------- 3. 端到端：对话框确认 → 销毁 → 结果窗数据 ----------
root = tk.Tk(); root.withdraw()
shown = {}
def fake_show(title, message, *a, **k):
    shown.setdefault('boxes', []).append((title, message))
mb.showwarning = fake_show
mb.showerror = fake_show
captured = []
orig_dialog = mod.BaZiDialog
mod.BaZiDialog = lambda parent, pdata: captured.append(pdata)
try:
    dlg = mod.BaZiInputDialog(root)
    dlg._start_panpan()
    check("确认后输入对话框已销毁", dlg.dialog.winfo_exists() == 0)
    check("结果窗收到完整排盘数据", bool(captured) and '四柱' in captured[0])

    # ---------- 4. 反向断言：非法/不存在日期被拒绝，不产出结果 ----------
    shown.clear(); captured.clear()
    dlg2 = mod.BaZiInputDialog(root)
    dlg2.year_var.set('1899')
    dlg2._start_panpan()
    check("1899 年：弹输入警告", bool(shown.get('boxes')))
    check("1899 年：不创建结果窗", not captured)
    check("1899 年：输入窗保留", dlg2.dialog.winfo_exists() == 1)
    dlg2.dialog.destroy()

    shown.clear(); captured.clear()
    dlg3 = mod.BaZiInputDialog(root)
    dlg3.month_var.set('2'); dlg3.day_var.set('30')
    dlg3._start_panpan()
    check("2月30日：弹输入警告且不创建结果窗",
          bool(shown.get('boxes')) and not captured)
    dlg3.dialog.destroy()
finally:
    mod.BaZiDialog = orig_dialog
    root.destroy()

print()
print(f"FAIL {len(FAILS)}")
sys.exit(1 if FAILS else 0)
