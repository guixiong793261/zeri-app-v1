@echo off
chcp 65001
cls
echo ==========================================
echo  专业级正五行择日软件 - GitHub上传工具
echo ==========================================
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Git未安装！
    echo.
    echo 请先安装Git：
    echo 1. 访问 https://git-scm.com/download/win
    echo 2. 下载并安装Git
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo [✓] Git已安装
echo.

REM 设置项目目录
cd /d "%~dp0"
echo 当前目录: %CD%
echo.

REM 初始化Git仓库
if not exist .git (
    echo [1/6] 初始化Git仓库...
    git init
    if errorlevel 1 (
        echo [错误] 初始化失败！
        pause
        exit /b 1
    )
    echo [✓] Git仓库初始化成功
) else (
    echo [✓] Git仓库已存在
)
echo.

REM 配置Git用户信息
echo [2/6] 配置Git用户信息...
git config user.name "Zeri App Developer"
git config user.email "developer@zeri.app"
echo [✓] Git配置完成
echo.

REM 添加所有文件
echo [3/6] 添加文件到Git...
git add .
if errorlevel 1 (
    echo [错误] 添加文件失败！
    pause
    exit /b 1
)
echo [✓] 文件添加成功
echo.

REM 提交更改
echo [4/6] 提交更改...
git commit -m "Initial commit - 专业级正五行择日软件 v1.0"
if errorlevel 1 (
    echo [注意] 没有新的更改需要提交
) else (
    echo [✓] 提交成功
)
echo.

REM 提示用户输入GitHub仓库地址
echo [5/6] 连接GitHub仓库...
echo.
echo 请先在GitHub上创建仓库：
echo 1. 访问 https://github.com/new
echo 2. 输入仓库名称（例如：zeri-app）
echo 3. 选择 Public
echo 4. 点击 Create repository
echo.
echo 然后复制仓库地址（格式：https://github.com/用户名/仓库名.git）
echo.
set /p REPO_URL="请输入GitHub仓库地址: "

if "%REPO_URL%"=="" (
    echo [错误] 仓库地址不能为空！
    pause
    exit /b 1
)

REM 添加远程仓库
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
if errorlevel 1 (
    echo [错误] 添加远程仓库失败！
    pause
    exit /b 1
)
echo [✓] 远程仓库连接成功
echo.

REM 推送到GitHub
echo [6/6] 推送到GitHub...
echo 正在推送代码，请稍候...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败！
    echo.
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. 需要GitHub认证
    echo 3. 仓库地址错误
    echo.
    echo 解决方法：
    echo 1. 检查网络连接
    echo 2. 访问 https://github.com/settings/tokens 创建Personal Access Token
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  [✓] 上传成功！
echo ==========================================
echo.
echo 下一步：
echo 1. 访问 %REPO_URL%
echo 2. 点击 "Actions" 标签查看构建进度
echo 3. 等待30-60分钟构建完成
echo 4. 下载生成的APK文件
echo.
echo 应用信息：
echo - 名称：专业级正五行择日软件
echo - 版本：1.0
echo - 包名：com.example.zeri
echo.
pause
