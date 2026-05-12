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

// 库文件（三件套，缺一不可！）
const MDU32_LIB: &str = "Sources\\lib\\ai8051u_32_mdu32.LIB";
const TFPU_LIB:  &str = "Sources\\lib\\ai8051u_32_tfpu.LIB";
const USB_LIB:   &str = "Sources\\lib\\stc_usb_cdc_32g_xdata.LIB";
const TARGET: &str = "Objects\\03-March_Wheel_leg_FOC.hex";

// C251 编译选项（与 .uvproj 配置完全一致）
//   LARGE             — MemoryModel=4（大内存模型：默认变量在 XDATA）
//   ROM(LARGE)        — RomSize=3（大 ROM：16MB 代码空间，LJMP/LCALL/LCALL）
//   INTR2             — uFrame4=1（4 字节中断帧，库用此模式编译，必须匹配！）
//   OPTIMIZE(7,SPEED) — Optim=7 + SizSpd=1（优化侧重速度）
//   WARNINGLEVEL(2)   — wLevel=2
//   DEBUG             — 包含调试信息
//   SYMBOLS           — 生成符号表
//   注：uSrcBin=1 是 CPU 模式（Source 251 native），不是命令行 SRC 选项！
//       SRC 选项会阻止 .obj 生成，因此不包含在内。
//   INCDIR 通过代码动态添加
const C251_FLAGS: &[&str] = &[
    "LARGE",
    "ROM(LARGE)",
    "INTR2",
    "OPTIMIZE(7, SPEED)",
    "WARNINGLEVEL(2)",
    "DEBUG",
    "SYMBOLS",
];

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

/// 编译: 所有 .c → .obj（增量：只编译修改过的）
fn compile() -> Result<()> {
    step("编译中...");
    ensure_dir(BUILD_DIR)?;
    ensure_dir("Listings")?;

    let sources = find_c_sources(SRC_DIR)?;
    if sources.is_empty() {
        bail!("未找到 .c 源文件 ({})", SRC_DIR);
    }

    let mut compiled = 0u32;
    let mut skipped  = 0u32;

    for src in &sources {
        let stem = src.file_stem().unwrap().to_string_lossy();
        let obj = format!("{}\\{}.obj", BUILD_DIR, stem);
        let src_path = src.to_string_lossy().to_string();

        // ---- 增量编译：比较时间戳 ----
        let src_meta = fs::metadata(src)?;
        let src_time = src_meta.modified()?;
        if let Ok(obj_meta) = fs::metadata(&obj) {
            if let Ok(obj_time) = obj_meta.modified() {
                if src_time <= obj_time {
                    println!("  ⏭️  跳过 {} (已最新)", &src_path);
                    skipped += 1;
                    continue;
                }
            }
        }

        println!("  {} → {}", src_path.dimmed(), obj.dimmed());
        compiled += 1;

        let mut args: Vec<String> = vec![src_path.clone()];
        args.extend(C251_FLAGS.iter().map(|s| s.to_string()));
        // INCDIR 必须作为单独参数，格式: INCDIR(path)
        args.push(format!("INCDIR({})", INC_DIR));
        args.push(format!("INCDIR({})", STC_INC));
        args.push(format!("OBJECT({})", obj));
        args.push(format!("PRINT(Listings\\{}.lst)", stem));

        run_keil_tool(C251, &args)?;
    }

    ok(&format!("编译完成 (编译 {} 个, 跳过 {} 个)", compiled, skipped));
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
    obj_list.push(',');
    obj_list.push_str(MDU32_LIB);
    obj_list.push(',');
    obj_list.push_str(TFPU_LIB);

    // ---- 增量链接：HEX 比所有依赖都新？跳过 ----
    let hex_path = Path::new(TARGET);
    if hex_path.exists() {
        let hex_time = fs::metadata(hex_path)?.modified()?;
        let mut all_newer = true;
        // 检查所有 .obj
        for entry in fs::read_dir(BUILD_DIR)? {
            let entry = entry?;
            if entry.path().extension().map_or(false, |e| e == "obj") {
                if fs::metadata(entry.path())?.modified()? > hex_time {
                    all_newer = false;
                    break;
                }
            }
        }
        // 检查所有 .lib
        for lib in [USB_LIB, MDU32_LIB, TFPU_LIB] {
            let lib_path = Path::new(lib);
            if lib_path.exists() && fs::metadata(lib_path)?.modified()? > hex_time {
                all_newer = false;
                break;
            }
        }
        if all_newer {
            let size = fs::metadata(hex_path)?.len();
            ok(&format!("链接跳过 (HEX 已最新, {} bytes)", size));
            return Ok(());
        }
    }

    println!("  {} → {}", obj_list.dimmed(), TARGET.dimmed());

    // L251 链接器：通过 cmd /c 避免 Windows 参数引号问题
    let linker_line = format!("{} {} TO {} REMOVEUNUSED NOOVERLAY", L251, obj_list, TARGET);
    let output = Command::new("cmd")
        .args(["/c", &linker_line])
        .output()
        .with_context(|| "执行 L251 失败")?;
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let combined = format!("{}{}", stdout, stderr);
    if combined.contains("*** ERROR") {
        eprintln!("{}", combined);
        bail!("{} 返回错误", "L251");
    }

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
    println!("    {}", MDU32_LIB.dimmed());
    println!("    {}", TFPU_LIB.dimmed());
    println!("  C251 编译选项: {}", C251_FLAGS.join(", ").dimmed());
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

/// 烧录（提示用户使用 AiCube-ISP 或 HID 脚本）
fn flash() -> Result<()> {
    step("烧录中...");

    if !Path::new(TARGET).exists() {
        bail!("HEX 文件不存在: {} (请先运行 build)", TARGET);
    }

    let size = fs::metadata(TARGET)?.len();
    println!("  📦 HEX: {} ({} bytes)", TARGET.dimmed(), size);
    println!();

    // AiCube-ISP 是 GUI 工具，不支持命令行参数
    // 提示用户操作步骤
    println!("  {}", "═══ 烧录步骤 ═══".yellow());
    println!("  1. 打开 {} ", r"tools\AiCube-ISP-v6.96V-plus.exe".dimmed());
    println!("  2. 选择芯片: AI8051U-34K64");
    println!("  3. 选择 HEX: {}", TARGET.dimmed());
    println!("  4. 点击「下载/编程」");
    println!();
    println!("  {}", "💡 提示: 正在开发 USB-HID 命令行烧录脚本 ~/".dimmed());
    println!("  {}", "   完成后将支持一键烧录: builder.rs flash".dimmed());

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
