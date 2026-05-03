# src/STC 头文件详解 & USB 库 API 完全手册

> **时间**：2026-05-02

---

## 1. `src/STC` 目录——9 个头文件各自做什么

| 文件 | 大小 | 用途 | 你需要吗？ |
|------|------|------|----------|
| **`AI8051U.H`** ⭐ | 36KB | AI8051U 所有 SFR 寄存器定义（976行）。P0~P7、定时器、UART、SPI、I2C、ADC、PWM 等的**寄存器地址和位定义** | ✅ 每个项目必须 |
| **`DEF.H`** | 4KB | 通用类型定义：`BYTE`/`WORD`/`u8`/`u16`/`bool`/`TRUE`/`FALSE` 等 | ✅ USB 库依赖 |
| **`STC32_STC8_USB.H`** | 3KB | USB-HID/CDC 库的**函数声明**（usb_init, USB_SendData 等） | ✅ 用 USB 时需要 |
| **`AI_USB.H`** | 3KB | 和 STC32_STC8_USB.H 内容几乎相同（AI 系列版本） | ⚠️ 备选 |
| **`STC32G.H`** | 34KB | STC32G 系列寄存器定义 | ❌ 你用 AI8051U |
| **`STC8051U.H`** | 38KB | STC8051U 系列寄存器定义（8位模式） | ❌ 你用 32 位模式 |
| **`AI32G.H`** | 34KB | AI32G 系列寄存器定义 | ❌ |
| **`AI16F.H`** | 15KB | AI16F 系列寄存器定义 | ❌ |
| **`STC16F.H`** | 15KB | STC16F 系列寄存器定义 | ❌ |

---

## 2. 你需要的是哪三个？

```
┌──────────────────────────────────────────────────────┐
│  main.c                                              │
│    #include "AI8051U.H"       ← 芯片寄存器定义      │
│    #include "stc32_stc8_usb.h" ← USB 库函数声明     │
│              │                                      │
│    stc32_stc8_usb.h                                  │
│      #include "def.h"          ← 类型定义            │
└──────────────────────────────────────────────────────┘
```

---

## 3. USB 库（.LIB）里的 API 和头文件是一一对应的吗？

**是的！** 头文件里声明的每一个函数，.LIB 里都有实现。但 LIB 里还多了很多**没有在头文件中暴露**的内部函数。

```
STC32_STC8_USB.H 声明了:          stc_usb_hid_32g_xdata.LIB 包含:
═══════════════════════          ═══════════════════════════
usb_init()               ←──→   usb_init()  的实现 ✅
USB_SendData()           ←──→   USB_SendData() 的实现 ✅
usb_OUT_done()           ←──→   usb_OUT_done() 的实现 ✅
set_usb_OUT_callback()   ←──→   + 内部实现 ✅
set_usb_ispcmd()         ←──→   + 内部实现 ✅
printf_usb()             ←──→   + 内部实现 ✅
LCD12864_ShowString()    ←──→   + 内部实现 ✅
...                              ...
                         还有大约 80 个未暴露的内部函数:
                                usb_bulk_intr_out()
                                usb_req_std()
                                usb_req_vendor()
                                usb_req_class()
                                usb_common()
                                usb_desc()
                                usb_isr()  ← USB 中断处理
                                ...  (看不到，也不需要知道)
```

> 💡 链接时的 L57 warning 就是那些"存在但你没用到"的未暴露函数——它们被编译进了 LIB 但没有被你的代码调用，链接器就跳过了。

---

## 4. 完整 API 速查手册

### 4.1 USB 核心函数（你最需要的）

| 函数 | 用途 | 使用示例 |
|------|------|---------|
| **`usb_init()`** ⭐ | 初始化 USB + 启动自动下载监听 | `usb_init();` |
| **`USB_SendData(dat, size)`** | 通过 USB-HID 发送数据到电脑 | `USB_SendData(buf, 64);` |
| **`usb_OUT_done()`** | 标记 OUT 数据已处理（准备接收下一包） | `usb_OUT_done();` |
| **`set_usb_OUT_callback(fn)`** | 设置 USB 数据到达的回调函数 | `set_usb_OUT_callback(my_handler);` |
| **`set_usb_ispcmd(cmd)`** | 设置自定义下载命令（默认 `@STCISP#`） | `set_usb_ispcmd("@MYCMD#");` |
| **`set_usb_wait_time(n)`** | 设置 USB 等待周期 | `set_usb_wait_time(40);` |

### 4.2 printf 重定向

| 函数 | 用途 |
|------|------|
| **`printf_usb(fmt, ...)`** | 把 printf 输出重定向到 USB-HID |
| `#define PRINTF_HID` 后 `printf(...)` | 自动映射到 `printf_usb` |

