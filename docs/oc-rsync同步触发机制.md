# oc-rsync 同步触发机制详解

> 整理日期：2026-05-12  
> 资料来源：rsync 官方手册、GeeksforGeeks、StackOverflow、watchexec 文档、阮一峰 rsync 教程

---

## 一、oc-rsync 是手动工具，不会自己"盯着"文件

**oc-rsync / rsync 本身没有"文件监控"功能。** 它不会像 Dropbox 那样自动检测文件变化并同步。

```
oc-rsync ≈ 一个智能快递员
- 你叫他，他才干活
- 干活时很聪明（只传差异）
- 但不会主动巡逻
```

要想"自动同步"，需要配合一个**文件监控工具**（见第四章）。

---

## 二、运行 oc-rsync 时，它怎么判断"哪些文件要同步"？

### 2.1 三级检测机制

oc-rsync 运行时会逐个对比源文件和目标文件，用**三层递进**的判断：

```
对每个文件：
  │
  ├─ ① 比较文件大小 (size)
  │    ├─ 大小不同？ → 🔴 选入传输列表
  │    └─ 大小相同？ → 进入②
  │
  ├─ ② 比较修改时间 (mtime)
  │    ├─ 时间不同？ → 🟡 选入传输，但启用 delta 算法（只传差异）
  │    └─ 时间相同？ → 进入③（如果有 -c 选项）
  │
  ├─ ③ 【可选，-c 才做】计算 checksum
  │    ├─ checksum 不同？ → 🟡 选入传输
  │    └─ checksum 相同？ → ✅ 跳过！
  │
  └─ 默认（无 -c）：大小和时间都相同 → ✅ 直接跳过！
```

### 2.2 用我们的项目举例

假设刚编译完，`Objects/` 目录下这些文件变了：

```
文件              源(刚编译)     目标(旧备份)     判定
─────────────────────────────────────────────────────
main.obj          size≠旧       → 🔴 全量传（其实只有几KB变了）
03-...FOC.hex     size≠旧       → 🔴 传差异块
03-...FOC.map     mtime≠旧      → 🟡 delta传差异部分
main.crf          size同,mtime同 → ✅ 跳过！
port.crf          size同,mtime同 → ✅ 跳过！
```

**结果：只传了 3 个变了的文件，2 个没变的直接跳过。** 这就是为什么第二次同步 `sent 0 bytes`。

### 2.3 相关参数

| 参数 | 行为 |
|------|------|
| 默认 | 大小或 mtime 变了就传（"quick check"） |
| `-c` (`--checksum`) | 大小相同的文件再算 checksum 确认（慢但精确） |
| `-I` (`--ignore-times`) | 不管大小和时间，**全部文件都传** |
| `--size-only` | 只看大小，忽略时间 |

---

## 三、Delta 算法：决定了"怎么传"

一旦 oc-rsync 判定一个文件需要传输，它**不会传整个文件**，而是用 **rsync 算法**：

```
源 (新 main.hex):    目标 (旧 main.hex):
┌──────────────┐    ┌──────────────┐
│:020000020000FC│    │:020000020000FC│ ← 块1：相同，跳过
│:10000000...   │    │:10000000...   │ ← 块2：相同，跳过
│:10001000... ✨ │    │:10001000... 旧│ ← 块3：不同！只传这块
│:10002000...   │    │:10002000...   │ ← 块4：相同，跳过
│:00000001FF    │    │:00000001FF    │ ← 块5：相同，跳过
└──────────────┘    └──────────────┘

实际传输量: 只需传第3块的数据 (几十字节)
而不是整个文件 (23KB)
```

这就是 `speedup 2.20` 的含义——比传整个文件快了 2.2 倍。

---

## 四、如何实现"自动同步"？

oc-rsync 是手动工具，但可以配合**文件监控工具**实现自动触发。

### 4.1 方案一：watchexec（Rust！推荐）

```bash
# 安装（Windows/Mac/Linux 通用）
cargo install watchexec-cli

# 监控 Objects/ 目录，有变化就同步
watchexec -w Objects "oc-rsync -av Objects\ D:\backup\"

# 或者监控整个项目，编译完自动同步
watchexec -w Objects -e hex "oc-rsync -av --delete Objects\ D:\backup\"
```

| 参数 | 含义 |
|------|------|
| `-w` | 监控哪个目录 |
| `-e` | 只监控特定后缀文件 |
| `-r` | 命令还在跑就重启（适合服务器） |
| `--debounce 2000` | 变化后等 2 秒再触发（防抖） |

