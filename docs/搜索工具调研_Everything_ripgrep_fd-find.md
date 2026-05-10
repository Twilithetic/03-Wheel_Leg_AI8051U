# 搜索工具调研：Everything / ripgrep / fd-find

> 📅 记录日期：2026-05-10  
> 📝 记录原因：了解 Everything 的开发语言，顺带调研了 Rust 生态里的两个明星搜索工具

---

## 一、Everything（Voidtools）

### 基本信息

| 项目 | 内容 |
|------|------|
| 官网 | https://www.voidtools.com |
| 作者 | David Carpenter（单人开发） |
| 首次发布 | 2004年12月22日 |
| 最新稳定版 | 1.4.1.1030（2025-09-04） |
| 平台 | Windows only（NT 4.0 ~ Win11） |
| 许可证 | MIT License |

### 开发语言

```
98%  C
 1%  C++
 1%  Assembly（汇编）
```

- **不依赖任何 GUI 库**（没用 Qt、GTK、wxWidgets），直接用 Win32 API 创建窗口
- 源码中 SDK 和 ES 命令行工具的代码随下载包附带

### 为什么这么快？

直接读取 **NTFS 文件系统的 Master File Table (MFT)**，而不是逐个遍历文件。MFT 是 NTFS 文件系统的元数据索引表，Everything 启动时扫描一次 MFT 建内存索引，之后通过 USN Journal 增量更新。

### Rust 相关

- **没有完整的 Rust 重写版本**
- 有一个 Rust FFI 绑定：[Ciantic/everything-sys-rs](https://github.com/Ciantic/everything-sys-rs)
  - 封装了 Everything 的 C SDK，让 Rust 程序可以调用 Everything 的搜索功能
  - 仍然需要安装 Everything 本体

### 同类替代品

| 工具 | 平台 | 语言 |
|------|------|------|
| FSearch | Linux | C + GTK3 |
| Recoll | 跨平台 | C++ + Qt |
| WinFindr | Windows | 未公开 |

---

## 二、ripgrep (`rg`)

### 基本信息

| 项目 | 内容 |
|------|------|
| 仓库 | https://github.com/BurntSushi/ripgrep |
| 作者 | Andrew Gallant（BurntSushi） |
| 语言 | Rust |
| 平台 | Windows / Linux / macOS |
| 功能 | **搜索文件内容**（文本搜索） |
| 安装 | `cargo install ripgrep` |

### 定位

ripgrep 是 `grep` 的现代替代品 —— 在当前目录递归搜索文件**内容**中匹配正则表达式的行。

### 核心特点

- 🚀 **极快**：作者做了 25 个 benchmark，碾压 grep、ag、git grep、ucg、pt、sift
- 🎨 **彩色输出**：匹配内容高亮
- 🧠 **默认聪明**：自动跳过 `.gitignore` 文件、隐藏文件、二进制文件
- 🌍 **完整 Unicode 支持**：中英文都 OK
- 🔒 **只读不写**：纯搜索，不修改任何文件

### 常用命令

```bash
rg "关键词"                    # 在当前目录搜文件内容
rg -l "关键词"                 # 只列出匹配的文件名
rg -c "关键词"                 # 统计匹配行数
rg --type-add 'c:*.c' -tc "xxx"  # 限定文件类型
```

### 趣闻

作者取名的过程：
- 想用 Rust 的 "r" 开头
- 想到了 "rip" 有"快速翻阅"的意思
- "RIP" 同时也是 "Rest in Peace" 的缩写 → "ripgrep kills grep" 😄

---

## 三、fd-find (`fd`)

### 基本信息

| 项目 | 内容 |
|------|------|
| 仓库 | https://github.com/sharkdp/fd |
| 作者 | David Peter（sharkdp） |
| 语言 | Rust |
| 平台 | Windows / Linux / macOS |
| 功能 | **搜索文件名/路径**（文件查找） |
| 安装 | `cargo install fd-find` |

### 定位

fd-find 是 `find` 命令的现代替代品 —— 按文件名/模式查找文件。

### 核心特点

- ⚡ **比 find 快**：benchmark 显示约 5~9 倍于 `find`
- 🎨 **彩色输出**：类似 `ls` 的彩色效果
- 🧠 **默认聪明**：自动跳过隐藏文件、`.gitignore` 文件
- 📝 **智能大小写**：默认不区分大小写；但如果搜索模式含大写字母，自动切换为区分大小写
- 🔀 **并行命令执行**：`-x` 对每个结果执行命令（类似 GNU Parallel）
- 😄 **名字短**：`fd` vs `find`，少打 2 个字母

### 常用命令

```bash
fd PATTERN                 # 搜文件名
fd -e c                    # 搜扩展名为 .c 的文件
fd -t d                    # 只搜目录
fd -S +1M                  # 搜大于 1MB 的文件
fd -x command {}           # 对每个结果执行命令
fd --changed-within 1h     # 搜最近1小时修改的文件
```

### vs find 语法对比

| 传统 find | fd |
|-----------|-----|
| `find . -iname '*pwm*.c'` | `fd pwm -e c` |
| `find . -type f -name '*.h'` | `fd -e h` |
| `find . -type d -name 'src'` | `fd -t d src` |

---

## 四、三兄弟对比

```
                    你想找什么？
                         │
         ┌───────────────┼───────────────┐
         ▼               │               ▼
    找"文件名"           │          找"文件内容"
         │               │               │
  ┌──────────────┐       │       ┌──────────────┐
  │  Everything   │       │       │   ripgrep    │
  │  (C 语言)     │       │       │   (Rust)     │
  │  Windows 专用  │       │       │   跨平台      │
  │  读 NTFS MFT   │       │       │   逐文件搜索   │
  │  极快 ⚡       │       │       │   很快 🚀     │
  └──────────────┘       │       └──────────────┘
         │               │
         ▼               │
  ┌──────────────┐       │
  │   fd-find    │       │
  │   (Rust)     │       │
  │   跨平台      │       │
  │   遍历目录树   │       │
  │   比 find 快  │       │
  └──────────────┘       │
```

### 一句话区分

| 工具 | 搜什么 | 相当于 |
|------|--------|--------|
| Everything | 文件名（Windows，读 MFT 索引） | 超级文件定位器 |
| fd-find | 文件名（跨平台，遍历目录） | 更快的 `find` |
| ripgrep | 文件**内容**（跨平台） | 更快的 `grep` |

---

## 五、实用建议

- **Windows 开发**：Everything + ripgrep 组合最佳（一个找文件一个找内容）
- **跨平台/服务器**：fd-find + ripgrep 是标准搭配
- **VSCode 用户**：其实你已经在用 ripgrep 了 —— VSCode 的"在文件中搜索"底层就是 ripgrep！
- 安装一行搞定：`cargo install ripgrep fd-find`

---

## 六、信息来源

- Stack Overflow: [Everything Search Engine - what language?](https://stackoverflow.com/questions/27461843/everything-search-engine)
- Wikipedia: [Everything (software)](https://en.wikipedia.org/wiki/Everything_(software))
- voidtools 官方论坛 & 官网
- [BurntSushi/ripgrep](https://github.com/burntsushi/ripgrep)
- [sharkdp/fd](https://github.com/sharkdp/fd)
- [ripgrep 官方博文：ripgrep is faster than {grep, ag, git grep, ucg, pt, sift}](https://blog.burntsushi.net/ripgrep/)
