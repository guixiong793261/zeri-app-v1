# -*- coding: utf-8 -*-
"""
专业级日课评分系统 - 独立启动脚本（闪退证据留痕版 v2）
- 顶层未捕获异常：落盘 logs/日课评分系统_闪退日志.log + 控制台打印 + 回车不退出
- 导入期/创建期/mainloop期 打印"里程碑"，便于定位闪退阶段
"""
import sys, os, traceback, datetime, io

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
CRASH_LOG = os.path.join(LOG_DIR, '日课评分系统_闪退日志.log')

def _write_log(msg):
    """同时写入控制台和闪退日志"""
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = '[%s] %s' % (ts, msg)
    try:
        with open(CRASH_LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass
    print(line, flush=True)

def _hook_excepthook(exc_type, exc_value, tb):
    """全局未捕获异常钩子"""
    buf = io.StringIO()
    traceback.print_exception(exc_type, exc_value, tb, file=buf)
    _write_log('========= 全局未捕获异常 =========')
    _write_log(buf.getvalue().rstrip())
    # Tk 已经炸了，别再弹 messagebox；直接阻塞
    try:
        print('\n[闪退] 异常已写入日志: %s' % CRASH_LOG, flush=True)
        input('按回车键退出...')
    except Exception:
        pass
    sys.exit(1)

sys.excepthook = _hook_excepthook

# 安装 Tkinter 回调异常钩子（经验 100017757：大部分闪退发生在 Tk after/bind 回调而非主线程）
def _install_tk_err_hook():
    try:
        import tkinter as tk
        # 创建 Tk 的实例后才能 report_callback_exception，但覆盖类方法对所有实例生效
        orig = getattr(tk.Tk, 'report_callback_exception', None)
        def _safe_report(self, *exc_info):
            exc_type, exc_value, tb = exc_info
            buf = io.StringIO()
            traceback.print_exception(exc_type, exc_value, tb, file=buf)
            _write_log('========= Tkinter 回调异常 =========')
            _write_log(buf.getvalue().rstrip())
            try:
                from tkinter import messagebox
                messagebox.showerror('运行错误',
                                     '程序运行中出现错误，详细信息已写入日志：\n\n%s' % CRASH_LOG)
            except Exception:
                pass
            if orig is not None:
                try:
                    orig(self, *exc_info)
                except Exception:
                    pass
        # 覆盖 Tk/Toplevel 的异常回调，防止不同父类
        for cls in (tk.Tk, tk.Misc):
            try:
                cls.report_callback_exception = _safe_report
            except Exception:
                pass
    except Exception as e:
        _write_log('安装Tk异常钩子失败(非致命): %s' % e)

_install_tk_err_hook()

_write_log('============================================================')
_write_log('启动：日课评分系统独立入口（闪退证据留痕版）')
_write_log('  PROJECT_ROOT = %s' % PROJECT_ROOT)
_write_log('  sys.executable = %s' % sys.executable)
_write_log('  sys.version    = %s' % sys.version.replace('\n', ' '))
_write_log('  闪退日志路径   = %s' % CRASH_LOG)

# 1. 导入模块
_write_log('[里程碑 1/5] 开始导入 modules.日课评分系统')
try:
    from modules.日课评分系统 import DayScoreWindow
except Exception as e:
    _write_log('导入失败: %s' % e)
    _write_log(traceback.format_exc().rstrip())
    try:
        input('\n按回车键退出...')
    except Exception:
        pass
    sys.exit(2)
_write_log('[里程碑 2/5] 导入成功，准备创建 DayScoreWindow(full)')

def main():
    _write_log('[里程碑 3/5] DayScoreWindow.__init__ 开始')
    app = DayScoreWindow()  # master=None → mode='full'（默认） → 创建 Tk
    _write_log('[里程碑 4/5] DayScoreWindow.__init__ 完成，进入 app.run()')
    app.run()
    _write_log('[里程碑 5/5] mainloop 正常退出（用户主动关闭窗口）')

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        _write_log('用户中断(Ctrl+C)')
    except Exception as e:
        _write_log('main() 顶层异常: %s' % e)
        _write_log(traceback.format_exc().rstrip())
        try:
            print('\n[闪退] 详细日志已保存到: %s' % CRASH_LOG, flush=True)
            input('按回车键退出...')
        except Exception:
            pass
        sys.exit(3)
