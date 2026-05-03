# EIDE 一键命令绑定方案报告

> **报告时间**：2026-04-29
> **问题**：EIDE 面板的 Build/Flash 按钮怎么绑定到 C251 和 HID 烧录？
> **解决方案**：理解三层架构 + 修复 EIDE 升级问题

---

## 1. 架构总览：三种"一键方式"

你项目里有**三种**触发编译/烧录的方式，它们走的是**不同的路径**：

```
┌──────────────────────────────────────────────────────────┐
│                    VSCode 界面                            │
│                                                           │
│  [EIDE 面板]          [Ctrl+Shift+B]        [终端]        │
│  Build / Flash        VSCode Tasks          手动命令       │
│      │                    │                    │           │
└──────┼────────────────────┼────────────────────┼──────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  EIDE 内部    │    │  tasks.json  │    │  手动命令行    │
│  命令系统     │    │  配置的任务   │    │  直接调用      │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│              builder.params (JSON)                        │
│  ┌─────────────────────────────────────────────────┐     │
│  │ toolchainLocation  → 编译器根目录 (C:\Keil_v5\C51)│    │
│  │ toolchainCfgFile   → model 文件路径              │    │
│  │ options            → 编译选项                    │    │
│  │ sourceList         → 源文件列表                  │    │
│  └─────────────────────────────────────────────────┘     │
│                         │                                 │
│              eide.yml (项目配置)                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │ toolchain  → 使用的工具链 (Keil_C51)            │    │
│  │ uploadConfigMap → 烧录命令                       │    │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

---

## 2. 三种方式详解

### 方式 1: EIDE 面板按钮

| 按钮 | 触发什么 | 配置文件 |
|------|---------|---------|
| **Build** | `${command:eide.project.build}` | `eide.yml` → `builder.params` → `unify_builder` |
| **Flash** | `${command:eide.project.uploadToDevice}` | `eide.yml` → `uploadConfigMap.Custom.commandLine` |
| **Rebuild** | `${command:eide.project.rebuild}` | 同上 |

**Build 链路**：
```
EIDE Build按钮
  → 读取 eide.yml (toolchain: Keil_C51)
  → 读取 .vscode/settings.json (EIDE.C51.INI.Path)
  → 检测 Keil C51 安装路径 → toolchainLocation
  → 选择 model 文件 → 8051.keil.model.json (已被 Hack)
  → 生成 builder.params
  → 调用 unify_builder
  → unify_builder 读 model → 调 C251.EXE
```

**Flash 链路**：
```
EIDE Flash按钮
  → 读取 eide.yml → uploadConfigMap.Custom.commandLine
  → 直接执行那条命令
```

### 方式 2: VSCode Tasks (Ctrl+Shift+B)

| 任务 | 快捷键/操作 | 说明 |
|------|-----------|------|
| **C251: Build** ⭐ | `Ctrl+Shift+B` (默认) | C251 编译+链接，不经过 EIDE |
| **HID Flash** | `Ctrl+Shift+P` → Run Task | Python HID 烧录 |
| **Build + Flash (C251 + HID)** | `Ctrl+Shift+P` → Run Task | 编译+链接+烧录一条龙 |
| Build (EIDE C251) | 同 EIDE 面板 Build | 如果 EIDE model 修好了就能用 |
| Flash (EIDE) | 同 EIDE 面板 Flash | 如果 eide.yml 修好了就能用 |

### 方式 3: 手动命令行

```powershell
# 编译
python ./tools/stc_hid_flash.py build/Debug/AI8051U_test.hex

# 烧录（已验证✅）
python ./tools/stc_hid_flash.py build/Debug/AI8051U_test.hex
```

---

## 3. EIDE 升级导致的问题

### 3.1 问题链

```
EIDE 升级 v3.26.7 → v3.26.8
    │
    ├── res/data/models/8051.keil.model.json → 被覆盖为原始 C51 版本 ❌
    │     → unify_builder 找不到 ../C251/BIN/C251 (因为路径回到 BIN/C51)
    │     → Build 失败
    │
    └── builder.params → toolchainCfgFile 指向 v3.26.8 的 model
          (自动更新了，EIDE 知道新版本路径)
```

### 3.2 为什么 eide.yml 也回退了？

`eide.yml` 可能也被 EIDE 重新生成了（或者在 VSCode 重载时 EIDE 重新写入了默认值）。修改 `eide.yml` 后需要保存并重新加载 EIDE。

### 3.3 修复清单（每次 EIDE 升级后都要做）

| # | 操作 | 文件 |
|---|------|------|
| 1 | 把 C251 model 写回 | `cl.eide-X.X.X\res\data\models\8051.keil.model.json` |
| 2 | 确认烧录命令 | `.eide/eide.yml` → `commandLine: python ./tools/stc_hid_flash.py "${hexFile}"` |
| 3 | 在 VSCode 中**重载 EIDE** | 点击 EIDE 面板的刷新按钮 |

---

## 4. 当前配置状态

| 组件 | 状态 | 说明 |
|------|------|------|
| `8051.keil.model.json` (v3.26.8) | ✅ 已修复 | 重新写入 C251 配置 |
| `.eide/eide.yml` Flash 命令 | ✅ 已修复 | 改为 `stc_hid_flash.py` |
| `.vscode/tasks.json` | ✅ 整理完毕 | 11 个任务，默认 C251 Build |
| `.vscode/settings.json` | ✅ 正常 | `EIDE.C51.INI.Path` 指向 C251 |
| `tools/stc_hid_flash.py` | ✅ 已验证 | 烧录测试通过 |

---

## 5. 你需要做的（在 VSCode 中）

```
1. 重载 EIDE：点击 EIDE 面板右上角 🔄 刷新按钮
       ↓
2. 测试 Build：点击 EIDE 面板 Build 按钮
       ↓ 如果成功了：
3. 测试 Flash：点击 EIDE 面板 Flash 按钮
```

> 💡 如果 EIDE Build 还是不工作，用 `Ctrl+Shift+B`（VSCode 任务版本）代替。
> VSCode 任务版本的 C251 Build 不依赖 EIDE 内部状态，100% 可靠！

---

## 6. 任务速查表

| 你想要的 | 最快方式 |
|---------|---------|
| 只编译 | `Ctrl+Shift+B` (默认) |
| 只烧录 | `Ctrl+Shift+P` → `Tasks: Run Task` → `HID Flash` |
| 编译+烧录一条龙 | `Ctrl+Shift+P` → `Tasks: Run Task` → `Build + Flash (C251 + HID)` |

---

## 7. 附录：完整文件关系图

```
eide.yml  ──────────────┐
  toolchain: Keil_C51   │
  uploadConfigMap       │──→ EIDE 内部逻辑
                        │
.vscode/settings.json  ─┤
  EIDE.C51.INI.Path     │
                        │
.vscode/tasks.json  ────┤──→ VSCode 任务系统 (Ctrl+Shift+B)
                        │
builder.params  ────────┤──→ unify_builder → C251.EXE
  toolchainLocation     │
  toolchainCfgFile      │
                        │
8051.keil.model.json ───┘──→ unify_builder 编译器配置
  $path: ../C251/BIN/C251

stc_hid_flash.py  ─────────→ Python hidapi → STC USB-ISP 设备
```

---

*💕 结论：EIDE 有三个独立系统（EIDE 按钮、VSCode 任务、手动命令），每个都需要单独配置。最容易出问题的是 EIDE 升级覆盖 model 文件。`Ctrl+Shift+B` 用 VSCode 任务版本最可靠！*
