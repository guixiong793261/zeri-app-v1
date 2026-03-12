# 专业级正五行择日软件 - APK打包说明

## 快速开始

### 方法1：使用GitHub Actions自动打包（最简单）

1. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 创建一个新的公开仓库
   - 将项目文件上传到仓库

2. **触发构建**
   - 推送代码到GitHub
   - 访问仓库的"Actions"标签页
   - 等待构建完成（约30-60分钟）

3. **下载APK**
   - 构建完成后，在Actions页面找到构建记录
   - 点击"Artifacts"下载APK文件

### 方法2：使用Replit在线打包

1. 访问 https://replit.com
2. 创建新的Python项目
3. 上传以下文件：
   - main.py
   - main_kivy_complete.py
   - buildozer.spec
4. 在终端运行：`buildozer android debug`
5. 等待构建完成，下载APK

### 方法3：使用WSL（需要技术基础）

```powershell
# 1. 安装WSL
wsl --install

# 2. 重启电脑后，在WSL中运行
sudo apt update
sudo apt install -y build-essential git python3 python3-pip openjdk-17-jdk
pip3 install buildozer

# 3. 进入项目目录
cd /mnt/d/自编择日软件/专业级正五行择日软件

# 4. 构建APK
buildozer android debug
```

## 项目文件

确保项目包含以下文件：

```
专业级正五行择日软件/
├── main.py                          # 主入口文件
├── main_kivy_complete.py            # Kivy应用代码
├── buildozer.spec                  # Buildozer配置文件
├── .github/
│   └── workflows/
│       └── build-apk.yml           # GitHub Actions工作流
├── APK打包指南.md                   # 详细打包指南
└── README.md                       # 本文件
```

## 应用信息

- **应用名称**：专业级正五行择日软件
- **包名**：com.example.zeri
- **版本**：1.0
- **支持架构**：armeabi-v7a, arm64-v8a
- **最低API**：21 (Android 5.0+)
- **目标API**：33 (Android 13)

## 功能特性

- 四柱计算（年柱、月柱、日柱、时柱）
- 日期范围择日
- 日课评分系统
- 多种事项类型支持
- 响应式手机界面

## 常见问题

### Q: 构建需要多长时间？
A: 首次构建约30-60分钟，后续构建约15-30分钟。

### Q: APK文件有多大？
A: 通常在20-50MB之间。

### Q: 支持哪些Android版本？
A: 支持Android 5.0 (API 21)及以上版本。

### Q: 构建失败怎么办？
A: 检查：
1. buildozer.spec配置是否正确
2. 所有文件是否上传完整
3. GitHub Actions日志中的错误信息

### Q: 如何更新应用？
A: 修改代码后推送到GitHub，Actions会自动构建新版本。

## 技术支持

如遇到问题，请检查：
- GitHub Actions构建日志
- buildozer.spec配置
- Python版本（推荐3.11）

## 许可证

MIT License

---

**推荐使用GitHub Actions方法，最简单快捷！**
