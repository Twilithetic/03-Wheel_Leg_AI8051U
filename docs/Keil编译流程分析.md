# AI8051U FOC 项目 — Keil 编译流程分析

> 分析日期：2026-05-11  
> 基于文件：`03-March_Wheel_leg_FOC.uvproj` + `.uvopt` + `build_log.htm` + `.lnp`

---

## 一、项目概览

| 属性 | 值 |
|------|-----|
| **芯片** | AI8051U-32Bit Series（80251 兼容内核，32位模式） |
| **厂商** | AI (STC) |
| **Keil IDE** | μVision V5.38.0.0 |
| **工具链** | PK251 Prof. Developers Kit V5.60.0.0 |
| **安装路径** | `C:\Keil_v5\C251\BIN\` |
| **主频** | 35 MHz (CLOCK=35000000) |

### 三类项目文件对比

| 项目文件 | 源文件 | USB 库 | 用途 |
|----------|--------|--------|------|
| `03-March_Wheel_leg_FOC.uvproj` | 仅 `main.c` | CDC (`stc_usb_cdc_32g_xdata.lib`) | **当前主力** |
| `03-March_Wheel_leg_FOC_bk1.uvproj` | main.c + port.c + clock.c + usblib.c + mathlib.c | CDC | 备份/多文件版本 |
| `03-March_Wheel_leg_FOC_bk2.uvproj` | 同上 | **HID** (`stc_usb_hid_32g_xdata.lib`) | USB-HID 模式备份 |

> ⚠️ 注意：当前 `Sources/` 目录下**只有 `main.c`**！  
> `port.c`、`clock.c`、`usblib.c`、`mathlib.c` 已被移除，但 `Objects/` 目录下仍残留之前构建的 `.crf` 文件。  
> 头文件 `config.h` 仍引用了它们，但因为 Keil 只编译 `main.c`（不编译头文件），所以并无影响。

---

## 二、完整的 Keil 编译流程

Keil μVision 对 MCS-251 项目的构建分为 **3 个阶段**，由 `.uvproj` XML 配置驱动：

```
┌─────────────────────────────────────────────────────┐
│               Keil μVision "Build" 按钮             │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  阶段 0：Before Compile（用户自定义前置命令）        │
│  当前未配置，跳过                                    │
├─────────────────────────────────────────────────────┤
│  阶段 1：编译 (Compile)                              │
│  ├─ 对每个 FileType=1（C源文件）执行 C251.EXE       │
│  ├─ 对每个 FileType=2（汇编文件）执行 A251.EXE       │
│  └─ .c → .obj，同时生成 .lst 列表文件                │
├─────────────────────────────────────────────────────┤
│  阶段 2：链接 (Link/Locate)                          │
│  ├─ L251.EXE 链接所有 .obj + .lib                   │
│  ├─ 定位内存中的 CODE/XDATA/DATA 段                  │
│  ├─ 生成 .map 内存映射文件                           │
│  └─ 调用 OH251.EXE 将最终二进制转 .hex               │
├─────────────────────────────────────────────────────┤
│  阶段 3：After Make（用户自定义后置命令）             │
│  当前未配置，跳过                                    │
└─────────────────────────────────────────────────────┘
```

---

## 三、阶段 1 详解：C251 编译器

### 3.1 工具信息

| 编译器 | 路径 | 版本 |
|--------|------|------|
| **C251.EXE** | `C:\Keil_v5\C251\BIN\C251.EXE` | V5.60.0.0 |
| **A251.EXE**（汇编器） | 同上 | V4.69.13.0 |

### 3.2 被编译的文件

根据主 `.uvproj` 文件 `<Groups>` 部分：

```xml
<Group>
  <GroupName>User Sources</GroupName>
  <!-- 空组，无文件 -->
</Group>
<Group>
  <GroupName>AiCube</GroupName>
  <Files>
    <File>
      <FileName>main.c</FileName>
      <FileType>1</FileType>     <!-- 1 = C源文件 -->
      <FilePath>.\Sources\main.c</FilePath>
    </File>
    <File>
      <FileName>ai8051u_32_mdu32.lib</FileName>
      <FileType>4</FileType>     <!-- 4 = 库文件 -->
      <FilePath>.\Sources\lib\ai8051u_32_mdu32.lib</FilePath>
    </File>
    <File>
      <FileName>ai8051u_32_tfpu.lib</FileName>
      <FileType>4</FileType>
      <FilePath>.\Sources\lib\ai8051u_32_tfpu.lib</FilePath>
    </File>
    <File>
      <FileName>stc_usb_cdc_32g_xdata.lib</FileName>
      <FileType>4</FileType>
      <FilePath>.\Sources\lib\stc_usb_cdc_32g_xdata.lib</FilePath>
    </File>
  </Files>
