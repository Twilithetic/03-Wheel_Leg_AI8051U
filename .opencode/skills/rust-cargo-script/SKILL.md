---
name: rust-cargo-script
description: 使用 Rust 编写单文件脚本或工具，替代 PowerShell/Bash/Makefile。适用于需要外部依赖（crates.io）、跨平台运行、或需要高性能的单文件工具。也适用于编写项目构建脚本、代码生成器、自动化工具。当用户需要写脚本、构建工具、或询问如何用 Rust 写单文件程序时，使用此 skill。触发关键词：cargo script、rust 脚本、单文件 rust、rust 替代 makefile、rust 替代 powershell、cargo +nightly -Zscript。
---

# Rust 单文件脚本 (cargo-script) 指南

## 概述

Rust 原生支持**单文件脚本**（RFC 3502），一个 `.rs` 文件就是一个完整的 Cargo 项目。

相比 PowerShell/Bash/Makefile 的优势：
- ✅ 可以用 **crates.io 上的任何 crate**（如 `colored`、`anyhow`、`clap`）
- ✅ **编译期错误检查**，避免运行时才发现拼写错误
- ✅ **跨平台**（Windows/Linux/macOS 统一行为）
- ✅ 首次编译后缓存，后续运行接近原生速度

## 格式：嵌入清单

在 `.rs` 文件顶部嵌入 TOML 清单：

```rust
#!/usr/bin/env cargo
---
[package]
edition = "2024"

[dependencies]
colored = "2"
anyhow = "1"
serde_json = "1"   # 如需 JSON
clap = { version = "4", features = ["derive"] }  # 如需 CLI 参数解析
---

//! 脚本说明写这里（//! 文档注释）

use std::process::Command;
use colored::Colorize;
use anyhow::{Context, Result};

fn main() -> Result<()> {
    // 脚本逻辑
    Ok(())
}
```

### 清单中可以放什么

```toml
[package]
name = "my_tool"       # 可选，默认取文件名
edition = "2024"        # 建议写，消掉 warning
version = "0.1.0"       # 可选

[dependencies]
# 任意 crates.io crate

[profile.release]
opt-level = 3            # release 模式优化
```

### 不能放什么
- ❌ `[workspace]` — 单文件不属于工作区
- ❌ `[lib]`、`[[bin]]` — 只能有一个 `main()`
- ❌ `package.publish` — 单文件不能发布到 crates.io

## 运行方式

```powershell
# 标准运行（首次需下载依赖 + 编译，约 5-15 秒）
cargo +nightly -Zscript .\tools\my_script.rs

# release 模式（更快）
cargo +nightly -Zscript --release .\tools\my_script.rs

# 传参
cargo +nightly -Zscript .\tools\my_script.rs -- arg1 arg2
```

> ⚠️ 当前需要 **Rust nightly** 工具链: `rustup toolchain install nightly`
> `+nightly` 前缀只影响这一条命令，不改变默认 stable 工具链。
> stable 频道暂不支持 `cargo file.rs` 语法（2026年5月实测）。

## 常用依赖组合

| 场景 | 依赖 |
|------|------|
| **构建脚本** | `colored = "2"`, `anyhow = "1"` |
| **CLI 工具** | `clap = "4"` (derive), `colored = "2"`, `anyhow = "1"` |
| **JSON 处理** | `serde_json = "1"` |
| **HTTP 请求** | `reqwest = { version = "0.12", features = ["blocking"] }` |
| **文件遍历** | 标准库 `std::fs::read_dir` 足够 |
| **正则表达式** | `regex = "1"` |

## 执行外部命令

用 `std::process::Command`：

```rust
use std::process::Command;

// 执行并捕获输出
let output = Command::new("C251.EXE")
    .args(&["source.c", "LARGE", "DEBUG", "SYMBOLS"])
    .output()?;

let stdout = String::from_utf8_lossy(&output.stdout);
let stderr = String::from_utf8_lossy(&output.stderr);

// 检查错误（不要只依赖 exit code——有些工具即使成功也返回非零）
if stdout.contains("*** ERROR") {
    anyhow::bail!("编译失败");
}
```

> 💡 重要：Windows 上某些工具（如 Keil Eval 版本）即使成功也会返回非零退出码。应**检查输出内容**而非仅依赖 `$LASTEXITCODE`。

## Windows 注意事项

| 事项 | 说明 |
|------|------|
| Shebang `#!/usr/bin/env cargo` | Windows 忽略，但在文件中保留无妨 |
| 路径分隔符 | `tools\\builder.rs` 或 `tools/builder.rs` 均可 |
| nightly 安装 | `rustup toolchain install nightly` 只需装一次 |
| 文件名限制 | 不能用 `build.rs`（Cargo 保留名），改用 `builder.rs` |
| 工作目录 | cargo script 的 CWD 是运行命令时的目录 |

## 什么时候用 cargo-script vs 常规 Cargo 项目

| 场景 | 推荐 |
|------|------|
| 少于 500 行的工具脚本 | **cargo-script** ✅ |
| 构建/自动化脚本 | **cargo-script** ✅ |
| 需要多个模块的大型工具 | 常规 Cargo 项目 |
| 需要发布到 crates.io | 常规 Cargo 项目 |
| 需要集成测试 | 常规 Cargo 项目 |
| 原型验证 / PoC | **cargo-script** ✅ |

## 项目中的实际例子

本项目 `tools/` 目录下有两个 cargo-script：

1. **`tools/builder.rs`** — AI8051U 项目构建脚本
   - 替代 Makefile/Makefile.ps1
   - 调用 Keil C251 编译器 + 链接器
   - 用法：`cargo +nightly -Zscript tools/builder.rs build`

2. **`tools/fix_c251_model.rs`** — EIDE C251 模型修复
   - 修改 JSON 配置文件
   - 用法：`cargo +nightly -Zscript tools/fix_c251_model.rs`

## 创建新脚本的步骤

1. 确定脚本名称（不要用 `build.rs`）
2. 在 `tools/` 或合适目录创建 `.rs` 文件
3. 顶部写嵌入清单（edition、dependencies）
4. 写 `//!` 文档注释（说明用途和用法）
5. 用 `anyhow::Result` 作为 main 返回类型
6. 用 `colored` 做彩色终端输出
7. 用 `Command::output()` 调用外部程序（检查输出而非 exit code）
8. 测试：`cargo +nightly -Zscript tools\xxx.rs`
