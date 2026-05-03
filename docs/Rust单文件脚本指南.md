# Rust 单文件脚本 (cargo-script) 完全指南

> 📅 日期：2026年4月28日（含实测验证）  
> 📚 来源：RFC 3502、RFC 3424、Rust 官方文档、社区实践  
> 🔬 验证环境：Windows 11 + Rust 1.97.0-nightly + stable 1.85+

---

## 一、什么是 cargo-script？

`cargo-script` 是 Cargo 的**原生功能**（RFC 3502），允许用**一个 `.rs` 文件**就是一个完整的 Rust 项目，不需要 `Cargo.toml`、不需要 `src/` 目录。

### 和 Python/Bash 脚本一样简单

| 语言 | 脚本运行方式 |
|------|------------|
| Python | `python script.py` |
| Bash | `bash script.sh` |
| **Rust** | `cargo +nightly -Zscript script.rs` 🦀 |

---

## 二、三种运行方式对比

### 方式 A：`rustc` 直接编译

```bash
rustc find_volt_div_res.rs -o find_volt_div_res.exe
./find_volt_div_res
```

| 优点 | 缺点 |
|------|------|
| ✅ 零配置，stable 直接用 | ❌ **不能使用外部 crate** |
| ✅ 编译极快（<1秒） | ❌ 需要手动指定编译选项 |
| ✅ 适合无依赖程序 | ❌ 无包管理 |

### 方式 B：`cargo script` 🔥（需要 nightly）

在 `.rs` 文件顶部加一段 TOML 嵌入清单：

```rust
#!/usr/bin/env cargo
---
[package]
edition = "2024"

[dependencies]
colored = "2"
---

//! 脚本说明写这里
use std::io::{self, Write};

fn main() {
    println!("Hello with dependencies!");
}
```

运行：

```powershell
# Windows (PowerShell)
cargo +nightly -Zscript .\script.rs

# Linux/Mac
cargo +nightly -Zscript ./script.rs
```

| 优点 | 缺点 |
|------|------|
| ✅ **可以用任何 crates.io 上的 crate** | ⚠️ 首次编译需下载依赖（~3-10秒） |
| ✅ 和完整项目开发体验一致 | ⚠️ 当前必须用 nightly 频道 |
| ✅ 自动处理依赖下载/编译/缓存 | |
| ✅ 单文件即项目，分享方便 | |

### 方式 C：完整 Cargo 项目

```bash
cargo new my_project
# 编辑 src/main.rs + Cargo.toml
cargo run
```

---

## 三、`rustc` vs `cargo script` vs `cargo new` 对比

| 维度 | `rustc` 编译 | `cargo script` | `cargo new` 项目 |
|------|-------------|---------------|-----------------|
| 文件数 | **1 个 .rs** | **1 个 .rs** | Cargo.toml + src/ |
| 外部依赖 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| 所需工具链 | **stable** | **nightly** | stable |
| 编译命令 | `rustc file.rs` | `cargo +nightly -Zscript file.rs` | `cargo run` |
| target 目录 | 无(只有 exe) | `~/.cargo/target/<hash>` | `./target/` |
| 分享给他人 | 简单复制 .rs | 简单复制 .rs | 需复制整个目录 |
| 适合场景 | 无依赖小工具 | **有依赖的脚本/原型** | 正式项目 |

---

## 四、实测：从零到跑通

### 实验文件：`find_volt_div_res.rs`（E24电阻分压计算器）

**文件内容：**
```rust
#!/usr/bin/env cargo
---
[package]
edition = "2024"

[dependencies]
colored = "2"
---

//! E24电阻分压计算器 - 交互式CLI
//! 根据目标输出电压，计算满足条件的E24电阻分压对

use std::io::{self, Write};

// ... (227行完整代码)
```

### 第一次尝试：stable 直接跑 → ❌

```powershell
PS> cargo .\find_volt_div_res.rs
error: could not find `Cargo.toml` in `...` or any parent directory
```

> `cargo <file>.rs` 语法在 stable 上还没开放！

```powershell
PS> cargo .\find_volt_div_res.rs -Zscript
error: the `-Z` flag is only accepted on the nightly channel
```

> `-Z` 标志是 **nightly-only**，stable 用不了！

### 第二步：安装 nightly → ✅

```powershell
PS> rustup toolchain install nightly
info: nightly-x86_64-pc-windows-msvc installed - rustc 1.97.0-nightly
```

### 第三步：用 nightly 跑 → ✅🎉

```powershell
PS> cargo +nightly -Zscript .\find_volt_div_res.rs
```

**实际运行输出：**
```
warning: `package.edition` is unspecified, defaulting to the latest edition (2024)

╔════════════════════════════════════════════════════════════╗
║         E24 电阻分压计算器 - 寻找满足条件的电阻对          ║
╚════════════════════════════════════════════════════════════╝

[✓] 生成E24电阻数组: 177 个标准值 (0~22MΩ)

=== 核心参数 ===
电源电压 Vcc (V) (默认 24.0):
目标输出电压最小值 (V) (默认 2.5):
电阻精度 (±, 如0.01表示±1%) (默认 0.0):

=== 电阻筛选范围 ===
最小电阻 (Ω) (默认 1000.0):
最大电阻 (Ω) (默认 100000.0):

[✓] 找到 2047 个符合条件的电阻对

   序号   │     Rup      │    Rdown     │   Vout_min   │   Vout_max   │    波动范围   
───────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────
    1 │     47.00 kΩ │      5.60 kΩ │       2.5098 V │       2.6012 V │     0.0913 V
    2 │     36.00 kΩ │      4.30 kΩ │       2.5154 V │       2.6069 V │     0.0915 V
    ...
```

