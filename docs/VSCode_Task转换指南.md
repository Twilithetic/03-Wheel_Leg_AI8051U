# 长命令 → VS Code Task 转换指南

> 把一条蛋疼的长命令拆成清爽的 tasks.json，三步搞定！

---

## 第一步：判断命令有没有 shell 操作符

看看你的命令里有没有这些东西：

| 操作符 | 含义 | 能直接拆吗？ |
|--------|------|-------------|
| `&&` | 前一个成功才执行后一个 | ❌ 不行，要 shell 解释 |
| `\|\|` | 前一个失败才执行后一个 | ❌ 不行 |
| `\|` | 管道 | ❌ 不行 |
| `>` `>>` | 重定向 | ❌ 不行 |
| **没有以上** | 纯命令 + 参数 | ✅ 直接拆！ |

### ✅ 情况 A：纯命令（直接拆 args）

```bash
# 原命令
gcc -Wall -O2 main.c -o main.exe
```

直接变：
```json
{
    "command": "gcc",
    "args": ["-Wall", "-O2", "main.c", "-o", "main.exe"]
}
```

> 规则：`command` 放程序名，每个空格分隔的东西拆成 `args` 数组的一个元素。

### ❌ 情况 B：有 shell 操作符（用组合任务）

```bash
# 原命令（有 && 不能直接拆！）
UV4.exe -b project.uvproj -j0 -t Target -l build.log && type build.log
```

---

## 第二步：拆成子任务

把 `&&` 前后各自独立的任务拎出来：

```
UV4.exe -b project.uvproj -j0 -t Target -l build.log    ← 子任务1：编译
&&
type build.log                                            ← 子任务2：显示日志
```

---

## 第三步：写成 tasks.json

```json
{
    "version": "2.0.0",
    "tasks": [
        // ═══════════ 子任务1：编译 ═══════════
        {
            "label": "我的编译",
            "hide": true,                          // 隐藏，不在任务列表里出现
            "type": "shell",
            "command": "C:\\Keil_v5\\UV4\\UV4.exe",
            "args": [
                "-b",
                "03-March_Wheel_leg_FOC.uvproj",
                "-j0",
                "-t", "03-March_Wheel_leg_FOC",
                "-l", "Objects\\build.log"
            ],
            "options": {
                "cwd": "${workspaceFolder}"        // 工作目录 = 项目根
            },
            "presentation": {
                "reveal": "always",
                "clear": true,                     // 每次清屏
                "showReuseMessage": false          // 不显示 "Terminal will be reused"
            }
        },

        // ═══════════ 子任务2：显示日志 ═══════════
        {
            "label": "显示日志",
            "hide": true,
            "type": "shell",
            "command": "type",
            "args": ["Objects\\build.log"],
            "options": {
                "cwd": "${workspaceFolder}"
            },
            "presentation": {
                "reveal": "always",
                "showReuseMessage": false
            }
        },

        // ═══════════ 组合任务：串联 ═══════════
        {
            "label": "🔨 Build",
            "dependsOn": ["我的编译", "显示日志"],   // 依赖两个子任务
            "dependsOrder": "sequence",              // 按顺序执行！
            "group": { "kind": "build", "isDefault": true },
            "presentation": { "close": false }       // 终端不自动关
        }
    ]
}
```

---

## 核心规则速查

```
┌──────────────────────────────────────────────┐
│  有 && / || / | / > ？                       │
│    ├─ 是 → 拆成子任务 + compound task        │
│    └─ 否 → 直接 command + args 搞定          │
├──────────────────────────────────────────────┤
│  每个子任务                                  │
│    command = 程序名（一个词）                 │
│    args    = 参数（每个空格分开）             │
│    hide    = true（不碍眼）                   │
├──────────────────────────────────────────────┤
│  组合任务                                    │
│    dependsOn    = ["子任务1", "子任务2"]      │
│    dependsOrder = "sequence"（顺序执行）      │
│    group        = 快捷键绑定                  │
└──────────────────────────────────────────────┘
```

### args 拆分示例

| 原始命令片段 | 拆法 |
|-------------|------|
| `-l Objects\\build.log` | `"-l", "Objects\\build.log"` |
| `-t "Target 1"` | `"-t", "Target 1"` → VS Code 自动加引号 |
| `-Wall` | `"-Wall"` |
| `&&` | **不能**放 args！拆成子任务 |

---

## 常用模板

### 模板：单命令（无 shell 操作符）

```json
{
    "label": "任务名",
    "type": "shell",
    "command": "你的程序",
    "args": ["参数1", "参数2", "参数3"],
    "options": { "cwd": "${workspaceFolder}" },
    "group": { "kind": "build", "isDefault": true }
}
```

### 模板：两段命令（有 &&）

```json
// 子任务1
{ "label": "step1", "hide": true, "command": "程序A", "args": [...] },
// 子任务2
{ "label": "step2", "hide": true, "command": "程序B", "args": [...] },
// 组合
{ "label": "🎯 最终任务", "dependsOn": ["step1", "step2"], "dependsOrder": "sequence" }
```

---

## 调试技巧

1. **先手动跑子任务**：复制子任务的 command + args，在终端里跑一遍确认能过
2. **`dependsOrder` 别忘**：默认是 `"parallel"`（并行），需要顺序执行必须写 `"sequence"`
3. **路径用 `${workspaceFolder}`**：不要写死绝对路径，换电脑就炸了
4. **backslash 要转义**：JSON 里 `\\` = 一个 `\`

---

> 💡 记住一句话：**`&&` 是 shell 的事，不是程序的事。碰到它就把命令"腰斩"，用 compound task 串联。**