</Group>
```

> **结论：当前项目只编译 1 个源文件 `main.c`，链接 3 个库文件。**

### 3.3 C251 编译选项（从 `.uvproj` 提取）

`.uvproj` 中 `<C251>` 节点定义了编译选项，这些选项映射到 C251.EXE 的命令行参数：

| XML 配置 | 值 | 对应命令行选项 | 含义 |
|----------|-----|---------------|------|
| `<MemoryModel>` | 4 | **`LARGE`** | 大内存模型：默认变量在 XDATA |
| `<RomSize>` | 3 | **`ROM(LARGE)`** | 大 ROM：支持 16MB 代码空间 (>64KB) |
| `<uFrame4>` | 1 | **`INTR2`** | 🔑 中断帧 4 字节（8051 兼容行为）|
| `<uSrcBin>` | 1 | **`SRC`** | 生成汇编源文件 |
| `<Optim>` | 7 | **`OPTIMIZE(7)`** | 优化级别 7（侧重速度，公共子表达式消除、循环优化）|
| `<SizSpd>` | 1 | **`SPEED`** | 优化侧重执行速度 |
| `<wLevel>` | 2 | **`WARNINGLEVEL(2)`** | 警告级别 2 |
| `<uAlias>` | 1 | **`NOALIAS`** | 禁止指针别名假设 |
| `<Fuzzy>` | 3 | **`FUZZY(3)`** | 模糊匹配级别 |
| `<uOrder>` | 0 | 默认 | 变量声明顺序 |
| `<IncludePath>` | `.\Sources\inc` | **`INCDIR(.\Sources\inc)`** | 头文件搜索路径 |

### 3.4 C251.EXE 实际命令行

Keil IDE 实际执行的编译命令（等价于）：

```batch
C251.EXE main.c ^
  LARGE ^
  ROM(LARGE) ^
  INTR2 ^
  OPTIMIZE(7, SPEED) ^
  WARNINGLEVEL(2) ^
  DEBUG ^
  SYMBOLS ^
  INCDIR(.\Sources\inc) ^
  OBJECT(.\Objects\main.obj) ^
  PRINT(Listings\main.lst)
