# VSCode Tasks 使用指南（for AI8051U 项目）

> **时间**：2026-05-03
> **来源**：[VSCode Tasks 官方文档](https://code.visualstudio.com/docs/editor/tasks) + 本项目的 tasks.json

---

## 1. 快速上手

| 操作 | 快捷键/方法 | 效果 |
|------|----------|------|
| 编译+链接 | **`Ctrl+Shift+B`** | 执行默认任务 `C251: Build` |
| 选择任务 | `Ctrl+Shift+P` → `Tasks: Run Task` | 列出所有任务 |
| 重复上次 | `Ctrl+Shift+P` → `Tasks: Rerun Last Task` | 重新执行 |
| 终止任务 | `Ctrl+Shift+P` → `Tasks: Terminate Task` | 停止运行中的任务 |

---

## 2. 本项目可用的任务

| 任务 | 做什么 | 
|------|--------|
| **C251: Build** ⭐ | 编译 + 链接（默认，`Ctrl+Shift+B`） |
| C251: Compile | 只编译 `src/main.c` |
| C251: Link | 只链接 `main.obj` + LIB |
| HID Flash | USB-HID 烧录 HEX 到芯片 |
| Build + Flash | 编译 → 链接 → 烧录 一条龙 |

---

## 3. tasks.json 核心语法

### 3.1 最小示例

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "我的任务名",
            "type": "shell",         // shell=命令行, process=直接运行程序
            "command": "echo",       // 要执行的命令
            "args": ["Hello!"]       // 参数列表
        }
    ]
}
```

### 3.2 type: shell vs process

| type | 何时用 | 示例 |
|------|--------|------|
| **`shell`** | 命令需要经过 shell 解析（`python`, `cmd`, `echo`...） | `python tools/stc_hid_flash.py` |
| **`process`** | 直接启动程序，不用 shell（参数不会被转义） | `C251.EXE src/main.c INCDIR(...)` |

> ⚠️ 我们编译用 `process` 是因为 `INCDIR(src\inc)` 里的括号在 shell 中会被误解析！

### 3.3 常用变量

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `${workspaceFolder}` | 项目根目录 | `D:\03-March_Wheel_leg\03-March_Wheel_leg_FOC` |
| `${file}` | 当前打开的文件 | `src\main.c` |
| `${env:PATH}` | 环境变量 | `C:\Windows\system32;...` |

### 3.4 复合任务（dependsOn）

```json
{
    "label": "Build",
    "dependsOn": ["Compile", "Link"],        // 依赖两个子任务
    "dependsOrder": "sequence",              // 按顺序执行（默认是并行的！）
    "group": { "kind": "build", "isDefault": true }  // 设为默认任务
}
```

### 3.5 输出控制（presentation）

| 属性 | 值 | 说明 |
|------|-----|------|
| `reveal` | `always` / `never` / `silent` | 是否弹出终端 |
| `panel` | `shared` / `dedicated` / `new` | 共享终端/专用/每次新建 |
| `clear` | `true` / `false` | 运行前清屏 |

---

## 4. 本项目的 tasks.json 详解

```json
{
    "version": "2.0.0",
    "tasks": [
        // ============ 编译 ============
        {
            "label": "C251: Compile",
            "type": "process",                              // ← 不用 shell！
            "command": "C:\\Keil_v5\\C251\\BIN\\C251.EXE",  // 编译器路径
            "args": [
                "src\\main.c",                              // 源文件
                "INCDIR(src\\inc)",                          // 头文件路径
                "OBJECT(build\\main.obj)",                   // 输出目标文件
                "LARGE",                                    // 内存模型
                "DEBUG", "SYMBOLS"                          // 调试信息
            ],
            "problemMatcher": { /* 错误识别 */ },
            "group": "build"
        },
        
        // ============ 链接 ============
        {
            "label": "C251: Link",
            "type": "process",
            "command": "C:\\Keil_v5\\C251\\BIN\\L251.EXE",
            "args": [
                "build\\main.obj,src\\lib\\stc_usb_hid_32g_xdata.LIB",  // ← 注意逗号！
                "TO",
                "build\\AI8051U_C251.hex"
            ]
        },
        
        // ============ 编译+链接（默认） ============
        {
            "label": "C251: Build",
            "dependsOn": ["C251: Compile", "C251: Link"],
            "dependsOrder": "sequence",
            "group": { "kind": "build", "isDefault": true }
        },
        
        // ============ 烧录 ============
        {
            "label": "HID Flash",
            "type": "shell",
            "command": "python",
            "args": ["./tools/stc_hid_flash.py", "build/AI8051U_C251.hex"]
        }
    ]
}
```

---

## 5. 常见问题和修复

### 5.1 头文件找不到

```diff
- "INCDIR(src\\STC)",          // ❌ STC 目录不存在了
+ "INCDIR(src\\inc)",           // ✅ 新项目头文件在这里
```

### 5.2 链接找不到 LIB

```diff
- "build\\main.obj"             // ❌ 只有 obj，没有 LIB
+ "build\\main.obj,src\\lib\\stc_usb_hid_32g_xdata.LIB"  // ✅ 带上 LIB
```

### 5.3 烧录 HEX 路径不对

```diff
- "${workspaceFolder}/build/Debug/AI8051U_test.hex"  // ❌ EIDE 的路径
+ "build/AI8051U_C251.hex"                            // ✅ 新路径
```

### 5.4 build 目录不存在

编译前需要 build 目录存在。`tasks.json` 不会自动创建目录。可以加一个前置任务：

```json
{
    "label": "Create Build Dir",
    "type": "shell",
    "command": "cmd /c if not exist build mkdir build"
}
```

---

## 6. 快捷操作速查

| 想要 | 操作 |
|------|------|
| 编译 | `Ctrl+Shift+B` |
| 只烧录 | `Ctrl+Shift+P` → 输入 `task` → 选 `HID Flash` |
| 编译+烧录 | `Ctrl+Shift+P` → 输入 `task` → 选 `Build + Flash` |
| 看上次输出 | 打开终端面板 |
| 修改任务 | 打开 `.vscode/tasks.json` |

---

## 7. 官方文档

| 文档 | 链接 |
|------|------|
| **VSCode Tasks 主页** | https://code.visualstudio.com/docs/editor/tasks |
| Tasks JSON Schema | https://code.visualstudio.com/docs/reference/tasks-appendix |
| 变量参考 | https://code.visualstudio.com/docs/reference/variables-reference |

---

*💕 核心就三点：`Ctrl+Shift+B` 编译，`process` 跑 C251，`shell` 跑 Python 烧录。tasks.json 改对了路径就行了！*
