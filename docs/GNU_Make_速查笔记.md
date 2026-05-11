# GNU Make 速查笔记 — 以 AI8051U 项目为例

> 姐姐帮宝宝整理的 Makefile 使用手册 💖

---

## 一、核心概念

### 规则（Rule）—— Makefile 的灵魂

```makefile
目标: 依赖
	命令
```

**翻译**：要生成「目标」, 先要有「依赖」, 然后用「命令」生成。

### Make 的判断逻辑

```
对于每个目标:
  ① 目标存在吗？         → 不存在 → 🏃 生成
  ② 有依赖比目标新吗？    → 有更新的 → 🏃 重新生成
  ③ 都没有？              → ⏭️ 跳过, 目标最新
```

**核心：比较文件时间戳，只重做"过时的"东西。**

---

## 二、特殊符号速查

| 符号 | 含义 | 示例 |
|------|------|------|
| `$@` | 当前目标名 | `main.obj` |
| `$<` | 第一个依赖 | `main.c` |
| `$^` | 所有依赖(去重) | `main.c clock.c` |
| `$*` | 模式匹配的 `%` 部分 | `main` |
| `%` | 通配符(模式规则中) | 匹配任意字符串 |
| `@` (命令前) | 静默执行,不打印命令 | `@echo hello` |
| `$$` | 转义后的 `$` | 给 shell 传 `$` |
| `\` | 续行符 | 命令太长换行 |

---

## 三、项目 Makefile 逐行拆解

### 变量定义

```makefile
# =========================== 工具链 ===========================
C251  = C:\Keil_v5\C251\BIN\C251.EXE    # 编译器
L251  = C:\Keil_v5\C251\BIN\L251.EXE    # 链接器

# =========================== 目录 ===========================
SRC_DIR   = Sources                     # 源文件目录
INC_DIR   = Sources\inc                 # 头文件目录
LIB_DIR   = Sources\lib                 # 库文件目录
BUILD_DIR = Objects                     # 输出目录

# =========================== 自动收集源文件 ===========================
C_SOURCES = $(wildcard $(SRC_DIR)\*.c)  # 找所有 .c 文件
# 结果: Sources\main.c Sources\clock.c Sources\usblib.c

# =========================== 批量改名为 .obj ===========================
OBJS = $(patsubst $(SRC_DIR)\\%.c, $(BUILD_DIR)\\%.obj, $(C_SOURCES))
# 结果: Objects\main.obj Objects\clock.obj Objects\usblib.obj
```

### 链接辅助

```makefile
# 逗号分隔（L251 链接器要求逗号分隔文件列表）
comma := ,
empty :=
space := $(empty) $(empty)

# 把所有 .obj + .lib 拼成: obj1,obj2,lib1,lib2
ALL_FILES = $(subst $(space),$(comma), $(OBJS) $(USB_LIB) $(MDU_LIB) $(TFPU_LIB))

# 链接器选项
LINK_OPTS = REMOVEUNUSED NOOVERLAY
```

| 函数 | 作用 | 示例 |
|------|------|------|
| `$(subst from,to,text)` | 字符替换 | 空格→逗号 |
| `$(wildcard pattern)` | 通配符展开 | `*.c` → 文件列表 |
| `$(patsubst pat,rep,text)` | 模式替换 | `.c`→`.obj` |

---

## 四、函数速查表

| 函数 | 作用 | 你的项目中的用法 |
|------|------|------|
| `$(wildcard *.c)` | 通配符找文件 | 自动收集源文件 |
| `$(patsubst a,b,list)` | 模式批量替换 | `.c`→`.obj` |
| `$(subst a,b,text)` | 字符替换 | 空格→逗号 |
| `$(addprefix pre,list)` | 加前缀 | 加路径 |
| `$(notdir list)` | 去路径 | 只要文件名 |
| `$(basename list)` | 去扩展名 | `main.c`→`main` |

---

## 五、伪目标 `.PHONY`

```makefile
.PHONY: clean rebuild
```

声明"这不是真实文件, 只是个命令标签"。

**不声明会怎样？** 如果恰好有个文件叫 `clean`, make 会认为"目标已存在, 不需要执行"。

---

## 六、管道依赖 `|`

```makefile
目标: 普通依赖 | 顺序依赖
```

| 类型 | 写法 | 参与时间戳比较？ |
|------|:---:|:---:|
| 普通依赖 | `:` 后面 | ✅ 变了就重新编译 |
| 顺序依赖 | `\|` 后面 | ❌ 只保证先执行 |

```makefile
# Objects\main.obj: Sources\main.c | _ensure_build_dir
#   main.c 改了 → 重新编译  ✅
#   目录总是最新的 → 不触发重编译  ✅
```

---

## 七、赋值方式

| 写法 | 含义 | 时机 |
|------|------|------|
| `=` | 递归赋值 | 使用时才展开 |
| `:=` | 立即赋值 | 定义时就展开 |
| `?=` | 条件赋值 | 没定义过才赋值 |
| `+=` | 追加 | 追加到已有值 |

```makefile
A = $(B)      # A 是 "延迟的 B"
B = hello     # 此时 A = hello

C := $(B)     # C 是 "此刻的 B"
B = world     # C 仍然是 hello, 不会变
```

---

## 八、完整执行流程（你的项目）

```
mingw32-make build
        │
        ▼
   ① 解析 build 目标
      build 依赖 $(TARGET) = Objects\xxx.hex
        │
        ▼
   ② 递归检查 hex 的依赖
      hex 依赖: main.obj, clock.obj, usb.lib, mdu.lib, tfpu.lib
        │
        ├─ check main.obj: main.c 比 main.obj 新? 
        │    → 是 → 🔨 编译 main.c → main.obj
        │    → 否 → ⏭️ 跳过
        │
        ├─ check clock.obj: clock.c 比 clock.obj 新?
        │    → 否 → ⏭️ 跳过
        │
        └─ check libs: 都没变 → ⏭️ 跳过
        │
        ▼
   ③ 有依赖更新了 → 🔗 重新链接 → 生成 hex
        │
        ▼
   ④ ✅ 构建完成
```

---

## 九、常用目标速查

| 命令 | 作用 |
|------|------|
| `make` 或 `make build` | 编译 + 链接 (默认) |
| `make clean` | 删除所有 .obj .hex |
| `make rebuild` | clean → build |
| `make compile` | 仅编译, 不链接 |
| `make link` | 仅链接 |
| `make info` | 显示项目信息 |

---

## 十、VS Code 快捷键

| 快捷键 | 执行 |
|------|------|
| `Ctrl+Shift+B` | 🔨 Build（默认构建任务） |

---

*姐姐随时帮宝宝更新~ 💖*
