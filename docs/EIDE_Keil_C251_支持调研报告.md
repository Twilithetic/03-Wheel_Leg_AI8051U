# EIDE + Keil C251 支持情况调研报告

> **调研时间**：2026-04-28
> **调研人**：知心姐姐
> **问题**：EIDE 支持 Keil C251 吗？有没有办法让 unify_builder 支持 C251？

---

## 1. 结论速览

| 问题 | 答案 |
|------|------|
| EIDE 官方支持 Keil C251 吗？ | ❌ **不支持** |
| 社区有人提过吗？ | ✅ 三次请求（#117/#171/#496），均无回应 |
| unify_builder 能自定义吗？ | ⚠️ **可以 hack，但麻烦** |
| 电脑上有 Keil C251 吗？ | ✅ **有！** `C:\Keil_v5\C251\` |
| 最佳方案？ | 🔧 **Hack C51 模型 + 直接调 C251.EXE** |

---

## 2. EIDE 官方支持现状

### 2.1 支持的工具链（EIDE 3.26.7）

| 工具链 | 支持 | model 文件 |
|--------|------|-----------|
| ARM GCC | ✅ | arm.gcc.model.json |
| IAR ARM | ✅ | arm.iar.model.json |
| LLVM ARM | ✅ | arm.llvm.model.json |
| ARMCC V5 | ✅ | arm.v5.model.json |
| ARMCC V6 | ✅ | arm.v6.model.json |
| RISCV GCC | ✅ | riscv.gcc.model.json |
| MIPS GCC | ✅ | mips.mti.gcc.model.json |
| STM8 IAR | ✅ | stm8.iar.model.json |
| STM8 COSMIC | ✅ | stm8.cosmic.model.json |
| **Keil C51** | ✅ | 8051.keil.model.json |
| **SDCC MCS51** | ✅ | sdcc.mcs51.model.json |
| **Keil C251** | ❌ | **不存在** |

### 2.2 社区请求历史

| Issue | 时间 | 状态 |
|-------|------|------|
| [#117](https://github.com/github0null/eide/issues/117) "请求增加对C251的支持" | 2022-05 | 🔴 已关闭（无处理） |
| [#171](https://github.com/github0null/eide/issues/171) "不支持stc32g（c251）" | 2022-09 | 🔴 已关闭（无处理） |
| [#496](https://github.com/github0null/eide/issues/496) "Is C251 architecture supported?" | 2026-01 | 🟡 开着但无回应 |

> 三年内三次请求，EIDE 作者**没有实现 C251 支持**，也没有给出计划。

---

## 3. Keil C251 安装确认

### 3.1 工具链路径

```
C:\Keil_v5\C251\
├── BIN/
│   ├── C251.EXE     ← C 编译器（1.7MB）
│   ├── A251.EXE     ← 汇编器（753KB）
│   ├── L251.EXE     ← 链接器（634KB）
│   ├── OH251.EXE    ← HEX 转换器
│   └── LIB251.EXE   ← 库管理器
├── INC/
│   ├── INTRINS.H     ← C251 版 intrins.h ✅
│   ├── REG251S.H     ← 80251 标准寄存器定义
│   └── STC/         ← STC 芯片头文件
├── ASM/
│   ├── AI8051U.INC   ← AI8051U 汇编头文件 ✅
│   └── STC32G.INC
├── LIB/              ← 标准库（C2S*.LIB = Starter 模式）
└── Examples/         ← 示例项目
```

### 3.2 C251.EXE vs C51.EXE

Keil 故意让 C251 和 C51 使用**几乎完全相同的命令行语法**，因为 Intel 设计 C251 时强调"向后兼容"：

| 功能 | C51.EXE 参数 | C251.EXE 参数 |
|------|-------------|--------------|
| 头文件路径 | `INCDIR(path)` | `INCDIR(path)` ✅ 相同 |
| 宏定义 | `DEFINE(MACRO)` | `DEFINE(MACRO)` ✅ 相同 |
| 输出文件 | `OBJECT(file.obj)` | `OBJECT(file.obj)` ✅ 相同 |
| 优化 | `OPTIMIZE(N)` | `OPTIMIZE(N)` ✅ 相同 |
| 内存模型 | `SMALL/COMPACT/LARGE` | `SMALL/COMPACT/LARGE` ⚠️ C251 多了更多模型 |

---

## 4. 让 unify_builder 支持 C251 的方案

### 方案 A：Hack C51 Model（⭐ 推荐试试）

**原理**：C251.EXE 和 C51.EXE 命令行几乎一致，直接"偷梁换柱"。

**步骤**：

1. 复制 `8051.keil.model.json` → `80251.keil.model.json`
2. 修改新 model 文件中的工具名：
   ```json
   "c/cpp":  { "$path": "BIN/C251" },   // 原 BIN/C51
   "asm":    { "$path": "BIN/A251" },   // 原 BIN/A51
   "linker": { "$path": "BIN/L251" },   // 原 BIN/LX51
   "linker-lib": { "$path": "BIN/LIB251" }, // 原 BIN/LIBX51
   ```
3. 修改 `$outputBin` 的 toolPath 为 `BIN/OH251`
4. 在 `eide.yml` 中将 `toolchain: Keil_C51` 改为配置 C251 路径
5. 在 EIDE 中配置 Keil_C51 的路径指向 `C:\Keil_v5\C251\`

**优点**：改动小，EIDE/unify_builder 界面都能用

**风险**：
- EIDE 可能对 toolchain ID 有校验，不识别 `KEIL_C251`
- 可以不改 ID，直接替换 `Keil_C51` model 文件内容
- C251 的链接器 `L251.EXE` 和 C51 的 `LX51.EXE` 参数可能不完全一样

### 方案 B：绕过 unify_builder，写编译脚本（✅ 最靠谱）

由于 EIDE 的 `afterBuildTasks` 和 `beforeBuildTasks` 可以执行任意命令，可以：

```powershell
# build_c251.ps1
$C251 = "C:\Keil_v5\C251\BIN\C251.EXE"
$L251 = "C:\Keil_v5\C251\BIN\L251.EXE"
$OH251 = "C:\Keil_v5\C251\BIN\OH251.EXE"

