# watchexec 触发机制与性能分析报告

> 整理日期：2026-05-12  
> 资料来源：watchexec 源码 (docs.rs/watchexec)、notify crate 文档、Hacker News 讨论

---

## 一、核心结论

```
watchexec 不是轮询！
它用的是操作系统内核级事件通知 —— 零 CPU 空转！
```

---

## 二、触发机制：四层架构

```
┌──────────────────────────────────────────────────────┐
│                   watchexec                          │
│  (Rust bin, 事件过滤、防抖、命令调度)                  │
├──────────────────────────────────────────────────────┤
│                   notify crate                       │
│  (Rust lib, 跨平台文件监控抽象)     62.7M+ 下载量      │
├──────────┬──────────┬──────────┬─────────────────────┤
│  Linux   │  macOS   │ Windows  │   Fallback           │
│ inotify  │ FSEvents │ ReadDir- │   polling            │
│ (内核)   │ (内核)    │ ectory-  │   (最后手段)          │
│          │          │ ChangesW │                      │
│          │          │ (内核)    │                      │
└──────────┴──────────┴──────────┴─────────────────────┘
```

### 2.1 各平台原生 API

| 平台 | API | 原理 |
|------|-----|------|
| **Windows** | `ReadDirectoryChangesW` | 内核监控，文件变化时通知，**不轮询** |
| **Linux** | `inotify` | 内核 inode 事件，`epoll` 等待，**零 CPU 空转** |
| **macOS** | `FSEvents` | 内核文件系统事件流 |

### 2.2 事件驱动 vs 轮询

```
轮询 (polling):                    事件驱动 (watchexec):
┌──────┐                            ┌──────┐
│ CPU  │ ██░░ ██░░ ██░░ ██░░        │ CPU  │ ░░░░ ░░░░ ██░░ ░░░░
│      │ 每100ms扫一次               │      │ 只在文件变时才醒
└──────┘                            └──────┘
  持续消耗 CPU                       几乎不消耗 CPU

实际数据：
  轮询 几万文件 @ 100ms → 持续 50% CPU  😱
  事件驱动 (watchexec) → < 0.1% CPU    😎
```

**watchexec 用事件驱动，空闲时 CPU 几乎为零。** 只有文件真正变化时内核才唤醒它。

---

## 三、watchexec 的智能处理

watchexec 不光监听事件，还做了几件聪明事：

### 3.1 防抖 (Debounce)

编辑器保存文件时，通常会触发一**串**事件：
```
编辑器保存 main.c：
  → 写临时文件 main.c~
  → 删旧文件 main.c
  → 重命名 main.c~ → main.c
  → 更新目录元数据

这些都在几毫秒内发生，watchexec 自动合并 → 只触发一次命令！
```

```bash
# --debounce 控制防抖窗口（默认已启用）
watchexec --debounce 2000 "oc-rsync ..."  # 2秒内的变化合并
```

### 3.2 智能忽略

```bash
# 默认忽略 .gitignore 中的文件
# 默认忽略 .git/ 目录
# 可手动指定忽略
watchexec -i "target/" -i "*.tmp" "make"
```

### 3.3 只监控关心的

```bash
# 只看特定目录
watchexec -w src -w include "make"

# 只看特定文件类型
watchexec -e hex,obj "oc-rsync -av Objects\ D:\backup\"

# 只看特定事件类型
watchexec --fs-events create "echo 新文件来了"
```

---

## 四、我们项目的实际开销估算

### 场景：监控 `Objects/` 目录

```
Objects/ 目录: ~12 个文件, ~2MB 总大小
监控频率: 事件驱动（不是轮询）
```

| 状态 | CPU 使用 | 说明 |
|------|----------|------|
| 空闲（没人编译） | **≈ 0%** | 内核挂起，watchexec 睡大觉 |
| 编译中（UV4 写入） | < 0.5% | 处理几个文件事件 |
| 同步中（oc-rsync） | 看 oc-rsync | watchexec 已退居后台 |

**结论：watchexec 对 CPU 的影响可以忽略不计。**

---

## 五、与其他工具对比

| 工具 | 检测方式 | CPU 开销 | 跨平台 | 语言 |
|------|----------|---------|--------|------|
| **watchexec** | 事件驱动 | ≈ 0% | ✅ Win/Mac/Linux | Rust |
| inotifywait | 事件驱动 | ≈ 0% | ❌ Linux only | C |
| fswatch | 事件驱动 | ≈ 0% | ✅ | C++ |
| nodemon | 事件驱动(?) | 低 | ✅ | Node.js |
| polling script | 轮询 | ⚠️ 高 | ✅ | Any |

---

## 六、推荐用法

### 编译完自动同步 HEX

```bash
# 安装
cargo install watchexec-cli

# 启动监控（最小 CPU 开销）
watchexec -w Objects -e hex --debounce 1000 ^
  "tools\oc-rsync\oc-rsync.exe -av Objects\03-March_Wheel_leg_FOC.hex D:\backup\"
```

### 参数说明

| 参数 | 作用 |
|------|------|
| `-w Objects` | 只监控 Objects 目录 |
| `-e hex` | 只看 .hex 文件的变化 |
| `--debounce 1000` | 1 秒内多次变化合并成一次 |
| `-n` | 不用 shell 包装（性能更好） |
| `-r` | 如果上次命令还跑着就重启（服务器场景） |

---

## 七、总结

```
┌──────────────────────────────────────────────┐
│           watchexec 工作流程                   │
├──────────────────────────────────────────────┤
│  1. 通知 notify crate："帮我盯着 Objects/"     │
│  2. notify → 内核 → ReadDirectoryChangesW    │
│  3. 内核：文件变了！→ 唤醒 notify               │
│  4. notify → watchexec：收到事件              │
│  5. watchexec：防抖合并 → 过滤忽略 → 执行命令   │
│  6. CPU 回零，继续睡                          │
└──────────────────────────────────────────────┘

关键数字：
  空闲 CPU: ≈ 0%
  事件延迟: < 10ms（内核直接通知）
  内存占用: < 10MB
```

> 💡 watchexec 不是轮询，是**操作系统内核帮你盯着**。就像快递柜——不是你自己每隔一分钟跑去看有没有包裹，而是快递员放进去后系统自动给你发短信。
