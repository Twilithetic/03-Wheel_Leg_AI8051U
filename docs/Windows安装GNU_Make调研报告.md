# Windows 上安装 GNU Make 调研报告

> 📅 日期：2026年5月6日  
> 📚 来源：StackOverflow、Chocolatey 官网、GnuWin32 官网、winget.run

---

## 一、当前环境检查

| 工具 | 状态 |
|------|------|
| `make.exe` | ❌ 未安装 |
| `mingw32-make.exe` | ❌ 未安装 |
| `nmake.exe` (MSVC) | ❌ 未安装 |
| Chocolatey (`choco`) | ✅ 已安装 (`C:\ProgramData\chocolatey\bin\`) |
| winget | 未确认（需 Win10 1809+ / Win11） |
| Scoop | ❌ 未安装 |

---

## 二、安装方式对比

### 方式 1：Chocolatey（⭐ 推荐）

```powershell
# 管理员 PowerShell
choco install make
```

| 评价 | 说明 |
|------|------|
| 难度 | 🟢 一行命令 |
| 版本 | GNU Make 4.4.1（最新） |
| PATH | 自动配置 |
| 命令名 | `make.exe`（不是 mingw32-make） |
| 适用性 | 本项目 Makefile 直接兼容 |

### 方式 2：winget（Windows 自带）

```powershell
winget install -e --id GnuWin32.Make
```

| 评价 | 说明 |
|------|------|
| 难度 | 🟢 一行命令 |
| 版本 | GnuWin32 Make 3.81（较老，2006年） |
| PATH | 自动配置 |
| 缺点 | 版本老（3.81 vs 4.4.1），可能不兼容新版 Makefile 语法 |

### 方式 3：手动下载 GnuWin32

1. 打开 https://gnuwin32.sourceforge.net/packages/make.htm
2. 下载 `Complete package, except sources` → Setup
3. 运行安装程序
4. 手动添加 `C:\Program Files (x86)\GnuWin32\bin` 到 PATH

| 评价 | 说明 |
|------|------|
| 难度 | 🟡 需要手动配置 PATH |
| 版本 | 3.81（2006年） |
| 缺点 | 老旧、手动操作多 |

### 方式 4：MSYS2 / MinGW-w64

```powershell
# 先装 MSYS2，再装 make
pacman -S make
# 或直接装 MinGW-w64（自带 mingw32-make）
winget install -e --id Git.Git  # Git for Windows 自带 mingw32-make
```

| 评价 | 说明 |
|------|------|
| 难度 | 🟡 安装体积大 |
| 命令名 | `mingw32-make`（不是 make） |
| 缺点 | 本项目 Makefile 需要改名或用别名 |

---

## 三、推荐方案

### ⭐ 首选：Chocolatey

因为电脑上 **已经有 Chocolatey**，直接一行搞定：

```powershell
# 管理员身份运行 PowerShell
choco install make -y
```

安装后验证：

```powershell
make --version
# GNU Make 4.4.1
# Built for Windows32

cd D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U
make info
make clean
make rebuild
```

### 备选：Git for Windows（已安装则自带）

Git for Windows 自带 `mingw32-make.exe`，在 `C:\Program Files\Git\usr\bin\` 中。如果已装 Git，可以创建一个别名：

```powershell
# 在 PowerShell profile 中添加
New-Alias -Name make -Value "C:\Program Files\Git\usr\bin\mingw32-make.exe"
```

---

## 四、是否真的需要 make？

考虑到本项目已经有 **Rust cargo-script 构建脚本** (`tools/builder.rs`)：

| 场景 | 使用 |
|------|------|
| `cargo +nightly -Zscript tools\builder.rs rebuild` | ✅ 主力，功能完整 |
| `make rebuild` | 备选，需要先装 make |

**结论**：make 是「锦上添花」，不是必需品。Rust builder.rs 已经覆盖了所有构建需求，且不依赖任何外部工具（只要 Rust nightly 即可）。

如果只是想要 `make clean`，一行 PowerShell 同样能做到：

```powershell
Remove-Item build\*.obj, build\*.hex, build\*.map -Force -ErrorAction SilentlyContinue
```

---

## 五、操作建议

1. **如果想快速体验**：管理员 PowerShell 执行 `choco install make -y`，约 30 秒完成
2. **如果不想装额外工具**：用 `cargo +nightly -Zscript tools\builder.rs clean` 替代 `make clean`
3. **如果要最小依赖**：Rust builder.rs 是唯一需要的工具（Rust nightly 在项目中已使用）