```

---

## 四、阶段 2 详解：L251 链接器

### 4.1 工具信息

| 工具 | 路径 | 版本 |
|------|------|------|
| **L251.EXE** | `C:\Keil_v5\C251\BIN\L251.EXE` | V4.66.93.0 |
| **OH251.EXE** | 同上 | V1.47.0.0（HEX 转换器） |

### 4.2 链接器输入（`.lnp` 文件）

L251 的输入由 `.lnp` 链接器命令文件定义（`Objects\03-March_Wheel_leg_FOC.lnp`）：

```
".\Objects\main.obj",
".\Sources\lib\ai8051u_32_mdu32.lib",
".\Sources\lib\ai8051u_32_tfpu.lib",
".\Sources\lib\stc_usb_cdc_32g_xdata.lib"
TO ".\Objects\03-March_Wheel_leg_FOC"
PRINT(".\Listings\03-March_Wheel_leg_FOC.map")
CASE DISABLEWARNING (16)
REMOVEUNUSED, NOOVERLAY
CLASSES (EDATA (0x0-0x7FF), HDATA (0x0-0x7FF))
```

### 4.3 链接器选项

| 选项 | 含义 |
|------|------|
| **`REMOVEUNUSED`** | 移除未被调用的库函数、未使用的段 |
| **`NOOVERLAY`** | 禁止函数间数据覆盖（简化调试，但会增加 DATA 用量） |
| **`DISABLEWARNING(16)`** | 禁用警告 16（未调用段警告） |
| **`CASE`** | 符号大小写敏感 |
| **`CLASSES (EDATA..., HDATA...)`** | 定义内存类（从 Target 内存配置自动生成） |

### 4.4 内存布局配置

从 `.uvproj` 的 `<OnChipMemories>` 提取：

| 内存区域 | 起始地址 | 大小 | 说明 |
|----------|----------|------|------|
| **RCB** | 0x000000 | 64KB | Root Code Bank（近代码区，≤64KB 可直接寻址） |
| **IROM** | 0xFF0000 | 64KB | 内部 ROM（中断向量表在 FF:0000） |
| **IRAM** | 0x0000 | 2KB | 内部 RAM（DATA/IDATA 区） |
| **XRAM** | 0x10000 | 32KB | 外部 RAM（XDATA 区） |

对应的内存模型配置：
```xml
<MemoryModel>4</MemoryModel>    <!-- LARGE: 默认变量在 XDATA -->
<RomSize>3</RomSize>            <!-- LARGE: 代码空间 >64KB -->
<hadIRAM>1</hadIRAM>            <!-- 片内有 IRAM -->
<hadXRAM>1</hadXRAM>            <!-- 片内有 XRAM -->
<hadIROM>1</hadIROM>            <!-- 片内有 IROM -->
```

### 4.5 输出文件

| 输出 | 路径 | 说明 |
|------|------|------|
| **`.hex`** | `Objects\03-March_Wheel_leg_FOC.hex` | Intel HEX 格式，烧录文件 |
| **`.map`** | `Listings\03-March_Wheel_leg_FOC.map` | 内存映射表（CODE/XDATA/DATA 段分布） |
| **无扩展名** | `Objects\03-March_Wheel_leg_FOC` | OMF251 格式的绝对目标文件 |

---

## 五、库文件详解

### 5.1 三件套（缺一不可）

| 库文件 | 功能 | 大小 |
|--------|------|------|
| **`ai8051u_32_mdu32.lib`** | MDU32 硬件乘除法单元驱动 | AI8051U 的 32位硬件乘除器 |
| **`ai8051u_32_tfpu.lib`** | TFPU 硬件浮点单元驱动 | AI8051U 的 32位硬件浮点运算器 |
| **`stc_usb_cdc_32g_xdata.lib`** | USB CDC 虚拟串口库 | USB 通信栈（CDC ACM 模式，xdata 版本）|

### 5.2 USB 库版本差异

| 库文件 | 通信模式 | 用途 |
|--------|----------|------|
| `stc_usb_cdc_32g_xdata.lib` | **CDC (虚拟串口)** | 当前使用，支持 USB 虚拟 COM 口 |
| `stc_usb_hid_32g_xdata.lib` | **HID (人机接口)** | bk2 备份项目，用于无驱 HID 通信 |

---

## 六、实际构建结果

从 `Objects\03-March_Wheel_leg_FOC.build_log.htm`：

```
Build target '03-March_Wheel_leg_FOC'
linking...
Program Size: data=8.3 edata+hdata=256 xdata=397 const=53 code=8206
creating hex file from ".\Objects\03-March_Wheel_leg_FOC"...
".\Objects\03-March_Wheel_leg_FOC" - 0 Error(s), 0 Warning(s).
Build Time Elapsed:  00:00:00
```

| 段 | 大小 | 说明 |
|-----|------|------|
| **data** | 8.3 字节 | DATA 区（直接寻址的低128字节） |
| **edata+hdata** | 256 字节 | EDATA（扩展 DATA，间接寻址的 256 字节）+ HDATA |
| **xdata** | 397 字节 | XDATA 区（外部 RAM，0x10000 起） |
| **const** | 53 字节 | 常量区 |
| **code** | 8206 字节 | 代码区（约 8KB，在 64KB IROM 内很宽裕） |

---

## 七、编译器选项 `INTR2` 的重要性

这是整个项目中**最关键也最容易出错**的编译选项。

### 7.1 原理

AI8051U 是 32 位 80251 兼容内核，在二进制模式下有两种中断帧大小：

| 中断模式 | 中断帧大小 | 入栈操作 | 对应选项 |
|----------|-----------|---------|---------|
| **8051 兼容** | 4 字节 | `PUSH PSW1; PUSH PC[23:16]; PUSH PC[15:8]; PUSH PC[7:0]` | **`INTR2`** |
| **251 原生** | 10 字节 | 额外保存 WR0, WR2, WR4, WR6 等寄存器 | 默认行为 |

### 7.2 为什么必须一致

STC 官方提供的三个库（`ai8051u_32_mdu32.lib`、`ai8051u_32_tfpu.lib`、`stc_usb_cdc_32g_xdata.lib`）都是 **用 `INTR2` 编译的**。

如果你的 `main.c` 没有用 `INTR2` 编译：
- 你的 ISR 会 push 10 字节（251 原生行为）
- 库函数的 ISR 只 push 4 字节（INTR2 行为）
- 栈帧不匹配 → 返回地址错乱 → 💥 **运行时崩溃**

### 7.3 验证方法

在 `.lst` 文件中检查 `interrupt` 函数的第一条指令：
```
; INTERRUPT(4) 的 ISR 入口：
    PUSH    PSW1        ; 1 字节
    PUSH    DR60        ; 1 字节 (PC[23:16])
    PUSH    DR56        ; 1 字节 (PC[15:8])
    PUSH    DR28        ; 1 字节 (PC[7:0])
