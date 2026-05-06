#!/usr/bin/env cargo
---
[package]
edition = "2024"

[dependencies]
colored = "2"
anyhow = "1"
---

//! # AI8051U FOC 项目构建脚本
//!
//! 单文件 Rust 构建脚本，替代 Makefile，编译 Keil C251 项目。
//!
//! ## 用法
//!
//! ```powershell
//! # 在项目根目录运行:
//! cargo +nightly -Zscript tools\builder.rs build    # 编译 + 链接
//! cargo +nightly -Zscript tools\builder.rs compile  # 仅编译
//! cargo +nightly -Zscript tools\builder.rs link     # 仅链接
//! cargo +nightly -Zscript tools\builder.rs clean    # 清理
//! cargo +nightly -Zscript tools\builder.rs rebuild  # 清理 + 重建
//! cargo +nightly -Zscript tools\builder.rs flash    # 烧录
//! cargo +nightly -Zscript tools\builder.rs info     # 显示项目信息
//! ```
//!
//! ## 前提
//!
//! - Keil C251 安装在 `C:\Keil_v5\C251\`
//! - Rust nightly 工具链 (`rustup toolchain install nightly`)
//! - 在项目根目录运行（脚本通过 CWD 定位文件）

use std::ffi::OsStr;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use anyhow::{bail, Context, Result};
use colored::Colorize;

// =========================== 常量 ===========================

const C251: &str = r"C:\Keil_v5\C251\BIN\C251.EXE";
const L251: &str = r"C:\Keil_v5\C251\BIN\L251.EXE";

const SRC_DIR: &str = "Sources";
const INC_DIR: &str = "Sources\\inc";
const STC_INC: &str = "Sources\\inc\\stc";
const BUILD_DIR: &str = "Objects";

// 库文件
const USB_LIB: &str = "Sources\\lib\\stc_usb_cdc_32g_xdata.LIB";
const TARGET: &str = "Objects\\03-March_Wheel_leg_FOC.hex";

// C251 编译选项
const C251_FLAGS: &[&str] = &["LARGE", "DEBUG", "SYMBOLS"];

// =========================== 辅助函数 ===========================

/// 彩色输出
fn ok(msg: &str)  { println!("  {} {}", "[OK]".green(), msg); }
fn err(msg: &str) { eprintln!("  {} {}", "[ERROR]".red(), msg); }
fn info(msg: &str){ println!("  {} {}", "[INFO]".cyan(), msg); }
fn step(msg: &str){ println!("{} {}", "🔨".bold(), msg.cyan().bold()); }

/// 确保目录存在
fn ensure_dir(dir: &str) -> Result<()> {
    if !Path::new(dir).exists() {
        fs::create_dir_all(dir)
            .with_context(|| format!("创建目录失败: {}", dir))?;
        println!("  📁 创建目录: {}", dir.to_string().dimmed());
    }
    Ok(())
}

/// 执行命令并检查输出中是否有 Keil 编译错误
/// Keil 错误格式: *** ERROR Cxxx ... 或 *** ERROR Lxxx ...
/// 注意：Eval 版本即使成功也可能返回非零退出码，所以不依赖 exit code
fn run_keil_tool(program: &str, args: &[impl AsRef<OsStr>]) -> Result<String> {
    let mut cmd = Command::new(program);
    for a in args {
        cmd.arg(a.as_ref());
    }
    let output = cmd.output()
        .with_context(|| format!("执行失败: {}", program))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let combined = format!("{}{}", stdout, stderr);

    if combined.contains("*** ERROR") {
        eprintln!("{}", combined);
        bail!("{} 返回错误", program);
    }
    Ok(combined)
}

/// 扫描目录获取所有 .c 文件
fn find_c_sources(dir: &str) -> Result<Vec<PathBuf>> {
    let mut sources = Vec::new();
    for entry in fs::read_dir(dir)
        .with_context(|| format!("无法读取目录: {}", dir))?
    {
        let entry = entry?;
        let path = entry.path();
        if path.extension().map_or(false, |e| e == "c") {
            sources.push(path);
        }
    }
    sources.sort();
    Ok(sources)
}

// =========================== 构建命令 ===========================

/// 编译: 所有 .c → .obj
fn compile() -> Result<()> {
    step("编译中...");
    ensure_dir(BUILD_DIR)?;
    ensure_dir("Listings")?;

    let sources = find_c_sources(SRC_DIR)?;
    if sources.is_empty() {
        bail!("未找到 .c 源文件 ({})", SRC_DIR);
    }

    for src in &sources {
        let stem = src.file_stem().unwrap().to_string_lossy();
        let obj = format!("{}\\{}.obj", BUILD_DIR, stem);
        let src_path = src.to_string_lossy().to_string();

        println!("  {} → {}", src_path.dimmed(), obj.dimmed());

        let mut args: Vec<String> = vec![src_path.clone()];
        args.extend(C251_FLAGS.iter().map(|s| s.to_string()));
        args.push(format!("INCDIR({})", INC_DIR));
        args.push(format!("INCDIR({})", STC_INC));
        args.push(format!("OBJECT({})", obj));
        args.push(format!("PRINT(Listings\\{}.lst)", stem));

        run_keil_tool(C251, &args)?;
    }

    ok(&format!("编译完成 ({} 个文件)", sources.len()));
    Ok(())
}

