# USB HID 与 CDC 设备区别 & STC AI8051U 烧录模式详解

## 一、问题
1. USB HID 和 CDC 设备有什么区别？
2. 为什么 STC AI8051U 可以选择 HID 或 CDC 烧录？会有什么区别？

## 二、USB 设备类（Device Class）基础

在 USB 协议中，设备通过**设备类代码（bDeviceClass）**告诉主机"我是什么类型的设备"，
这样操作系统就可以加载对应的标准驱动程序，无需厂商自定义驱动。

### 2.1 HID（Human Interface Device） - 人机接口设备

**USB-IF 规范**：Device Class Definition for Human Interface Devices (HID)
**Class Code**：`0x03`

| 特性 | 说明 |
|------|------|
| **定位** | 人机交互设备（键盘、鼠标、游戏手柄等） |
| **传输方式** | **中断传输（Interrupt Transfer）** |
| **最大带宽** | 全速: 64KB/s，高速: 每微帧 1024B |
| **免驱** | ✅ **所有操作系统原生支持，无需安装驱动** |
| **延迟** | 低延迟（中断传输有保证的轮询间隔） |
| **典型应用** | 键盘、鼠标、游戏手柄、触摸屏、自定义 HID 设备 |

**核心特点**：
- HID 协议使用**中断端点**通信，主机以固定间隔轮询设备
- 全速设备（12Mbps）：每 1~255ms 一个 IN 事务，每包最多 64 字节
- 高速设备（480Mbps）：每微帧（125μs）最多 1024 字节
- **天生免驱** — 这是 HID 最大的优势

### 2.2 CDC（Communication Device Class） - 通信设备类

**USB-IF 规范**：Class definitions for Communication Devices
**Class Code**：`0x02`

| 特性 | 说明 |
|------|------|
| **定位** | 通信设备（网卡、调制解调器、虚拟串口等） |
| **子类 ACM** | Abstract Control Model — 模拟传统串口 |
| **传输方式** | 控制传输 + **批量传输（Bulk Transfer）** |
| **免驱** | ⚠️ **需安装 .inf 驱动（Win10/11 内置 usbser.sys）** |
| **带宽** | 批量传输可占满剩余总线带宽 |
| **典型应用** | USB 转串口、USB 网卡、USB 虚拟 COM 口 |

**核心特点**：
- CDC-ACM（Abstract Control Model）是最常用的子类，用于**虚拟串口**
- CDC 需要向主机上报 Line Coding（波特率、数据位、停止位、校验位）
- Windows 10/11 内置了 `usbser.sys` 驱动，但需要 .inf 文件声明兼容 ID
- Linux/macOS 原生支持 CDC-ACM，直接识别为 `/dev/ttyACM0`
- **批量传输充分利用带宽**，数据吞吐量比 HID 大得多

### 2.3 直观对比表

| 维度 | HID | CDC |
|------|-----|-----|
| USB Class Code | 0x03 | 0x02 |
| 操作系统识别 | 键盘/鼠标/自定义HID | 串口 (COM口) |
| 需要驱动？ | ❌ 不需要 | ⚠️ Windows 需要（Win10+内置） |
| 传输模式 | 中断传输 | 批量传输 |
| 速度上限 | ~64KB/s（全速） | 接近总线带宽（批量） |
| 典型用途 | 游戏手柄、ISP烧录 | 虚拟串口、printf调试、仿真 |
| 延迟 | 低延迟 | 批量传输可能排队 |

---

## 三、STC AI8051U 的 USB 模式详解

### 3.1 为什么 AI8051U 可以选择 HID 或 CDC 烧录？

AI8051U 内置了**硬件 USB 控制器**和**系统区 ISP Bootloader**。

芯片上电时，芯片会根据 P3.2 引脚电平决定进入哪种模式：
- **P3.2 = 1（高电平）** → 运行用户代码
- **P3.2 = 0（低电平/接地）+ 冷启动** → 进入 ISP 模式

在 ISP 模式下，Bootloader 通过 D-/P3.0 和 D+/P3.1 枚举为一个 USB 设备。
STC 的 Bootloader **同时支持两种设备类协议**，用户可以在 STC-ISP 软件中选择。

### 3.2 HID 模式（STC 推荐！）

来自 STC 官方技术手册原文：

> "现在 STC 的带硬件 USB 的 MCU 支持用硬件 USB 下载，因为用的是
>  **USB-HID 通信协议，不需要安装任何驱动**。"

**STC-ISP 软件中识别为**：`STC USB Writer (HID1)`

**操作流程**：
1. D-/P3.0, D+/P3.1 连接电脑 USB
2. 按住 P3.2 接地 → 芯片上电（冷启动）
3. STC-ISP 自动识别出 `STC USB Writer (HID1)`
4. 松开 P3.2 → 点击"下载/编程"