### 4.3 USB 状态变量（全局，可直接读取）

| 变量 | 类型 | 含义 |
|------|------|------|
| **`bUsbOutReady`** | `BOOL` | 电脑发来了数据（=1 时可读 `UsbOutBuffer`） |
| **`bUsbInBusy`** | `BOOL` | USB 正在发送数据（=1 时不要写 `UsbInBuffer`） |
| **`DeviceState`** | `BYTE` | USB 设备状态（0~5，见下） |
| **`OutNumber`** | `BYTE` | 收到的数据字节数 |

### 4.4 USB 数据缓冲区（64 字节 HID 包）

| 缓冲区 | 方向 | 用途 |
|--------|------|------|
| **`UsbOutBuffer[64]`** | 电脑→芯片 | 接收电脑发来的数据 |
| **`UsbInBuffer[64]`** | 芯片→电脑 | 准备发送到电脑的数据 |
| **`UsbFeatureBuffer[64]`** | 双向 | 特性报告（HID Feature Report） |

### 4.5 USB 状态码（DeviceState）

| 宏 | 值 | 含义 |
|-----|-----|------|
| `DEVSTATE_ATTACHED` | 0 | 已连接 |
| `DEVSTATE_POWERED` | 1 | 已供电 |
| `DEVSTATE_DEFAULT` | 2 | 默认状态 |
| `DEVSTATE_ADDRESS` | 3 | 已分配地址 |
| `DEVSTATE_CONFIGURED` | 4 | **已配置（可以通信了！）** |
| `DEVSTATE_SUSPENDED` | 5 | 挂起 |

### 4.6 显示外设函数（需要对应硬件）

| 类别 | 函数数 | 用途 |
|------|--------|------|
| **SEG7（7段数码管）** | 4 | SEG7_ShowString/Long/Float/Code |
| **LED40（40位LED矩阵）** | 4 | LED40_SendData/SetPort/SetBit/ClrBit |
| **LED64（64位LED矩阵）** | 4 | LED64_SendData/SetPort/SetBit/ClrBit |
| **LCD12864** | 15 | 显示/光标/滚动/清屏/字符串/图片 |
| **OLED12864** | 15 | 显示/对比度/滚动/镜像/反色/图片 |

> ⚠️ 这些显示函数需要对应的硬件（数码管/LCD/OLED 等），你现在的板子没有这些外设，**不需要用**。

---

## 5. 你的项目实际可用的 API

去掉不需要的显示外设函数，你现在**实际能用的 USB API**：

```c
// ===== 初始化 =====
usb_init();                              // 启动 USB（含自动下载）
set_usb_ispcmd("@STCISP#");             // 改自定义下载命令（可选）

// ===== 发送数据到电脑 =====
USB_SendData(UsbInBuffer, 64);          // 发送 64 字节 HID 包到电脑
// 或
printf_usb("Hello! ADC=%d\r\n", val);   // printf 风格输出到 USB

// ===== 接收电脑发来的数据 =====
if (bUsbOutReady)                        // 电脑发数据来了
{
    // UsbOutBuffer[0..63] 中有收到的数据
    // 处理...
    usb_OUT_done();                      // 标记处理完毕
}

// ===== 查询 USB 状态 =====
if (DeviceState == DEVSTATE_CONFIGURED)  // USB 已就绪
```

---

## 6. 对比：有库 vs 没有库

| | 没有 USB 库 | 有 USB 库 |
|------|-----------|---------|
| **自动下载** | ❌ 需要手动断电 | ✅ `usb_init()` 一行搞定 |
| **USB 通信** | ❌ 不可能 | ✅ `USB_SendData` / `printf_usb` |
| **代码量** | 基准 | 多 ~6KB (code=7841) |
| **复杂度** | 简单 | 简单（库封装好了） |

---

## 7. 总结

| 问题 | 答案 |
|------|------|
| 头文件各有分工吗？ | ✅ 是的——寄存器、类型、USB API 各司其职 |
| .LIB 和 .H 一一对应？ | ✅ 头文件声明的每个函数 LIB 都有，LIB 还有更多内部函数 |
| 现在有哪些 API 可用？ | USB 核心 6 个 + printf 重定向 + 5 个状态变量 + 3 个缓冲区 |
| 显示函数能用吗？ | 板子没硬件的话用不了（也不建议用） |

---

*💕 一句话：`AI8051U.H` = 芯片身份证，`DEF.H` = 类型字典，`STC32_STC8_USB.H` = USB API 菜单，`.LIB` = 厨房（只管点菜，不用看怎么做）。三个头文件各管一块，加在一起就是你全部的编程接口！*
