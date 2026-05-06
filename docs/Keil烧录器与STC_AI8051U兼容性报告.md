# Keil 烧录器与 STC AI8051U 兼容性调研

> 📅 日期：2026年5月6日  
> 📚 来源：Keil 官方文档、STC 芯片手册、STC-ISP 官方工具、项目已有文档

---

## 一、结论速览

| 问题 | 答案 |
|------|------|
| Keil 内置烧录器能烧 AI8051U 吗？ | ❌ **不能** |
| Keil 能联动烧录工具吗？ | ✅ 可以，通过 "External Tool" 机制 |
| 用什么烧录？ | STC 官方工具：**AiCube-ISP** |
| 支持几种接口？ | UART / USB-HID / USB-CDC 三种 |

---

## 二、Keil 内置烧录器为什么不支持？

Keil uVision 的内置 Flash Programming 机制依赖于**调试适配器硬件**：

| 适配器 | 支持芯片 | 支持 STC？ |
|--------|---------|-----------|
| ULINK2/ULINKpro | ARM Cortex-M | ❌ |
| J-Link | ARM / Renesas | ❌ |
| ST-Link | STM8/STM32 | ❌ |
| 第三方 CMSIS-DAP | ARM | ❌ |

> STC 芯片使用**私有 ISP 协议**（In-System Programming），不遵循标准的 SWD/JTAG 调试协议。Keil 的 UV4 项目文件中 `<InvalidFlash>1</InvalidFlash>` 也确认了这一点。

---

## 三、AI8051U 的三种烧录方式

### 方式 A：USB-HID（⭐ 推荐，免驱动）

```
电脑 USB ──→ AI8051U USB 口（直接 USB 线连接）
                │
                └── AiCube-ISP 通过 USB-HID 协议烧录
```

- ✅ 不需要 USB-TTL 模块
- ✅ 不需要装驱动（Windows 自带 HID 驱动）
- ✅ 支持"免断电自动下载"

### 方式 B：USB-CDC（虚拟串口）

```
电脑 USB ──→ AI8051U USB 口
                │
                └── 识别为 COM 口 → AiCube-ISP 通过串口协议烧录
```

- ⚠️ 需要装 STC-CDC 驱动
- ✅ 可以同时当串口调试用

### 方式 C：UART 串口

```
电脑 USB ──→ USB-TTL ──→ AI8051U P3.0(RXD) / P3.1(TXD)
```

- ⚠️ 需要额外硬件（USB-TTL 模块）
- ⚠️ 需要手动断电/上电进入 ISP 模式

---

## 四、免断电自动下载（最省事的方案）

AI8051U 支持在用户程序运行时通过 USB 接收 ISP 命令，软件复位到 ISP 区：

```
你的程序运行中            AiCube-ISP 检测到 HEX 变化
      │                          │
      │  收到 "@STCISP#" 命令    │
      │  IAP_CONTR = 0x60        │
      │  ↓                       │
      │  CPU 复位到 ISP 区        │
      │                          ↓
      │                   自动开始烧录！🔥
```

> 参考：项目文档 `docs/AI8051U_免断电自动下载方案.md`

---

## 五、Keil 联动 STC-ISP 烧录

虽然 Keil 不能直接烧录，但可以配置成**编译完成后自动调用 STC-ISP**：

### 配置方法

1. Keil → **Options for Target** → **Utilities** 选项卡
2. 勾选 **Use External Tool for Flash Programming**
3. **Command**: 填写 `tools\AiCube-ISP-v6.96V-plus.exe`
4. **Arguments**: 填写 `/auto Objects\03-March_Wheel_leg_FOC.hex`
5. 勾选 **Run Independent**（后台运行）

### 效果

```
Keil F7 编译 ──→ 生成 HEX ──→ 自动启动 AiCube-ISP ──→ 自动烧录
```

> ⚠️ 需要先配置 AiCube-ISP 的芯片型号和接口类型，首次使用需手动选择。

---

## 六、我们的 builder.rs 已经支持烧录

```powershell
cargo +nightly -Zscript tools\builder.rs flash
```

这个命令直接调用 `tools\AiCube-ISP-v6.96V-plus.exe` 烧录最新的 HEX 文件。

---

## 七、总结

| 烧录方式 | 可用性 | 推荐度 |
|---------|--------|--------|
| Keil 内置 | ❌ 不支持 | — |
| AiCube-ISP 手动 | ✅ | ⭐⭐ |
| AiCube-ISP 自动联动 | ✅ | ⭐⭐⭐ |
| builder.rs flash | ✅ | ⭐⭐⭐ |
| USB-HID 免断电下载 | ✅ | ⭐⭐⭐⭐ |