**优点**：
- ✅ 无需任何驱动，插上就能用
- ✅ Win7/8/10/11 全兼容
- ✅ 支持"不停电下载"（`@STCISP#` 命令）
- ✅ 支持自动调节内部 IRC 频率（硬件 USB 独有）

**缺点**：
- ⚠️ HID 中断传输每包最多 64 字节（全速），速度不如批量传输
- ⚠️ 不能同时用于 printf 调试输出（HID 没有串口语义）

### 3.3 CDC 模式（用于仿真和调试）

来自 STC 官方技术手册：

> "当使用 USB-CDC 串口 1 进行仿真的同时，还可以使用
>  USB-CDC 串口 2 调试程序中的串口模块。"

**STC-ISP 软件中识别为**：`STC USB Writer (CDC1)` 或串口号

**操作流程**：
1. D-/P3.0, D+/P3.1 连接电脑 USB
2. 在 STC-ISP 中选择 "USB-CDC 模式"
3. 按住 P3.2 → 冷启动 → 点击下载

**优点**：
- ✅ 批量传输，烧录速度快
- ✅ 可以同时用于虚拟串口通信（printf 调试、数据收发）
- ✅ 支持多个 CDC 串口（仿真 + 调试同时进行）

**缺点**：
- ⚠️ **Windows 下需要安装驱动**（STC-ISP 软件中提供一键安装）
- ⚠️ Linux 下原生支持

### 3.4 你的项目用什么模式？

你的项目（AiCube 生成）实际上**混合使用了两种模式**：

| 功能 | 协议 | 说明 |
|------|------|------|
| **ISP 烧录** | HID | `set_usb_ispcmd("@STCISP#")` — 不停电下载命令 |
| **printf 调试输出** | CDC | `PRINTF_USB` 宏 — printf 重定向到 USB 虚拟串口 |
| **数据收发** | CDC | `USBLIB_OUT_Done()` — 接收 PC 数据并回传 |

你代码中的：
```c
usb_init();                  // USB设备初始化（枚举为 CDC + HID 复合设备?）
set_usb_ispcmd("@STCISP#");  // 设置不停电下载命令（HID协议）
```

`@STCISP#` 是 STC 约定的自定义命令，当用户程序收到这个字符串时，
会自动软复位到 ISP 区，实现 "不停电下载"——也就是说你改了代码重新编译后，
不用再手动按 P3.2 + 断电上电了，STC-ISP 软件自动帮你复位！

---

## 四、总结

|  | HID 烧录 | CDC 烧录 |
|------|---------|---------|
| **驱动** | ❌ 不需要 | ⚠️ 需要（Win） |
| **即插即用** | ✅ 最好 | ⚠️ 需先装驱动 |
| **速度** | 较慢（中断传输） | 较快（批量传输） |
| **printf 调试** | ❌ 不支持 | ✅ 虚拟串口 |
| **仿真调试** | ❌ 不支持 | ✅ CDC 仿真 |
| **推荐场景** | 日常烧录、现场升级 | 调试开发、需要串口通信 |
| **STC 推荐** | ✅✅✅ 首选 | 特定场景用 |

---

## 五、参考来源

1. **USB 2.0 Specification** (文件: `USB 2.0 协议usb_20.pdf`)
   - §4.8 (Page 50): *"USB devices are divided into device classes such as hub, **human interface**, printer, imaging, or mass storage device."*
   - §4.8.1 (Page 50): *"Standard information ... includes vendor identification, **device class**, and power management capability."*
   - §4.8.2.2 (Page 52): *"A **human interface device** such as a mouse, keyboard, tablet, or game controller"*
   - §5.5 (Page 66): *"**Control transfers** allow access to different parts of a device."*
   - §5.5.3 (Page 67): *"The allowable maximum control transfer data payload sizes for full-speed devices is 8, 16, 32, or **64 bytes**"*
   - Page 30: *"This document is complemented and referenced by the **Universal Serial Bus Device Class Specifications**."*（说明 HID/CDC 细节在独立类规范中）
2. **USB Device Class Definition for HID** — USB-IF HID 规范
3. **USB Device Class Definition for CDC** — USB-IF CDC 规范（ACM 子类）
4. **STC8H 系列单片机技术参考手册** — 第 129-137 页，USB ISP 下载章节
   > "STC 的带硬件USB 的MCU 支持用硬件USB 下载，因为用的是USB-HID 通信协议，不需要安装任何驱动"
5. **STC32G 系列单片机技术参考手册** — 第 132-137 页，USB 下载模式
   > "选择 USB(HID)模式，并设置USB 设备的VID 和PID"
   > "必须将STC 提供的 stc_usb_hid.lib 代码库添加到项目中"
