# fix_c251_model.rs 重写计划

## 问题

将 `tools/fix_c251_model.ps1`（PowerShell 脚本）改写成 Rust 单文件 cargo-script，遵循 `docs/Rust单文件脚本指南.md` 规范。

## 分析

### PowerShell 脚本核心逻辑回顾

| 步骤 | 操作 | PS 实现 |
|------|------|---------|
| 1 | 扫描 `~/.vscode/extensions/cl.eide-*` 目录 | `Get-ChildItem -Directory -Filter` |
| 2 | 找到 `res/data/models/8051.keil.model.json` | `Join-Path` + `Test-Path` |
| 3 | 读取 + 解析 JSON | `Get-Content` + `ConvertFrom-Json` |
| 4 | 检测是否已 hack（`id == "KEIL_C251"`） | `if ($model.id -eq "KEIL_C251")` |
| 5 | 备份原文件 → `.bak` | `Copy-Item` |
| 6 | 修改 JSON 对象（6 类修改） | 直接赋值 + `.Remove()` |
| 7 | 写回文件 | `Set-Content -Encoding UTF8 -NoNewline` |
| 8 | 汇总报告 | `Write-Host` 彩色输出 |

### Rust 实现的技术选型

| 需求 | 方案 | 依赖 |
|------|------|------|
| JSON 解析/修改/序列化 | `serde_json::Value`（动态操作，最接近 PS 做法） | `serde_json = "1"` |
| 目录扫描 | `std::fs::read_dir` + `Path` | 标准库 |
| 文件读写 | `std::fs` | 标准库 |
| 彩色终端输出 | `colored = "2"`（与指南用同一版本） | `colored = "2"` |
| 获取用户目录 | `dirs` 或 `std::env::var("USERPROFILE")` / `home::home_dir()` | 标准库 + `dirs` |
| 运行模式 | `cargo +nightly -Zscript tools/fix_c251_model.rs` | nightly toolchain |

### cargo-script 嵌入清单

```toml
[package]
edition = "2024"

[dependencies]
serde_json = "1"
colored = "2"
```

需要 nightly 工具链（`cargo +nightly -Zscript`）。

### 代码结构设计

```
1. 嵌入清单（Cargo.toml）
2. //! 文档注释（脚本说明）
3. 类型定义 & 常量
4. fix_model() 核心修复函数
5. main() 入口 + 扫描逻辑
```

### JSON 修改的具体映射

```rust
// 基本属性
model["name"] = json!("Keil C251 Compiler");
model["id"]   = json!("KEIL_C251");
model["version"]["matcher"] = json!("^(?<name>C251 COMPILER) V(?<version>\\d[\\d\\.]+)");

// 工具路径 (5 个)
model["groups"]["c/cpp"]["$path"]         = json!("../C251/BIN/C251");
model["groups"]["asm"]["$path"]           = json!("../C251/BIN/A251");
model["groups"]["linker"]["$path"]        = json!("../C251/BIN/L251");
model["groups"]["linker-lib"]["$path"]    = json!("../C251/BIN/LIB251");
model["groups"]["linker"]["$outputBin"][0]["toolPath"] = json!("../C251/BIN/OH251");

// 编译选项
model["groups"]["c/cpp"]["$default"] = json!(["CODE", "NOCOND", "SYMBOLS"]);

// 移除 use-RTX
model["groups"]["linker"].as_object_mut().unwrap().remove("use-RTX");
```

### 与 PowerShell 脚本的差异

| 特性 | PS 原版 | Rust 重写 |
|------|---------|----------|
| 运行方式 | `pwsh.exe -File fix_c251_model.ps1` | `cargo +nightly -Zscript fix_c251_model.rs` |
| 用户目录 | `$env:USERPROFILE` | `dirs::home_dir()` 或 `env::var("USERPROFILE")` |
| JSON 操作 | 动态 PS 对象 | `serde_json::Value` |
| 彩色输出 | `Write-Host -ForegroundColor` | `colored` crate |
| 暂停提示 | `Read-Host "按 Enter 退出"` | 命令行参数 `--no-pause` 或 `stdin().read_line()` |
| 错误处理 | `try/catch` | `Result<T, E>` + `?` 操作符 |

### 注意事项

1. `serde_json::Value` 的 `$path` 这种带 `$` 的 key 可以直接用字符串索引：`model["groups"]["c/cpp"]["$path"]`
2. `c/cpp` 键名含 `/`，用字符串索引即可，不需要特殊处理
3. `$outputBin` 同样带 `$`，字符串索引即可
4. 需要处理 `serde_json::Value` 的 `as_object_mut()` 和 `as_array_mut()` 模式匹配
5. Windows 上获取 home 目录：直接用 `std::env::var("USERPROFILE")` 最直接
6. `--no-pause` 参数：考虑到可能在 OpenCode/CI 中运行，支持跳过手动确认

## 解决方案

创建 `tools/fix_c251_model.rs`，遵循 cargo-script 规范：
- 顶部嵌入 Cargo 清单
- 使用 `serde_json::Value` 动态操作 JSON
- 使用 `colored` 做彩色终端输出
- 支持 `--no-pause` 命令行参数
- 保持与 PowerShell 原版相同的功能和输出风格

## 总结

| 确认项 | 状态 |
|--------|------|
| 遵循 Rust 单文件脚本指南 | ✅ |
| 功能与 PS 原版一一对应 | ✅ |
| 外部依赖最小化（2 个 crate） | ✅ |
| 彩色终端输出 | ✅ |
| 错误处理完善 | ✅ |
| 支持非交互式运行 | ✅ |