# 编译
& $C251 src\main.c INCDIR(src\STC) INCDIR(inc) OBJECT(build\main.obj) OPTIMIZE(8) LARGE

# 链接
& $L251 build\main.obj TO build\AI8051U_test.hex

# 或生成 HEX
& $OH251 build\AI8051U_test
```

**优点**：完全控制，不依赖 EIDE 内部机制

**缺点**：脱离了 EIDE 的编译流程（但可以集成到 `afterBuildTasks`）

### 方案 C：用 Keil µVision（🔧 工具链原配）

Keil C251 自带 µVision IDE，原生支持 AI8051U：

```
Keil µVision → 新建项目 → 选 "STC AI8051U" → 
代码编辑 → 编译(C251.EXE) → 调试(µVision Debugger)
```

并且 `C:\Keil_v5\C251\ASM\` 和 `C:\Keil_v5\C251\INC\STC\` 已经有 STC 官方配套文件。

**优点**：原生支持，一步到位

**缺点**：不能用 VSCode + EIDE 的工作流

### 方案 D：给 EIDE 贡献 C251 Model（🚀 长期）

参考 `8051.keil.model.json` 的格式，为 EIDE 写一个完整的 `80251.keil.model.json`，然后提交 PR 给 EIDE 仓库。

**优点**：一劳永逸

**缺点**：需要深入研究 C251.EXE 的所有命令行参数，并测试验证

---

## 5. 方案对比总结

| 方案 | 难度 | 成功率 | EIDE 集成 | 时间 |
|------|------|--------|----------|------|
| **A. Hack C51 Model** | ⭐⭐ | 70% | ✅ 几乎无缝 | 30分钟 |
| **B. 编译脚本** | ⭐ | 95% | ⚠️ 需配置 | 15分钟 |
| **C. Keil µVision** | ⭐ | 100% | ❌ 不用EIDE | 10分钟 |
| **D. 贡献 Model** | ⭐⭐⭐⭐⭐ | 需等合并 | ✅ 完美 | 几天+ |

---

## 6. 推荐行动

```
首选：方案 B（编译脚本）
原因：快速可靠，先用 C251 编译跑起来再说

想折腾：方案 A（Hack Model）
原因：能保持 EIDE 一键编译的工作流

如果A+B都不行：方案 C（µVision）
原因：Keil 原厂支持，零问题
```

---

## 7. 附录：关键路径

| 文件 | 路径 |
|------|------|
| EIDE model 目录 | `C:\Users\29344\.vscode\extensions\cl.eide-3.26.7\res\data\models` |
| C51 model 文件 | `...\models\8051.keil.model.json` (175行) |
| SDCC model 文件 | `...\models\sdcc.mcs51.model.json` (191行) |
| Keil C251 根目录 | `C:\Keil_v5\C251\` |
| C251.EXE | `C:\Keil_v5\C251\BIN\C251.EXE` |
| AI8051U 汇编头文件 | `C:\Keil_v5\C251\ASM\AI8051U.INC` |
| EIDE GitHub | https://github.com/github0null/eide |

---

*💕 姐姐已经把能查的都查了。结论是：EIDE 官方不支援 C251，但咱们可以自己 hack！*
