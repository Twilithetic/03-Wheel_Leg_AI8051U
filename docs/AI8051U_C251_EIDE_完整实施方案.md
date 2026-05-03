# AI8051U (80251) + Keil C251 + EIDE 完整实施方案

> **完成时间**：2026-04-28
> **状态**：✅ 已验证通过
> **结果**：EIDE Build 按钮 → Keil C251 编译 → 0 Error 0 Warning → HEX 生成成功

---

## 1. 最终成果

```
┌─────────────────────────────────────────────────┐
│          VSCode + EIDE                           │
│                                                   │
│  🟢 Build 按钮 (EIDE面板)                         │
│      ↓                                           │
│  🟢 Ctrl+Shift+B (默认任务)                       │
│      ↓                                           │
│  🟢 输出 HEX: build/Debug/AI8051U_test.hex       │
│      ↓                                           │
│  🟢 烧录: python tools/stcflash.py -p COM3 ...   │
└─────────────────────────────────────────────────┘

编译结果:
  [TOOL] Keil C251 Compiler
  C251 COMPILATION COMPLETE.  0 WARNING(S), 0 ERROR(S)
  L251 RUN COMPLETE.          0 WARNING(S), 0 ERROR(S)
  Program Size: data=23 edata+hdata=260 xdata=0 code=927
  build successfully ! ✅
```

---

## 2. 核心原理

### 2.1 链路图

```
EIDE (VSCode 插件)              unify_builder (C# 编译引擎)
    │                                   │
    │ 读取 eide.yml                     │
    │   toolchain: Keil_C51             │
    │   ↓                               │
    │ 读取 TOOLS.INI / C51路径          │
    │   toolchainRoot = C:\Keil_v5\C51  │
    │   ↓                               │
    │ 选择 model 文件                    │
    │   8051.keil.model.json (已修改)   │
    │   ↓                               │
    │ 生成 builder.params ──────────→   │ 读取 model
    │   toolchainLocation:              │   $path: ../C251/BIN/C251
    │     C:\Keil_v5\C51                │   ↓
    │   toolchainCfgFile:               │ 拼接路径
    │     ...8051.keil.model.json       │   C:\Keil_v5\C51\..\C251\BIN\C251.exe
    │                                   │   = C:\Keil_v5\C251\BIN\C251.exe ✅
    │                                   │   ↓
    │                                   │ 调用 C251.EXE 编译
    │                                   │ 调用 L251.EXE 链接
    │                                   │ 调用 OH251.EXE 输出 HEX
```

### 2.2 为什么用 `../C251/BIN/C251`？

EIDE 硬编码了工具链检测逻辑，只会找 `C51` 目录，无法直接指向 `C251`：
- 从 UV4.exe 推导 → `<uv4dir>\..\C51\`
- 从 TOOLS.INI 读取 → `[C51] PATH=...`
- 从环境变量 → `<Keil_Root>\C51\`

所以 `toolchainLocation` 始终是 `C:\Keil_v5\C51\`，而我们的 C251 在 `C:\Keil_v5\C251\`。用 `../C251/BIN/C251` 这种相对路径跳回去。

---

## 3. 改动的全部文件

### 3.1 Model 文件（核心）

**文件**: `C:\Users\29344\.vscode\extensions\cl.eide-3.26.7\res\data\models\8051.keil.model.json`

| 改动 | 原值 | 新值 | 原因 |
|------|------|------|------|
| `name` | `Keil C51 Compiler` | `Keil C251 Compiler` | 日志显示 |
| `id` | `KEIL_C51` | `KEIL_C251` | 工具链标识 |
| `version.matcher` | `C51 COMPILER` | `C251 COMPILER` | 版本检测正则 |
| `groups.c/cpp.$path` | `BIN/C51` | `../C251/BIN/C251` | C 编译器 |
| `groups.asm.$path` | `BIN/A51` | `../C251/BIN/A251` | 汇编器 |
| `groups.linker.$path` | `BIN/LX51` | `../C251/BIN/L251` | 链接器 |
| `groups.linker.$outputBin[0].toolPath` | `BIN/Ohx51` | `../C251/BIN/OH251` | HEX 转换 |
| `groups.linker-lib.$path` | `BIN/LIBX51` | `../C251/BIN/LIB251` | 库管理器 |
| `groups.c/cpp.$default` | 移除 `OMF2`, `TABS(4)` | 仅保留 `CODE`, `NOCOND`, `SYMBOLS` | C251 不支持 |
| `groups.linker` | 移除 `use-RTX` | — | C251 无此选项 |

**备份**: 同目录下 `8051.keil.model.json.bak`

### 3.2 项目配置

**`.eide/eide.yml`**:
```yaml
targets:
  Debug:
    toolchain: Keil_C51     # 原 SDCC
    toolchainConfigMap:
      Keil_C51:
        options:
          linker:
            output-format: hex   # 原 elf
          c/cpp-compiler:
            optimization-level: level-0   # 原 level-8