; 共 4 push → 4 字节帧 ✓
```

---

## 八、Makefile 和 builder.rs 的问题总结

### 8.1 Makefile 的问题

| 问题 | 详情 |
|------|------|
| ❌ 路径不匹配 | 只编译 `Sources/*.c`，但 bk1/bk2 引用的 `port.c` 等文件不存在 |
| ❌ 缺少 SRC 选项 | `.uvproj` 中有 `uSrcBin=1`（SRC 模式），Makefile 未设置 |
| ❌ 缺少 ROM(LARGE) | 大 ROM 空间需要显式 `ROM(LARGE)` 控制 |
| ❌ INCDIR 路径 | 多加了 STC 头文件路径 `Sources\inc\stc`（虽然无害但 .uvproj 里没有） |

### 8.2 builder.rs 的**致命问题**

| 问题 | 详情 |
|------|------|
| 🔴 **缺少 `INTR2`** | 这是最关键的错误！库用 INTR2 编译，主程序也必须有。没有它会导致运行时栈帧错乱 |
| 🟡 缺少 `SRC` | .uvproj 有 uSrcBin=1，builder.rs 未设置 |
| 🟡 缺少 `ROM(LARGE)` | 大 ROM 空间选项未显式设置 |
| 🟡 缺少 `SPEED` | 优化侧重点未指定 |

### 8.3 正确的 C251 编译选项

```rust
const C251_FLAGS: &[&str] = &[
    "LARGE",                 // MemoryModel=4
    "ROM(LARGE)",            // RomSize=3
    "INTR2",                 // uFrame4=1  ← 🔴 必须加！
    "OPTIMIZE(7, SPEED)",    // Optim=7, SizSpd=1
    "WARNINGLEVEL(2)",       // wLevel=2
    "DEBUG",
    "SYMBOLS",
];
```

---

## 九、VS Code 集成配置

`.vscode/` 下的配置文件：

### settings.json
```json
{
    "EIDE.C51.INI.Path": "C:\\Keil_v5\\C251\\TOOLS.INI",  // EIDE 插件配置
    "C_Cpp.errorSquiggles": "disabled"                     // 禁用错误波浪线
}
```

### tasks.json
当前 VS Code 任务使用 **Makefile**（`make` 命令），而非直接调用 Keil 工具链。

---

## 十、总结：Keil IDE 一键构建的完整路径

```
用户点击 "Build" (F7)
    │
    ├── Keil 读取 .uvproj 配置
    │     ├── 提取 C251 编译选项
    │     ├── 提取 L251 链接选项
    │     ├── 提取文件列表（Groups/Files）
    │     └── 提取内存布局（OnChipMemories）
    │
    ├──【编译】对每个 C 源文件执行：
    │   C251.EXE main.c <编译选项> OBJECT(.\Objects\main.obj) PRINT(Listings\main.lst)
    │   输出: .\Objects\main.obj + .\Listings\main.lst
    │
    ├──【链接】生成 .lnp 文件并执行：
    │   L251.EXE <所有 .obj> <所有 .lib> <链接选项> TO <目标名>
    │   输出: .\Objects\03-March_Wheel_leg_FOC (OMF251)
    │
    ├──【转换】OH251.EXE 自动触发：
    │   将 OMF251 目标文件转为 Intel HEX
    │   输出: .\Objects\03-March_Wheel_leg_FOC.hex
    │
    └── 完成 ✅ (0 Error(s), 0 Warning(s))
```
