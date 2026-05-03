#!/usr/bin/env cargo
---
[package]
edition = "2024"

[dependencies]
anyhow = "1"
serde_json = "1"
colored = "2"
---

//! # fix_c251_model.rs
//!
//! EIDE C251 Model 自动修复脚本 (Rust 重写)
//!
//! 每次 EIDE 升级后运行此脚本，自动将 Keil C51 模型替换为 C251 配置。
//!
//! ## 用法
//!
//! ```powershell
//! # 标准运行（带按 Enter 退出提示）
//! cargo +nightly -Zscript tools\fix_c251_model.rs
//!
//! # 非交互式运行（CI/OpenCode 中）
//! cargo +nightly -Zscript tools\fix_c251_model.rs -- --no-pause
//! ```
//!
//! ## 功能
//!
//! 1. 扫描所有 EIDE 版本目录
//! 2. 找到 `8051.keil.model.json` 并检测是否已被 hack
//! 3. 备份原文件 → `.bak`
//! 4. 修改 JSON 中的 5 个工具路径 + 编译选项 + 版本信息
//! 5. 写回文件并输出彩色报告

use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process;

use anyhow::{Context, Result};
use colored::Colorize;
use serde_json::{json, Value};

// =========================== 常量 ===========================

const EIDE_EXT_FILTER: &str = "cl.eide-";
const MODEL_RELPATH: &str = "res/data/models/8051.keil.model.json";
const TARGET_ID: &str = "KEIL_C251";

// =========================== 辅助函数 ===========================

/// 获取用户 home 目录（Windows: USERPROFILE，Unix: HOME）
fn home_dir() -> Option<PathBuf> {
    std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .ok()
        .map(PathBuf::from)
}

/// 获取 VSCode 扩展目录
fn vscode_extensions_dir() -> Option<PathBuf> {
    home_dir().map(|h| h.join(".vscode").join("extensions"))
}

// =========================== 核心逻辑 ===========================

/// 检查 model 是否已被 hack（id 为 KEIL_C251）
fn is_already_hacked(model: &Value) -> bool {
    model
        .get("id")
        .and_then(Value::as_str)
        .map_or(false, |id| id == TARGET_ID)
}

/// 备份原文件 → 同目录下 `.bak`
fn backup_file(model_path: &Path) -> Result<PathBuf> {
    let bak_path = model_path.with_extension("json.bak");
    fs::copy(model_path, &bak_path)
        .with_context(|| format!("备份失败: {}", bak_path.display()))?;
    Ok(bak_path)
}

/// 修改 JSON 对象，执行所有 6 类修改
fn apply_c251_changes(model: &mut Value) -> Result<()> {
    // ① 基本属性
    model["name"] = json!("Keil C251 Compiler");
    model["id"] = json!("KEIL_C251");
    model["version"]["matcher"] =
        json!("^(?<name>C251 COMPILER) V(?<version>\\d[\\d\\.]+)");

    // ② 工具路径（5 个编译器组件）
    model["groups"]["c/cpp"]["$path"] = json!("../C251/BIN/C251");
    model["groups"]["asm"]["$path"] = json!("../C251/BIN/A251");
    model["groups"]["linker"]["$path"] = json!("../C251/BIN/L251");
    model["groups"]["linker-lib"]["$path"] = json!("../C251/BIN/LIB251");

    // ③ HEX 输出工具路径（$outputBin 是数组，取第一个元素）
    if let Some(arr) = model["groups"]["linker"]["$outputBin"].as_array_mut() {
        if let Some(first) = arr.first_mut() {
            first["toolPath"] = json!("../C251/BIN/OH251");
        }
    }

    // ④ 默认编译选项（精简为 C251 兼容的 3 个）
    model["groups"]["c/cpp"]["$default"] = json!(["CODE", "NOCOND", "SYMBOLS"]);

    // ⑤ 移除 use-RTX（C251 不支持）
    if let Some(linker) = model["groups"]["linker"].as_object_mut() {
        linker.remove("use-RTX");
    }

    Ok(())
}

/// 对单个 model 文件执行修复。返回 None 表示跳过，Some(true) 表示修复成功
fn fix_model(model_path: &Path) -> Result<Option<bool>> {
    // Step 1: 读取 JSON
    let content = fs::read_to_string(model_path)
        .with_context(|| format!("无法读取文件: {}", model_path.display()))?;

    let mut model: Value = serde_json::from_str(&content)
        .with_context(|| format!("JSON 解析失败: {}", model_path.display()))?;

    // Step 2: 检查是否已被 hack
    if is_already_hacked(&model) {
        return Ok(None); // 跳过，无需修复
    }

    // Step 3: 备份
    let _bak = backup_file(model_path)?;
    info(&format!("已备份原文件 → {}.bak", model_path.file_stem().unwrap_or_default().to_string_lossy()));

    // Step 4: 修改 JSON
    apply_c251_changes(&mut model)?;

    // Step 5: 写回文件（格式化 + UTF-8 + Unix 换行）
    let new_json = serde_json::to_string_pretty(&model)?;
    // 确保 Unix 换行 (\n)，与 EIDE 原始格式一致
    let new_json = new_json.replace("\r\n", "\n");
    fs::write(model_path, &new_json)
        .with_context(|| format!("写入文件失败: {}", model_path.display()))?;

    Ok(Some(true))
}