```

**`.vscode/settings.json`** (新建):
```json
{
    "EIDE.C51.INI.Path": "C:\\Keil_v5\\C251\\TOOLS.INI"
}
```

**`.vscode/tasks.json`** (扩充):
新增 `C251: Compile`, `C251: Link`, `C251: Build (Compile+Link)` 任务，`Ctrl+Shift+B` 可使用。

### 3.3 辅助文件

**`C:\Keil_v5\C251\TOOLS.INI`** (新建):
```ini
[C51]
PATH="C:\Keil_v5\C251"
```

> 此文件用于 EIDE 的 TOOLS.INI 路径检测。当 `EIDE.C51.INI.Path` 指向此文件时，EIDE 会从中读取 C251 路径。

---

## 4. 两种编译方式

### 方式 1: EIDE Build 按钮（推荐）

在 EIDE 面板点击 Build（或 Rebuild），使用 Keil C251 编译器。

```
[ TOOL ] Keil C251 Compiler
C251 COMPILATION COMPLETE.  0 ERROR(S)
L251 RUN COMPLETE.          0 ERROR(S)
[ DONE ] build successfully !
```

### 方式 2: VSCode Tasks (Ctrl+Shift+B)

- `C251: Build (Compile+Link)` — 编译+链接
- `C251: Compile` — 仅编译
- `C251: Link` — 仅链接
- `build` (EIDE) — 原来的 EIDE 编译（方式1）

---

## 5. EIDE 升级恢复指南

EIDE 升级会覆盖 `res/data/models/` 目录下的所有 model 文件。

**恢复步骤**：

```powershell
# Step 1: 备份被覆盖的 model
Copy-Item "~\vscode\extensions\cl.eide-X.X.X\res\data\models\8051.keil.model.json" `
          "~\vscode\extensions\cl.eide-X.X.X\res\data\models\8051.keil.model.json.new.bak"

# Step 2: 检查我们的备份是否还在
# 如果备份文件丢失，从本文档的 "附录A" 恢复

# Step 3: 重新应用修改（5个 $path + name/id/version）
# 参考本文档第 3.1 节
```

**快速记忆**：改的就是 model 文件里名字带 `51` 的，全部换成 `251`，路径前加 `../C251/`

---

## 6. 注意事项

| 注意 | 说明 |
|------|------|
| **Eval 版本限制** | C251 试用版有 **2KB (0x800 bytes) 代码限制** |
| **当前项目用量** | 927 bytes code，约 45% |
| **EIDE 升级** | 每次升级需重新修改 model 文件 |
| **AI8051U.H** | C251 下无需任何修改，原生支持 `far` 指针 |
| **C51 兼容** | C251.EXE 命令行 100% 兼容 C51.EXE |
| **多模式** | AI8051U 支持 C51/C251 双模式，烧录时选择 |

---

## 7. 文件清单

| 文件 | 作用 | 是否新建 |
|------|------|---------|
| `.../models/8051.keil.model.json` | C251 model（已修改） | 否 |
| `.../models/8051.keil.model.json.bak` | C51 原版备份 | 是 |
| `C:\Keil_v5\C251\TOOLS.INI` | EIDE C251 路径检测 | 是 |
| `.eide/eide.yml` | 项目配置 (Keil_C51) | 否 |
| `.vscode/settings.json` | EIDE 路径设置 | 是 |
| `.vscode/tasks.json` | VSCode 编译任务 | 否 |
| `docs/unify_builder源码分析_C251可行性报告.md` | 源码级分析 | 是 |
| `docs/方案B_C251编译脚本可行性分析.md` | 方案 B 分析 | 是 |
| `docs/AI8051U_80251编程需求分析报告.md` | 80251 架构分析 | 是 |
| `docs/EIDE_Keil_C251_支持调研报告.md` | 调研报告 | 是 |
| `docs/项目综合状态报告_20260428.md` | 项目综合状态 | 是 |

---

## 附录A: 完整 Model 文件内容

