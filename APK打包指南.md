# APK打包指南

由于Buildozer和python-for-android在Windows上配置复杂，我们提供以下几种实用的APK打包方案：

## 方案1：使用GitHub Actions自动打包（推荐）

这是最简单的方法，GitHub提供免费的构建环境。

### 步骤：

1. **创建GitHub仓库**
   - 将项目上传到GitHub
   - 确保包含所有必要文件

2. **创建GitHub Actions工作流**
   - 在项目根目录创建`.github/workflows/build-apk.yml`
   - 配置自动构建APK

3. **自动构建**
   - 推送代码后自动触发构建
   - 从Actions页面下载APK

## 方案2：使用Replit在线打包

Replit提供免费的在线开发环境，可以直接打包APK。

### 步骤：

1. 访问 https://replit.com
2. 创建新的Python项目
3. 上传项目文件
4. 在终端运行Buildozer命令
5. 下载生成的APK

## 方案3：使用Colab（Google Colab）

Google Colab提供免费的GPU环境，可以用来打包APK。

### 步骤：

1. 访问 https://colab.research.google.com
2. 创建新的Notebook
3. 运行以下命令安装依赖：

```bash
!pip install buildozer
!buildozer init
!buildozer android debug
```

4. 下载生成的APK

## 方案4：使用WSL（Windows Subsystem for Linux）

在Windows上安装Linux子系统，然后在Linux环境中打包。

### 步骤：

1. **安装WSL**
   ```powershell
   wsl --install
   ```

2. **重启电脑**

3. **在WSL中安装依赖**
   ```bash
   sudo apt update
   sudo apt install -y build-essential git python3 python3-pip openjdk-17-jdk
   pip3 install buildozer
   ```

4. **打包APK**
   ```bash
   cd /mnt/d/自编择日软件/专业级正五行择日软件
   buildozer android debug
   ```

## 方案5：使用Docker

使用Docker容器运行Buildozer。

### 步骤：

1. **安装Docker Desktop**

2. **使用Buildozer Docker镜像**
   ```bash
   docker pull kivy/buildozer
   docker run -it --rm kivy/buildozer
   ```

3. **在容器中打包**

## 当前项目文件清单

确保以下文件都在项目目录中：

- `main.py` - 主入口文件
- `main_kivy_complete.py` - Kivy应用代码
- `buildozer.spec` - Buildozer配置文件
- 其他依赖文件

## 推荐方案

对于Windows用户，我强烈推荐**方案1（GitHub Actions）**或**方案2（Replit）**，因为：

1. 不需要安装复杂的开发工具
2. 使用免费的环境资源
3. 自动化构建，简单方便
4. 可以持续集成和部署

## 立即可用的解决方案

如果您想立即获得APK，可以：

1. 将项目文件上传到Replit
2. 在Replit终端运行：`buildozer android debug`
3. 等待构建完成（可能需要30-60分钟）
4. 下载生成的APK文件

## 注意事项

- 首次构建会下载大量依赖，需要较长时间
- 确保网络连接稳定
- APK文件大小通常在20-50MB之间
- 构建过程需要2-4GB的内存

## 需要帮助？

如果遇到问题，请检查：
1. buildozer.spec配置是否正确
2. 所有依赖文件是否齐全
3. 网络连接是否正常
4. Python版本是否兼容（推荐Python 3.11）

选择最适合您的方案，开始打包APK吧！