// =========================== 输出函数 ===========================

fn ok(msg: &str) {
    println!("  {}       {}", "[OK]".green(), msg);
}

fn skip(msg: &str) {
    println!("  {}     {}", "[SKIP]".yellow(), msg);
}

fn err(msg: &str) {
    eprintln!("  {}    {}", "[ERROR]".red(), msg);
}

fn info(msg: &str) {
    println!("  {}     {}", "[INFO]".cyan(), msg);
}

fn print_header() {
    let line = "=".repeat(60);
    println!();
    println!("{}", line.cyan());
    println!("  {}", "EIDE C251 Model 自动修复脚本".cyan().bold());
    println!(
        "  {}",
        "每次 EIDE 升级后运行此脚本一键恢复 C251 编译支持".dimmed()
    );
    println!("{}", line.cyan());
    println!();
}

fn print_result(fixed: u32, skipped: u32, failed: u32) {
    let line = "=".repeat(60);
    println!("{}", line.cyan());
    println!("  {}", "修复完成!".green().bold());
    println!(
        "  {} {} {}",
        "✅ 已修复:".green(),
        fixed.to_string().green(),
        "个".green()
    );
    if skipped > 0 {
        println!(
            "  {} {} {}",
            "⏭️  已跳过:".yellow(),
            skipped.to_string().yellow(),
            "个".yellow()
        );
    }
    if failed > 0 {
        println!(
            "  {} {} {}",
            "❌ 失败:".red(),
            failed.to_string().red(),
            "个".red()
        );
    }
    println!();
    println!(
        "  {}",
        "提示: 在 VSCode 中点击 EIDE 面板的 🔄 刷新按钮即可生效".dimmed()
    );
    println!("{}", line.cyan());
    println!();
}

// =========================== 入口 ===========================

fn main() -> Result<()> {
    // 解析命令行参数
    let args: Vec<String> = std::env::args().collect();
    let no_pause = args.iter().any(|a| a == "--no-pause");

    print_header();

    // 查找 EIDE 扩展目录
    let ext_dir = match vscode_extensions_dir() {
        Some(d) if d.exists() => d,
        _ => {
            err(&format!(
                "找不到 EIDE 扩展目录: {:?}",
                vscode_extensions_dir()
            ));
            pause_or_exit(no_pause, 1);
        }
    };

    // 扫描所有 EIDE 版本
    let mut eide_dirs: Vec<PathBuf> = Vec::new();
    for entry in fs::read_dir(&ext_dir).with_context(|| "无法读取扩展目录")? {
        let entry = entry?;
        let name = entry.file_name();
        let name_str = name.to_string_lossy();
        if name_str.starts_with(EIDE_EXT_FILTER) && entry.file_type()?.is_dir() {
            eide_dirs.push(entry.path());
        }
    }

    // 按版本号降序排列
    eide_dirs.sort_by(|a, b| {
        b.file_name()
            .unwrap_or_default()
            .cmp(a.file_name().unwrap_or_default())
    });

    if eide_dirs.is_empty() {
        err("未找到 EIDE 安装 (cl.eide-*)");
        pause_or_exit(no_pause, 1);
    }

    println!(
        "{} {} {}",
        "找到".white(),
        eide_dirs.len().to_string().white(),
        "个 EIDE 安装:".white()
    );
    println!();

    let mut fixed = 0u32;
    let mut skipped = 0u32;
    let mut failed = 0u32;

    for eide_dir in &eide_dirs {
        let version = eide_dir
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .replace(EIDE_EXT_FILTER, "");
        let model_path = eide_dir.join(MODEL_RELPATH);

        println!("{}", format!("[{}]", version).white());

        if !model_path.exists() {
            skip("未找到 8051.keil.model.json (此版本可能不包含此文件)");
            skipped += 1;
            println!();
            continue;
        }

        match fix_model(&model_path) {
            Ok(Some(_)) => {
                ok("已修复 → Keil C251 Compiler");
                fixed += 1;
            }
            Ok(None) => {
                skip("已经是 C251 版本，跳过");
                skipped += 1;
            }
            Err(e) => {
                err(&format!("{}", e));
                failed += 1;
            }
        }
        println!();
    }

    print_result(fixed, skipped, failed);

    pause_or_exit(no_pause, 0);
}

fn pause_or_exit(no_pause: bool, exit_code: i32) -> ! {
    if !no_pause {
        eprint!("按 Enter 退出...");
        let _ = io::stdout().flush();
        let _ = io::stdin().read_line(&mut String::new());
    }
    process::exit(exit_code);
}
