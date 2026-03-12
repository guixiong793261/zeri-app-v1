# GitHub上传和APK打包步骤

## 第一步：安装Git

Git正在自动安装中，请等待安装完成。

如果自动安装失败，您可以手动下载安装：
1. 访问 https://git-scm.com/download/win
2. 下载64位版本
3. 运行安装程序，使用默认设置

## 第二步：创建GitHub账户和仓库

### 2.1 创建GitHub账户
1. 访问 https://github.com
2. 点击 "Sign up" 注册账户
3. 按照提示完成注册

### 2.2 创建新仓库
1. 登录GitHub
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `zeri-app` (或其他名称)
   - Description: `专业级正五行择日软件`
   - 选择 "Public" (公开)
   - 勾选 "Add a README file"
4. 点击 "Create repository"

## 第三步：上传项目文件

### 3.1 打开命令提示符
1. 按 `Win + R`
2. 输入 `cmd`，按回车

### 3.2 进入项目目录
```cmd
cd "D:\自编择日软件\专业级正五行择日软件"
```

### 3.3 初始化Git仓库
```cmd
git init
```

### 3.4 添加所有文件
```cmd
git add .
```

### 3.5 提交更改
```cmd
git commit -m "Initial commit - 专业级正五行择日软件"
```

### 3.6 连接GitHub仓库
将以下命令中的 `YOUR_USERNAME` 替换为您的GitHub用户名：
```cmd
git remote add origin https://github.com/YOUR_USERNAME/zeri-app.git
```

### 3.7 推送到GitHub
```cmd
git branch -M main
git push -u origin main
```

## 第四步：触发自动构建

### 4.1 等待GitHub Actions
1. 推送完成后，访问您的GitHub仓库页面
2. 点击顶部的 "Actions" 标签
3. 您会看到 "Build Android APK" 工作流正在运行

### 4.2 监控构建进度
- 构建过程约需30-60分钟
- 首次构建会下载大量依赖，时间较长
- 可以在Actions页面查看实时日志

## 第五步：下载APK

### 5.1 构建完成后
1. 在Actions页面点击最新的构建记录
2. 向下滚动到 "Artifacts" 部分
3. 点击 "zeri-app-apk" 下载APK文件

### 5.2 安装APK
1. 将APK文件传输到Android设备
2. 在设备上允许安装未知来源应用
3. 安装APK

## 常见问题

### Q: 推送时出现认证错误？
A: 需要使用GitHub Personal Access Token：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择 "repo" 权限
4. 生成token并复制
5. 推送时输入token作为密码

### Q: 构建失败怎么办？
A: 检查以下几点：
1. 所有必要文件是否已上传
2. buildozer.spec配置是否正确
3. 查看Actions日志中的错误信息

### Q: 如何更新应用？
A: 修改代码后：
```cmd
git add .
git commit -m "更新说明"
git push
```
GitHub Actions会自动重新构建。

## 文件清单

确保以下文件都已上传到GitHub：
- ✅ main.py
- ✅ main_kivy_complete.py
- ✅ buildozer.spec
- ✅ .github/workflows/build-apk.yml
- ✅ README.md

## 需要帮助？

如果在任何步骤遇到问题，请告诉我具体的错误信息，我会帮您解决。

---

**现在让我们开始吧！**

1. 首先访问 https://github.com 创建账户
2. 创建新仓库
3. 按照上面的步骤上传代码
4. 等待自动构建完成
5. 下载APK文件

整个过程大约需要1-2小时（主要是构建时间）。
