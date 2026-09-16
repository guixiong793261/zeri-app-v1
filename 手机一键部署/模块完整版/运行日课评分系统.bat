@echo off
REM ======================================================================
REM  专业级日课评分系统 - 双击启动脚本（最终版 v5 — 纯净无额外命令依赖）
REM  无论成功/失败/异常退出，命令行窗口始终 PAUSE，绝不"一闪就退"。
REM  语法参考已经正常工作的「运行主程序.bat」保持一致。
REM ======================================================================
setlocal

REM ---------- 强制进入脚本所在目录（防 UNC / 工作目录漂移） ----------
cd /d "%~dp0"

REM ---------- 保证 logs 目录存在 ----------
if not exist "logs" mkdir "logs"
set "OUT_LOG=%CD%\logs\BAT启动_控制台.log"

REM ---------- 清理沙箱可能残留的旧启动输出 ----------
echo. > "%OUT_LOG%"

REM ---------- 显示标题 ----------
cls
echo.
echo  ##############################################################
echo  ##                                                          ##
echo  ##      专业级正五行择日软件 - 独立日课评分系统             ##
echo  ##                                                          ##
echo  ##   注意：本窗口是程序控制台，请勿提前关闭！               ##
echo  ##   正常使用：关闭 GUI 评分窗口后，这里会显示退出码，      ##
echo  ##   再按任意键退出本窗口。                                 ##
echo  ##                                                          ##
echo  ##############################################################
echo.

REM ---------- 第一步：找 Python（优先 python，兜底 py -3） ----------
set "PE="
where python >nul 2>&1 && set "PE=python"
if "%PE%"=="" ( where py >nul 2>&1 && set "PE=py -3" )

if "%PE%"=="" (
    echo   [错误] 未检测到 Python！
    echo.
    echo   请先安装 Python 3.9（或更高版本），安装时
    echo   务必勾选 "Add Python to PATH"，然后重新双击本文件。
    echo.
    pause
    exit /b 11
)

echo   [1/3] 工作目录 : %CD%
for /f "delims=" %%i in ('%PE% --version 2^>^&1') do echo   [2/3] Python     : %PE%  （%%i）
echo   [3/3] 控制台日志 : %OUT_LOG%
echo.
echo  -----------------------------------------------------------------
echo   正在启动日课评分系统 GUI ... （请稍候）
echo.

REM ---------- 把 BAT 启动信息写入 OUT_LOG ----------
>  "%OUT_LOG%" echo ======== BAT启动日志 ========
>> "%OUT_LOG%" echo 启动时间 : %date% %time%
>> "%OUT_LOG%" echo 工作目录 : %CD%
>> "%OUT_LOG%" echo 解释器   : %PE%

REM ---------- 第二步：真正启动 Python GUI（控制台直接可见；入口脚本自己会写闪退日志和里程碑）
REM  注意：入口脚本「日课评分系统.py」内部已实现持久化异常落盘 + 5 个里程碑打印 +
REM        Tk 回调异常钩子，因此不需要 BAT 再做 stdout 重定向。
%PE% 日课评分系统.py
set "EC=%ERRORLEVEL%"

REM ---------- 把退出码写入日志 ----------
>> "%OUT_LOG%" echo.
>> "%OUT_LOG%" echo Python退出码 : %EC%
>> "%OUT_LOG%" echo 结束时间     : %date% %time%

echo.
echo  -----------------------------------------------------------------
echo.
if "%EC%"=="0" (
    echo   [正常结束] 用户已关闭评分窗口（退出码=0）。
) else (
    echo   [程序异常] 退出码 = %EC%
    echo.
    echo   请把以下 2 份日志发给开发者用于定位问题：
    echo     #1 logs\日课评分系统_闪退日志.log   （Python 异常堆栈 / 5 个里程碑）
    echo     #2 %OUT_LOG%
    echo.
)
echo.
echo  -----------------------------------------------------------------
echo  按任意键退出本窗口 ...
pause >nul

endlocal
exit /b %EC%
