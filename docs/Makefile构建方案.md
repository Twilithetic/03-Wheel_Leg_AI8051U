# AI8051U 项目 Makefile 构建方案

## 项目概况

| 项目 | 说明 |
|------|------|
| **芯片** | AI8051U (STC 80251兼容, LQFP48) |
| **主频** | 36MHz (FOSC), 24MHz (HIRC) |
| **编译器** | Keil C251 V5 (`C:\Keil_v5\C251\BIN\`) |
| **构建工具** | C251.EXE (编译) + L251.EXE (链接) |
| **烧录工具** | AiCube-ISP v6.96V+ (USB-HID / USB-CDC) |
| **库依赖** | STC USB CDC LIB, MDU32, TFPU |

## 当前构建流程分析

### VSCode Tasks (`.vscode/tasks.json`)

```
C251: Compile  → C251.EXE main.c INCDIR(src\inc) OBJECT(build\main.obj) LARGE DEBUG SYMBOLS
C251: Link     → L251.EXE main.obj,stc_usb_hid_32g_xdata.LIB TO build\AI8051U_C251.HEX
C251: Build    → Compile + Link
HID Flash     → python stc_hid_flash.py build/AI8051U_C251.HEX
Build + Flash → Compile + Link + Flash
```

### 已识别的问题

| 问题 | 详情 |
|------|------|
| **tasks.json 路径不匹配** | 用 `src\main.c` 但实际是 `Sources\main.c` |
| **库名不匹配** | tasks.json 引用 `stc_usb_hid_32g_xdata.LIB`，实际文件是 `stc_usb_cdc_32g_xdata.LIB`（CDC 模式） |
| **烧录脚本缺失** | `stc_hid_flash.py` 不在 tools/ 目录中 |
| **未编译其他 .c 文件** | clock.c, cre.c, port.c, usblib.c, mathlib.c 未参与编译 |

## 解决方案

### Makefile 设计方案

目标列表：
- `make` / `make all` — 编译 + 链接 = 生成 HEX
- `make compile` — 仅编译 (C251)
- `make link` — 仅链接 (L251)
- `make clean` — 清理构建产物
- `make flash` — 烧录到芯片 (AiCube-ISP)
- `make rebuild` — clean + all
- `make info` — 显示项目信息
- `make fix-eide` — 修复 EIDE C251 模型

### 技术细节

**C251 编译选项**：
- `LARGE` — LARGE 内存模型 (16MB 地址空间)
- `DEBUG` — 包含调试信息
- `SYMBOLS` — 生成符号表
- `INCDIR(path)` — 头文件搜索路径
- `OBJECT(path)` — 指定输出 .OBJ 路径

**L251 链接语法**：
```
L251 obj1.obj,lib1.LIB[,lib2.LIB...] TO output.hex [options]
```

**使用的库文件**：
- `Sources/lib/stc_usb_cdc_32g_xdata.LIB` — USB CDC 通信
- `Sources/lib/ai8051u_32_mdu32.lib` — 硬件乘除法加速
- `Sources/lib/ai8051u_32_tfpu.lib` — 硬件浮点加速

**烧录方式**：
- AiCube-ISP.exe 支持命令行参数自动烧录
- 目标文件：`build/AI8051U_C251.HEX`

### 注意事项

1. Windows 上需使用 `mingw32-make` 或 Git Bash 的 `make`
2. 若无 make 工具，提供 `Makefile.ps1` (PowerShell) 作为备选
3. 库文件路径可能随功能切换而变化 (HID ↔ CDC)
4. .c 文件列表可通过 `SRCS` 变量扩展
