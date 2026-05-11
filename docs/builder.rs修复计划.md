# builder.rs 修复计划

> 日期：2026-05-11

---

## 一、问题诊断

通过对 C251.EXE 直接测试，确认了以下问题：

### 1.1 选项对照表

| 选项含义 | `.uvproj` 配置 | 正确的命令行 | builder.rs (现状) | Makefile (现状) |
|----------|---------------|-------------|-------------------|-----------------|
| 大内存模型 | MemoryModel=4 | **`LARGE`** ✅ | `LARGE` | `LARGE` |
| 大 ROM | RomSize=3 | **`ROM(LARGE)`** ✅ | ❌ 缺失 | ❌ 缺失 |
| 4字节中断帧 | uFrame4=1 | **`INTR2`** ✅ | ❌ 缺失 | ❌ `INTERRUPT(4)` (无效) |
| 源码模式 | uSrcBin=1 | **`SRC`** ✅ | ❌ 缺失 | ❌ 缺失 |
| 优化 | Optim=7, SizSpd=1 | **`OPTIMIZE(7, SPEED)`** ✅ | ❌ 缺失 | ❌ 缺失 |
| 警告级别 | wLevel=2 | **`WARNINGLEVEL(2)`** ✅ | ❌ 缺失 | ❌ 缺失 |
| 调试信息 | — | **`DEBUG`** ✅ | `DEBUG` | `DEBUG` |
| 符号表 | — | **`SYMBOLS`** ✅ | `SYMBOLS` | `SYMBOLS` |
| 头文件路径 | IncludePath | **`INCDIR(...)`** ✅ | `INCDIR(...)` (代码实现) | `INCDIR(...)` |

### 1.2 关键发现

🔴 **`INTR2`** 才是正确的 4 字节中断帧选项，不是 `INTERRUPT(4)`！
- `INTERRUPT(4)` → C251 报错 `UNKNOWN CONTROL`
- `INTR2` → 编译通过 ✅

### 1.3 已通过 C251.EXE 验证的命令行

```batch
C251.EXE main.c LARGE ROM(LARGE) INTR2 SRC OPTIMIZE(7, SPEED) WARNINGLEVEL(2) DEBUG SYMBOLS INCDIR(.\Sources\inc)
```

---

## 二、修复内容

### 2.1 修改 C251_FLAGS 常量

```rust
// 修复前
const C251_FLAGS: &[&str] = &[
    "LARGE",
    "DEBUG",
    "SYMBOLS",
];

// 修复后
const C251_FLAGS: &[&str] = &[
    "LARGE",
    "ROM(LARGE)",
    "INTR2",
    "SRC",
    "OPTIMIZE(7, SPEED)",
    "WARNINGLEVEL(2)",
    "DEBUG",
    "SYMBOLS",
];
```

### 2.2 检查链接器部分

链接器当前已经有 `REMOVEUNUSED NOOVERLAY`，与 .uvproj 一致，暂不修改。
但如果链接失败，可能需要添加 `CLASSES` 和 `DISABLEWARNING(16)`。

---

## 三、测试结果 ✅

### 3.1 构建成功

```
🔨 编译中...
  Sources\main.c → Objects\main.obj
  [OK] 编译完成 (编译 1 个, 跳过 0 个)
🔨 链接中...
  Objects\main.obj,...LIB → Objects\03-March_Wheel_leg_FOC.hex
  [OK] 链接完成: Objects\03-March_Wheel_leg_FOC.hex (37920 bytes)
```

### 3.2 验证结果

| 验证项 | 状态 | 详情 |
|--------|------|------|
| main.obj | ✅ 生成 | 14,767 bytes |
| main.lst | ✅ 生成 | 17,037 bytes, 0 WARNING, 0 ERROR |
| .hex 文件 | ✅ 生成 | 37,920 bytes |
| INTR2 生效 | ✅ | .lst 第 6 行确认 |
| ROM(LARGE) 生效 | ✅ | .lst 第 6 行确认 |
| OPTIMIZE(7,SPEED) 生效 | ✅ | .lst 第 6 行确认 |
| Code 大小 | ✅ | 259 bytes (仅 main 模块) |
| XDATA 使用 | ✅ | 2 bytes (tick_10ms) |

### 3.3 踩坑记录

- **`SRC` 选项会阻止 .obj 生成！** `.uvproj` 中 `uSrcBin=1` 是 CPU 模式（Source 251 native），不是命令行 `SRC` 选项
- **`INTERRUPT(4)` 是无效选项**，C251 报错 `UNKNOWN CONTROL`。正确选项是 `INTR2`
