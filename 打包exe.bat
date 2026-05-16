@echo off
chcp 65001
echo ==========================================
echo  完美版正五行择日软件 - 打包工具
echo ==========================================
echo.

REM 检查是否安装了 pyinstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 pyinstaller...
    pip install pyinstaller
)

echo.
echo 请选择要打包的程序：
echo 1. 完美版正五行择日（主程序）
echo 2. 完美版日课评分系统
echo 3. 两个都打包
echo.
set /p choice=请输入选项(1/2/3):

if "%choice%"=="1" goto package_main
if "%choice%"=="2" goto package_score
if "%choice%"=="3" goto package_both
goto end

:package_main
echo.
echo 正在打包 完美版正五行择日...
pyinstaller --clean --onefile --windowed --name "完美版正五行择日" 完美版正五行择日.spec
goto end

:package_score
echo.
echo 正在打包 完美版日课评分系统...
pyinstaller --clean --onefile --windowed --name "完美版日课评分系统" 完美版日课评分系统.spec
goto end

:package_both
echo.
echo 正在打包 完美版正五行择日...
pyinstaller --clean --onefile --windowed --name "完美版正五行择日" 完美版正五行择日.spec
echo.
echo 正在打包 完美版日课评分系统...
pyinstaller --clean --onefile --windowed --name "完美版日课评分系统" 完美版日课评分系统.spec
goto end

:end
echo.
echo ==========================================
echo  打包完成！
echo  输出目录: dist\
echo ==========================================
pause