### 4.2 方案二：cargo-watch（Rust 项目专用）

```bash
cargo install cargo-watch

# Rust 项目自动编译
cargo watch -x check
cargo watch -x test
cargo watch -x run

# 不适用我们的 Keil 项目（它只认 Cargo.toml）
```

### 4.3 方案三：加到 VS Code Task（最省事）

直接在 `tasks.json` 的编译任务后面加一步同步：

```json
{
    "label": "🔨 Build + Sync",
    "dependsOn": ["uv4-rebuild", "sync-hex"],
    "dependsOrder": "sequence"
},
{
    "label": "sync-hex",
    "hide": true,
    "type": "shell",
    "command": "tools\\oc-rsync\\oc-rsync.exe",
    "args": ["-av", "--delete", "Objects\\", "D:\\firmware-backup\\"],
    "options": { "cwd": "${workspaceFolder}" }
}
```

**效果：Ctrl+Shift+B 一键编译 + 同步！**

### 4.4 方案四：inotifywait / fswatch（Linux/Mac）

```bash
# Linux
while inotifywait -r -e modify,create,delete Objects/; do
    oc-rsync -av --delete Objects/ /mnt/backup/
done

# Mac
fswatch -o Objects/ | xargs -n1 -I{} oc-rsync -av --delete Objects/ /backup/
```

### 4.5 方案五：系统定时任务（最简单但不实时）

```bash
# Windows 任务计划程序 / Linux cron
# 每 5 分钟同步一次
*/5 * * * * oc-rsync -av --delete /source/ /dest/
```

---

## 五、我们项目的实践建议

| 场景 | 推荐方案 |
|------|----------|
| 编译完自动备份 HEX | VS Code Task 组合（一键搞定） |
| 持续备份到 U 盘/NAS | watchexec 监控 Objects/ |
| 定期冷备份 | Windows 任务计划 / cron |
| 开发中实时同步代码 | watchexec -w Sources |

---

## 六、总结

```
┌─────────────────────────────────────────────────┐
│           oc-rsync 同步流程全景                   │
├─────────────────────────────────────────────────┤
│  触发：手动 或 watchexec/VS Code Task/定时任务    │
│    ↓                                            │
│  检测：对比 size → mtime → (可选 checksum)       │
│    ↓                                            │
│  传输：delta 算法，只传变化的字节块               │
│    ↓                                            │
│  完成：目标 = 源的精确镜像                       │
└─────────────────────────────────────────────────┘

核心公式：
  检测：size + mtime（快，默认）
  传输：rolling checksum delta（只传差异）
  触发：手动跑，或者用 watchexec 盯着
```

> 💡 oc-rsync **只能手动同步**，但它可以和 watchexec（也是 Rust 写的！）配合实现自动监控+触发。简单说：oc-rsync 是快递员，watchexec 是门铃——门铃响了，快递员才过来取件。

---

## 七、实用技巧（综合阮一峰教程）

### 7.1 ⚠️ 斜杠陷阱：最容易踩的坑

源路径末尾有没有斜杠，**天差地别**：

```bash
# ❌ 复制整个目录 → 目标下出现 Objects/Objects/
oc-rsync -av Objects D:\backup
# 结果: D:\backup\Objects\main.obj

# ✅ 复制目录内容 → 这才是你要的
oc-rsync -av Objects/ D:\backup
# 结果: D:\backup\main.obj
```

```
Objects     →  "把 Objects 这个文件夹本身复制过去"
Objects/    →  "把 Objects 里面的东西复制过去"
```

> 🔥 这个坑阮一峰专门强调，几乎每个新手都踩过！

### 7.2 排除不需要的文件

```bash
# 排除特定文件类型
oc-rsync -av --exclude='*.tmp' --exclude='*.log' source/ dest/

# 排除整个目录
oc-rsync -av --exclude='.git/' --exclude='node_modules/' source/ dest/

# 批量排除（用文件列表）
# exclude-list.txt 内容：
# *.o
# *.obj
# *.crf
# .git/
oc-rsync -av --exclude-from='exclude-list.txt' source/ dest/

# 只同步特定类型（先排除所有，再包含）
oc-rsync -av --include='*.hex' --include='*.map' --exclude='*' source/ dest/
```

### 7.3 断点续传

大文件传到一半断了？不用重头来：

```bash
# -P = --partial（保留半截文件）+ --progress（显示进度）
oc-rsync -avP large_file.bin user@server:/backup/

# 如果断了，再跑一次同样的命令 → 自动接着传！
```