/// 链接: 所有 .obj + LIB → .HEX
fn link() -> Result<()> {
    step("链接中...");
    ensure_dir(BUILD_DIR)?;

    // 收集所有 .obj 文件
    let mut obj_list = String::new();
    for entry in fs::read_dir(BUILD_DIR)
        .with_context(|| format!("无法读取 build 目录: {}", BUILD_DIR))?
    {
        let entry = entry?;
        let path = entry.path();
        if path.extension().map_or(false, |e| e == "obj") {
            if !obj_list.is_empty() {
                obj_list.push(',');
            }
            obj_list.push_str(&path.to_string_lossy());
        }
    }

    if obj_list.is_empty() {
        bail!("未找到 .obj 文件 ({}), 请先运行 compile", BUILD_DIR);
    }

    obj_list.push(',');
    obj_list.push_str(USB_LIB);

    println!("  {} → {}", obj_list.dimmed(), TARGET.dimmed());

    run_keil_tool(L251, &[&obj_list, "TO", TARGET])?;

    // 确认 HEX 文件已生成
    if Path::new(TARGET).exists() {
        let size = fs::metadata(TARGET)?.len();
        ok(&format!("链接完成: {} ({} bytes)", TARGET, size));
    } else {
        bail!("HEX 文件未生成: {}", TARGET);
    }

    Ok(())
}

/// 清理构建产物
fn clean() -> Result<()> {
    step("清理构建产物...");
    let mut count = 0u32;

    // 清理 Objects/ 目录
    if Path::new(BUILD_DIR).exists() {
        let patterns = &["*.obj", "*.hex", "*.map", "*.m51", "*.lst"];
        for entry in fs::read_dir(BUILD_DIR)? {
            let entry = entry?;
            let name = entry.file_name().to_string_lossy().to_string();
            if patterns.iter().any(|p| {
                let pat = p.trim_start_matches("*.");
                name.ends_with(pat)
            }) {
                fs::remove_file(entry.path())?;
                count += 1;
            }
        }
    }

    // 清理 Listings/ 目录
    if Path::new("Listings").exists() {
        for entry in fs::read_dir("Listings")? {
            let entry = entry?;
            let name = entry.file_name().to_string_lossy().to_string();
            if name.ends_with(".lst") || name.ends_with(".map") {
                fs::remove_file(entry.path())?;
                count += 1;
            }
        }
    }

    ok(&format!("清理完成 ({} 个文件)", count));
    Ok(())
}

/// 重建
fn rebuild() -> Result<()> {
    clean()?;
    compile()?;
    link()?;
    Ok(())
}

/// 项目信息
fn show_info() -> Result<()> {
    let sources = find_c_sources(SRC_DIR).unwrap_or_default();
    println!();
    let bar = "=".repeat(60);
    println!("{}", bar.cyan());
    println!("  {}", "AI8051U FOC 项目信息".cyan().bold());
    println!("{}", bar.cyan());
    println!("  芯片:     AI8051U (80251 兼容, LQFP48, 36MHz)");
    println!("  编译器:   Keil C251 V5");
    println!("  C251:     {}", C251.dimmed());
    println!("  L251:     {}", L251.dimmed());
    println!("  源文件:   ({} 个)", sources.len());
    for s in &sources {
        println!("    {}", s.display().to_string().dimmed());
    }
    println!("  库文件:");
    println!("    {}", USB_LIB.dimmed());
    println!("  头文件 (STC):");
    println!("    {}", STC_INC.dimmed());
    println!("  输出:     {}", TARGET.dimmed());
    println!("{}", bar.cyan());
    println!("  命令:");
    println!("    cargo +nightly -Zscript tools\\builder.rs [build|compile|link|clean|rebuild|info]");
    println!("{}", bar.cyan());
    println!();
    Ok(())
}

/// 烧录（调用 AiCube-ISP）
fn flash() -> Result<()> {
    step("烧录中...");

    if !Path::new(TARGET).exists() {
        bail!("HEX 文件不存在: {} (请先运行 build)", TARGET);
    }

    let isp = r"tools\AiCube-ISP-v6.96V-plus.exe";
    if Path::new(isp).exists() {
        info(&format!("启动烧录工具: {}", isp));
        Command::new(isp)
            .arg("/auto")
            .arg(TARGET)
            .spawn()
            .with_context(|| "启动烧录工具失败")?;
        ok("烧录命令已发送");
    } else {
        err(&format!("未找到烧录工具: {}", isp));
        info("请手动打开 AiCube-ISP 烧录 HEX 文件");
    }
    Ok(())
}

// =========================== 入口 ===========================

fn main() -> Result<()> {
    // 获取命令行参数
    let args: Vec<String> = std::env::args().collect();
    let cmd = if args.len() > 1 { args[1].as_str() } else { "build" };

    let cwd = std::env::current_dir()?;
    println!("  📂 项目目录: {}", cwd.display().to_string().dimmed());

    match cmd {
        "build"   => { compile()?; link()?; }
        "compile" => compile()?,
        "link"    => link()?,
        "clean"   => clean()?,
        "rebuild" => rebuild()?,
        "flash"   => flash()?,
        "info"    => show_info()?,
        _ => {
            eprintln!("  {} 未知命令: {}", "[!]".yellow(), cmd.yellow());
            show_info()?;
        }
    }

    Ok(())
}