> 虽然 `colored = "2"` 在依赖里但代码中没 import，不会报错，只是 cargo 下载了它。

---

## 五、Windows 特别注意事项 ⚠️

| 事项 | 说明 |
|------|------|
| `#!/usr/bin/env cargo` | Windows 上**不起作用**，但在文件中保留无妨（Unix 下有用） |
| 正斜杠/反斜杠 | `cargo +nightly -Zscript .\file.rs` 和 `./file.rs` 都可以 |
| nightly 安装 | `rustup toolchain install nightly` 只需装一次 |
| `+nightly` 前缀 | 只影响这一条命令，不影响默认 stable 工具链 |
| edition 警告 | 加 `edition = "2024"` 到 manifest 的 `[package]` 中即可消掉 |

---

## 六、嵌入清单（embedded manifest）语法详解

格式是 Markdown 代码块 + TOML：

```rust
#!/usr/bin/env cargo          ← Unix shebang，Windows 忽略但保留
---
[package]
edition = "2024"              ← 消掉 edition 警告

[dependencies]
crate_name = "version"
---
                              ← 空行后方开始写 Rust 代码
fn main() {}
```

### 可以放什么？

```toml
[package]
name = "my_script"       # 可选，默认取文件名
edition = "2024"          # 建议写上，消掉警告
version = "0.1.0"         # 可选

[dependencies]
serde = "1"
clap = { version = "4", features = ["derive"] }

[profile.release]
opt-level = 3
```

### 不能放什么？

- ❌ `[workspace]` — 单文件不属于工作区
- ❌ `[lib]`, `[[bin]]`, `[[example]]` — 只能有一个 `main()`
- ❌ `package.publish` — 单文件不能发布到 crates.io

### 依赖声明了但没 import 会怎样？

不会报错！cargo 会下载该 crate 但编译器只给一个 warning（如果你没用到的话）。这在搭框架时很方便——先声明依赖，以后慢慢用。

---

## 七、`find_volt_div_res.rs` 的最终版本

```rust
#!/usr/bin/env cargo
---
[package]
edition = "2024"

[dependencies]
colored = "2"
---

//! E24电阻分压计算器 - 交互式CLI
//!
//! 根据目标输出电压，计算满足条件的E24电阻分压对
//! 考虑电阻误差，计算worst-case最小输出电压

use std::io::{self, Write};

/// E24标准电阻基础值（24个）
const E24_BASE: [f64; 24] = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0,
    2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3,
    4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
];
// ... (后续代码不变)
```

### 三种运行方式任选

```powershell
# ① cargo script (nightly，支持外部依赖)
cargo +nightly -Zscript .\find_volt_div_res.rs

# ② rustc 直接编译 (stable，最快)
rustc .\find_volt_div_res.rs -o find_volt_div_res.exe
.\find_volt_div_res.exe

# ③ 直接用已有的 exe (你编译好的)
.\find_volt_div_res.exe
```

---

## 八、常见错误速查

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| `could not find Cargo.toml` | stable 频道不支持 | 加 `+nightly -Zscript` |
| `-Z flag is only accepted on nightly` | 没装 nightly | `rustup toolchain install nightly` |
| `package.edition is unspecified` | 没声明 edition | manifest 里加 `edition = "2024"` |
| 编译后没有 exe | cargo script 产物在缓存目录 | 查看 `~/.cargo/target/` 或用 `rustc` |

---

## 九、cargo-script 现状

| 项目 | 状态 |
|------|------|
| RFC #3502 | ✅ 已接受（2023年9月） |
| Nightly 可用 | ✅ `cargo +nightly -Zscript`（已验证） |
| Stable 可用 | ⏳ 尚未稳定，需 nightly |
| rust-analyzer 支持 | 🔄 进行中 |

> ⚠️ 2026年4月实测：Rust 1.85 stable **仍不支持** `cargo file.rs`，必须用 `cargo +nightly -Zscript`。

---

## 十、速查表

```powershell
# === 安装 nightly（只需一次）===
rustup toolchain install nightly

# === 无依赖脚本 ===
rustc tool.rs -o tool.exe && ./tool

# === 有依赖脚本（cargo script）===
cargo +nightly -Zscript .\tool.rs              # 编译+运行
cargo +nightly -Zscript --release .\tool.rs    # release 模式

# === 其他 cargo 命令 ===
cargo +nightly test -Zscript --manifest-path .\tool.rs   # 运行测试
cargo +nightly clean -Zscript --manifest-path .\tool.rs  # 清理缓存

# === 查看展开的 Cargo.toml ===
cargo metadata --manifest-path .\tool.rs --format-version=1
```

---

> 💡 **一句话总结**：Rust 单文件脚本就是 `.rs` 顶部嵌入 `Cargo.toml` 清单，用 `cargo +nightly -Zscript file.rs` 一行跑通。无依赖时用 `rustc` 更快，有依赖时 cargo-script 无敌！🦀
