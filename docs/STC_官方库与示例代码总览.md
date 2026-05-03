# STC 官方库和示例代码总览

> **时间**：2026-05-02
> **来源**：STC 官网、AiCube ISP 内置工具、手册

---

## 1. STC 有"库"吗？

和 STM32 的 HAL 库不同——STC **没有**像 `HAL_GPIO_WritePin()` 那样的完整硬件抽象层。STC 的"库"更接近**寄存器封装函数 + 示例代码**。

```
STM32 风格:  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);  // ❌ STC 没有
STC 风格:    P42 = ~P42;                              // ✅ 直接操作寄存器
             GPIO_Toggle(P4, PIN_2);                  // ✅ 库函数封装
```

---

## 2. STC 官方库函数

| 库 | 适用芯片 | 下载 |
|-----|---------|------|
| **STC32G 库函数** | STC32G12K128 | https://www.stcmicro.com/slcx.html |
| **STC8G/8H 库函数** | STC8G/8H 系列 | 同上 |
| **STC8A8K64D4 库函数** | STC8A 系列 | 同上 |
| **STC15 库函数** | STC15 系列 | 同上 |

> ⚠️ **AI8051U 目前没有独立的库函数包**。但 AI8051U 和 STC32G 都是 80251 核心，STC32G 的库**基本兼容**。

---

## 3. STC USB 库（⭐ 最有用）

STC 提供官方的 **USB-CDC** 和 **USB-HID** 库：

```
下载地址:
https://www.stcaimcu.com/data/download/Library/STC_USB_LIBRARY.zip

包含:
├── STC-HID 范例程序（查询方式）
├── STC-HID 范例程序（中断方式）
├── STC-HID 库文件
├── STC-CDC 范例程序
├── STC-CDC 库文件
└── ...
```

| 库 | 协议 | 速度 | 驱动 | 用途 |
|-----|------|------|------|------|
| **USB-CDC** | 虚拟串口 | 800KB/s | Win10+ 免驱动 | 高速数据传输 |
| **USB-HID** | 人机接口 | 64KB/s | 全系统免驱动 | 小数据量、键盘鼠标 |

---

## 4. 示例代码包（Demo Code）

STC 官网提供的 Demo 代码：

| 包名 | 内容 |
|------|------|
| **STC32G-DEMO-CODE** | 定时器、UART、SPI、I2C、ADC、PWM、USB 等综合范例 |
| **STC8H-DEMO-CODE** | STC8H 系列范例 |
| **FreeRTOS-STC32G-CANOpen** | STC32G 上跑 FreeRTOS + CANOpen |
| **STC32G-User-UART-ISP-Bootloader** | 自定义串口 Bootloader |
| **STC32G-User-USB-ISP-Bootloader** | 自定义 USB Bootloader |
| **STC32G-User-CAN-ISP-Bootloader** | 自定义 CAN Bootloader |

---

## 5. AiCube ISP 内置工具

AiCube ISP 不仅仅是烧录工具，还内置了：

| 工具 | 位置 |
|------|------|
| **头文件导出** | "头文件" 标签 → 导出 AI8051U.H |
| **代码生成器** | 波特率计算、定时器配置 |
| **范例程序** | 内置各种外设的示例代码 |
| **EEPROM 编辑器** | 在线编辑/读取 EEPROM |
| **串口助手** | 调试用串口工具 |

---

## 6. 已经在你项目里的

| 文件 | 用途 |
|------|------|
| `src/STC/AI8051U.H` | 寄存器定义（976 行，所有外设） |
| `src/STC/AI_USB.H` | USB 相关定义 |
| `src/STC/STC32_STC8_USB.H` | USB 库函数声明 |

> 你的项目里已经有 STC 的 USB 头文件了！可以直接用。

---

## 7. AI8051U 可用的库层次

```
            ┌────────────────────────────────┐
            │  STC USB 库 (CDC/HID)          │ ← 下载后直接用
            │  官方提供的 USB 通信封装        │
            ├────────────────────────────────┤
            │  STC32G 库函数                  │ ← 基本兼容 AI8051U
            │  定时器/UART/SPI/I2C 等封装     │
            ├────────────────────────────────┤
            │  AI8051U.H 头文件               │ ← 你已有了
            │  所有寄存器位定义               │
            ├────────────────────────────────┤
            │  直接寄存器操作                  │ ← 你现在用的
            │  P42 = 0; TMOD = 0x01; 等       │
            └────────────────────────────────┘
```

---

## 8. 推荐下载（如果你需要）

| 下载什么 | 链接 |
|---------|------|
| **STC USB 库**（最有用） | https://www.stcaimcu.com/data/download/Library/STC_USB_LIBRARY.zip |
| **STC32G Demo Code** | https://www.stcmicro.com/slcx.html |
| **STC32G 库函数** | 同上 |
| **STC-ISP 最新版** | https://www.stcmicro.com/rjxz.html |

---

## 9. 总结

| 问题 | 答案 |
|------|------|
| STC 有 HAL 库吗？ | ❌ 没有完整的 HAL，只有寄存器封装 |
| AI8051U 有专属库吗？ | ⚠️ 没有，但 STC32G 库基本兼容 |
| USB 有库吗？ | ✅ 有！CDC 和 HID 官方库 |
| 怎么下载？ | 官网 slcx.html + STC_USB_LIBRARY.zip |
| 你现在需要吗？ | 闪灯项目不需要，加 USB 通信时需要 |

---

*💕 结论：STC 不像 STM32 那样有 HAL 库，但有寄存器封装 + 丰富的 Demo 代码 + USB 专用库。对于简单项目直接操作寄存器就够了，要加 USB 功能时再用官方 USB 库~*