### 7.4 限制带宽（不抢网速）

```bash
# 限速 100KB/s
oc-rsync -av --bwlimit=100 source/ dest/

# 不限速
oc-rsync -av --bwlimit=0 source/ dest/
```

### 7.5 增量版本备份（类似 Time Machine）

利用 `--link-dest` + 硬链接，每次只存变化，但看起来像完整备份：

```bash
#!/bin/bash
# 每次运行 → 生成一个带时间戳的"完整"备份
# 但没变的文件都是硬链接，不占额外空间！

BACKUP_DIR="/backup/firmware"
DATETIME=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_PATH="${BACKUP_DIR}/${DATETIME}"
LATEST="${BACKUP_DIR}/latest"

mkdir -p "${BACKUP_DIR}"

oc-rsync -av --delete \
  Objects/ \
  --link-dest "${LATEST}" \
  "${BACKUP_PATH}"

rm -f "${LATEST}"
ln -s "${BACKUP_PATH}" "${LATEST}"    # Windows 用 mklink /D
```

**效果**：每次编译完跑一次，就能保留每次编译的 HEX 快照，但只占增量空间。

### 7.6 远程同步

```bash
# 推送到远程服务器（SSH）
oc-rsync -avz Objects/ user@192.168.1.100:/firmware/

# 从远程拉取
oc-rsync -avz user@192.168.1.100:/logs/ ./logs/

# 用非标准 SSH 端口
oc-rsync -avz -e 'ssh -p 2222' source/ user@host:/dest/

# 用 rsync 协议（对方跑着 rsync daemon）
oc-rsync -av source/ rsync://192.168.1.100/module/dest/
```

---

## 八、完整参数速查表

| 参数 | 含义 | 常用度 |
|------|------|--------|
| `-a` | 归档模式（= `-rlptgoD`），保留权限时间等 | ⭐⭐⭐⭐⭐ |
| `-v` | 显示详情（`-vv` 更详细） | ⭐⭐⭐⭐⭐ |
| `-n` | 干跑，只看不执行 | ⭐⭐⭐⭐ |
| `--delete` | 删目标多余文件，变成镜像 | ⭐⭐⭐⭐ |
| `-z` | 传输时压缩 | ⭐⭐⭐⭐ |
| `-P` | `--progress` + `--partial`（进度+断点续传） | ⭐⭐⭐⭐ |
| `-r` | 递归子目录（`-a` 已包含） | ⭐⭐⭐ |
| `-c` | checksum 比较（慢但精确） | ⭐⭐⭐ |
| `-u` | 跳过目标更新的文件 | ⭐⭐⭐ |
| `-h` | 人类可读的大小格式 | ⭐⭐⭐ |
| `-i` | 显示每个文件的变更详情 | ⭐⭐ |
| `--exclude` | 排除文件/目录 | ⭐⭐⭐⭐ |
| `--exclude-from` | 从文件读取排除列表 | ⭐⭐⭐ |
| `--include` | 包含文件（配合 `--exclude`） | ⭐⭐⭐ |
| `--bwlimit` | 带宽限制 KB/s | ⭐⭐ |
| `--max-size` | 最大文件限制 | ⭐⭐ |
| `--min-size` | 最小文件限制 | ⭐⭐ |
| `--partial` | 保留中断的半截文件 | ⭐⭐ |
| `--append` | 接着上次中断处继续 | ⭐⭐ |
| `--link-dest` | 增量备份基准目录 | ⭐⭐ |
| `--remove-source-files` | 传完删源文件 | ⭐ |

---

## 九、常见问题

### Q1: 同步时源文件正在被写入怎么办？

rsync 不锁定文件。如果 UV4 正在写 `.hex`，rsync 可能读到一半的文件。
- 解决：用 `watchexec --debounce 2000`，等 2 秒文件稳定了再触发

### Q2: 如何验证两个目录完全一致？

```bash
# 干跑看有没有差异
oc-rsync -avnc --delete source/ dest/
# -c 用 checksum 确保精确
# -n 只看不执行
# 如果输出为空 → 完全一致！
```

### Q3: 同步会不会覆盖我手动改的文件？

默认会覆盖（源优先）。不想覆盖用 `-u`：
```bash
oc-rsync -avu source/ dest/   # 跳过目标中更新的文件
```

### Q4: Windows 上路径空格怎么办？

```bash
# 用引号包住
oc-rsync -av "D:\My Project\Objects\" "E:\Backup\My Project\"
```
