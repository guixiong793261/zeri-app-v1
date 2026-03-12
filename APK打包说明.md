# 择日软件APK打包说明

## 概述
本文档说明如何将Python择日软件打包为Android APK文件。

## 方案说明

### 方案一：使用Buildozer + Kivy（当前方案）

**优点：**
- 免费开源
- 支持完整的Python功能
- 可以访问Android原生API

**缺点：**
- 需要Linux环境（推荐Ubuntu）
- 打包时间较长（首次约30-60分钟）
- APK文件较大（约20-50MB）

## 打包步骤

### 1. 准备工作

#### 安装Linux环境
- 推荐使用Ubuntu 20.04或更高版本
- 或者使用Windows Subsystem for Linux (WSL2)

#### 安装依赖
```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装必要依赖
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk

# 安装Buildozer
pip3 install buildozer

# 安装Cython
pip3 install cython
```

### 2. 项目准备

#### 文件结构
```
专业级正五行择日软件/
├── main_kivy.py          # Kivy版本主程序
├── buildozer.spec        # Buildozer配置文件
├── 择日软件_完整单文件版_小窗口.py  # 原始程序
└── APK打包说明.md        # 本说明文档
```

#### 修改main_kivy.py
需要将原有的计算逻辑从`择日软件_完整单文件版_小窗口.py`移植到`main_kivy.py`中。

当前`main_kivy.py`是一个框架，需要：
1. 复制原有的天干地支数据
2. 复制四柱计算函数
3. 复制评分算法
4. 完善界面交互

### 3. 打包命令

```bash
# 进入项目目录
cd 专业级正五行择日软件

# 初始化buildozer（如果还没有buildozer.spec）
buildozer init

# 开发调试模式
buildozer android debug deploy run

# 仅打包APK（调试版）
buildozer android debug

# 打包发布版APK
buildozer android release
```

### 4. 输出文件

打包完成后，APK文件位于：
```
bin/zeriapp-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

## 常见问题

### 1. 打包失败 - 内存不足
**解决：** 增加交换空间
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 2. 打包失败 - 网络问题
**解决：** 配置代理或使用国内镜像
```bash
# 配置git代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### 3. 应用闪退
**解决：** 
- 检查日志：`adb logcat | grep python`
- 确保所有依赖都在buildozer.spec中声明
- 检查Python代码是否有平台相关的问题

### 4. APK太大
**解决：**
- 在buildozer.spec中减少archs数量
- 移除不必要的依赖
- 使用`android.release_artifact = aab`生成AAB格式

## 替代方案

### 方案二：使用Pydroid 3（简单但有限制）
- 在Android设备上安装Pydroid 3应用
- 直接运行Python代码
- 无法生成独立APK

### 方案三：使用Chaquopy（商业方案）
- 在Android Studio中使用
- 需要购买许可证
- 更好的性能和集成

### 方案四：使用Termux（技术用户）
- 在Android上安装Termux
- 安装Python环境
- 运行原始Python程序

## 下一步工作

要将当前框架完善为可用应用，需要：

1. **移植计算逻辑**
   - 从原文件复制所有计算函数
   - 确保四柱计算、评分算法完整

2. **完善界面**
   - 添加更多输入控件
   - 优化结果显示
   - 添加图表展示

3. **测试验证**
   - 在模拟器上测试
   - 在真实设备上测试
   - 验证计算结果准确性

4. **优化性能**
   - 减少APK体积
   - 优化启动速度
   - 处理大日期范围计算

## 技术支持

如需帮助，可以：
- 查阅Buildozer文档：https://buildozer.readthedocs.io/
- 查阅Kivy文档：https://kivy.org/doc/stable/
- 在GitHub上提交issue

## 注意事项

1. **版权问题**：确保使用的库都有合适的许可证
2. **隐私政策**：如果收集用户数据，需要添加隐私政策
3. **应用商店**：发布到Google Play需要遵守相关政策
4. **签名证书**：发布版需要使用自己的签名证书

---

**当前状态：** 已创建Kivy框架和Buildozer配置，需要完善计算逻辑后才能打包。