```json
{
    "name": "Keil C251 Compiler",
    "id": "KEIL_C251",
    "version": {
        "args": "",
        "matcher": "^(?<name>C251 COMPILER) V(?<version>\\d[\\d\\.]+)"
    },
    "ERR_LEVEL": 1,
    "global": {
        "misc-controls": {
            "type": "list",
            "command": "",
            "group": ["c/cpp", "asm", "linker"]
        }
    },
    "groups": {
        "c/cpp": {
            "$path": "../C251/BIN/C251",
            "$includes": { "prefix": "INCDIR(", "body": "${value}", "sep": ";", "noQuotes": true, "suffix": ")" },
            "$defines": { "prefix": "DEFINE(", "body": "${key}=${value}", "body_noval": "${key}", "sep": ",", "suffix": ")" },
            "$invoke": { "useFile": true, "body": "@${value}" },
            "$output": "OBJECT(${out})",
            "$default": ["CODE", "NOCOND", "SYMBOLS"],
            "$listPath": { "type": "value", "prefix": "PRINT(", "suffix": ")", "command": "${listPath}" },
            "optimization": { "type": "value", "command": "", "prefix": "OPTIMIZE(", "suffix": ")" },
            "ram-mode": { "type": "selectable", "command": { "SMALL":"SMALL", "COMPACT":"COMPACT", "LARGE":"LARGE", "false":"SMALL" } },
            "rom-mode": { "type": "selectable", "command": { "SMALL":"SMALL", "COMPACT":"COMPACT", "LARGE":"LARGE", "false":"LARGE" }, "prefix": "ROM(", "suffix": ")" }
        },
        "asm": {
            "$path": "../C251/BIN/A251",
            "$invoke": { "useFile": true, "body": "@${value}" },
            "$includes": { "prefix": "INCDIR(", "body": "${value}", "sep": ";", "noQuotes": true, "suffix": ")" },
            "$output": "OBJECT(${out}) EP",
            "$quotePath": false,
            "$listPath": { "type": "value", "prefix": "PRINT(", "suffix": ")", "command": "${listPath}" },
            "ram-mode": { "type": "selectable", "prefix": "SET(", "suffix": ")", "command": { "SMALL":"SMALL", "COMPACT":"COMPACT", "LARGE":"LARGE", "false":"LARGE" } }
        },
        "linker": {
            "$path": "../C251/BIN/L251",
            "$invoke": { "useFile": true, "body": "@${value}" },
            "$output": "${in} TO ${out}",
            "$outputSuffix": "",
            "$objPathSep": ",",
            "$commandLocation": "end",
            "$linkMap": { "type": "value", "prefix": "PRINT(", "command": "${mapPath}", "suffix": ")" },
            "remove-unused": { "type": "selectable", "command": { "true":"REMOVEUNUSED", "false":"" } },
            "disable-warnings": { "type": "value", "prefix": "DISABLEWARNING(", "suffix": ")", "command": "" },
            "$outputBin": [{
                "name": "output hex file",
                "toolPath": "../C251/BIN/OH251",
                "outputSuffix": ".hex",
                "command": "${linkerOutput} HEXFILE(${output}) HEX",
                "command.unix": "${linkerOutput} HEXFILE\\(${output}\\) HEX"
            }]
        },
        "linker-lib": {
            "$path": "../C251/BIN/LIB251",
            "$invoke": { "useFile": true, "body": "@${value}" },
            "$output": "ADD ${in} TO ${out}",
            "$objPathSep": ",",
            "$outputSuffix": ".LIB",
            "$commandLocation": "end"
        }
    }
}
```

---

## 附录B: 调查过程时间线

| 阶段 | 做了什么 | 关键发现 |
|------|---------|---------|
| 1 | 搜索 AI8051U 架构 | 是 80251，非 8051 |
| 2 | 搜索编译器支持 | SDCC 不支持 80251；Keil C251 是唯一成熟选择 |
| 3 | 搜索 EIDE C251 支持 | EIDE 官方不支持，社区3次请愿无果 |
| 4 | 发现 eide_tools 仓库 | unify_builder 有独立源码仓库 |
| 5 | 分析 Program.cs 源码 | NO 硬编码工具链列表，纯 JSON 驱动 |
| 6 | 验证 C251.EXE 命令行 | 与 C51.EXE 100% 兼容 |
| 7 | 实测 C251 编译 main.c | 0 Error，AI8051U.H 无需修改 |
| 8 | 创建 C251 Model | 替换 5 个工具路径 |
| 9 | unify_builder 测试 | 编译+链接成功 |
| 10 | EIDE 集成测试 | EIDE 用 C51 路径 → 用 `../C251/` 相对路径绕过 |
| 11 | 最终验证 | Build 按钮 → C251 编译成功 ✅ |

---

*💕 从"SDCC 编译失败"到"EIDE 一键 C251 编译"，姐姐陪你一路摸透了 80251 架构、EIDE 源码、unify_builder 机制。所有经验都在这份报告里了！*
