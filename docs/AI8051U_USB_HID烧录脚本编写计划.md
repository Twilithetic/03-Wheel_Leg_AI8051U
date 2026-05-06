# AI8051U USB-HID 烧录脚本编写计划

> 📅 日期：2026年5月6日  
> 📚 来源：GitHub robinkrens/stc32_hid_program.py、项目已有调研、STC 芯片手册

---

## 一、背景

### 现状
- `tools\AiCube-ISP-v6.96V-plus.exe` 是纯 GUI 工具，**不支持命令行参数**
- 项目曾有一个 `stc_hid_flash.py`（改编自 GitHub robinkrens gist），但**静默失败**
- 需要编译后在 CLI 中自动烧录，实现「编译 → 烧录」一键完成

### 目标
编写一个 **Rust cargo-script**：`tools/flash.rs`，通过 USB-HID 协议直接烧录 AI8051U 芯片。

---

## 二、协议分析

### 2.1 已知协议（来自 robinkrens/stc32_hid_program.py）

```
USB VID/PID: 0x34BF / 0x1001

数据包格式:
┌─────────┬──────────┬─────────┬──────────┬──────────┬──────┐
│ 0x46,0xB9│ 0x6A(Host)│ 长度(2B) │ 命令数据 │ 校验和(2B)│ 0x16 │
│  Start   │ Direction │  BigEnd│ Payload  │  BigEnd  │ End  │
└─────────┴──────────┴─────────┴──────────┴──────────┴──────┘

命令列表:
  0x00           — 初始化握手
  0x01 + 7bytes  — 查询芯片信息
  0x05 + 0x5AA5  — 解锁 ISP
  0x03 + 0x5AA5  — 擦除 Flash
  0x32 + addr(2B) + 0x5AA5 + chunk(128B) — 首包写入
  0x12 + addr(2B) + 0x5AA5 + chunk(128B) — 后续写入
  0xFF           — 复位芯片
```

### 2.2 AI8051U 差异（待验证）

| 项目 | STC32F12K54 | AI8051U（待确认） |
|------|------------|-------------------|
| VID/PID | 0x34BF/0x1001 | 可能是 0x34BF/0x1001 或不同 |
| Flash 页大小 | 128B (0x80) | 待确认 |
| 芯片 ID 响应 | 特定格式 | 需要实际抓包 |
| 命令兼容性 | 基准 | 需逐个验证 |

### 2.3 AI8051U ISP 模式进入

根据手册（2.3.3 节），芯片上电时：
- 如果 P3.2 = 0（低电平）→ 进入 USB-HID ISP 模式
- 如果正常运行中收到 USB-HID 特殊命令 → IAP_CONTR = 0x60 软复位到 ISP 区

---

## 三、技术方案

### 3.1 语言选型

| 方案 | 优点 | 缺点 |
|------|------|------|
| Python + hidapi | 已有参考代码 | 需要装 Python 依赖 |
| **Rust + hidapi** | 编译为单 exe，无运行时依赖 | 需要写从零开始 |
| Rust cargo-script | 单文件，管理简单 | nightly 工具链 |

**选择 Rust cargo-script**，与项目风格一致。

### 3.2 依赖

```toml
[dependencies]
hidapi = "2"           # USB HID 通信
anyhow = "1"           # 错误处理
colored = "2"          # 彩色输出
intelhex = "???"       # HEX 文件解析（或用 serde 解析简单格式）
```

> ⚠️ Rust 生态的 intelhex crate 不够成熟。可以自己写一个简单的 Intel HEX 解析器（约 50 行）。

### 3.3 功能模块

```
flash.rs
├── parse_hex()      — 解析 Intel HEX 文件 → Vec<(addr, data)>
├── open_device()    — 打开 USB HID 设备 (VID=0x34BF, PID=0x1001)
├── send_packet()    — 构造并发送 ISP 数据包
├── recv_response()  — 接收并解析响应
├── init_isp()       — 初始化 + 握手
├── query_chip()     — 查询芯片型号/Flash 大小
├── erase_chip()     — 擦除 Flash
├── write_flash()    — 写入 HEX 数据（分 128B 块）
├── verify_flash()   — 可选：回读校验
├── reset_chip()     — 复位到用户程序
└── main()           — CLI 参数解析 + 流程编排
```

### 3.4 CLI 接口

```powershell
# 基本烧录
cargo +nightly -Zscript tools\flash.rs Objects\03-March_Wheel_leg_FOC.hex

# 指定 VID/PID（调试用）
cargo +nightly -Zscript tools\flash.rs --vid 34BF --pid 1001 firmware.hex

# 仅擦除
cargo +nightly -Zscript tools\flash.rs --erase

# 烧录 + 校验
cargo +nightly -Zscript tools\flash.rs --verify firmware.hex

# 列出连接的 STC 设备
cargo +nightly -Zscript tools\flash.rs --list
```

---

## 四、实施步骤

### 阶段 1：验证通信（最关键）

1. 安装 `hidapi` Rust crate
2. 编写设备发现代码，列出所有 VID=0x34BF 的 HID 设备
3. 如果找不到，调整 VID/PID（可能需要抓包 AI8051U 的 USB 描述符）
4. 尝试发送 `0x00` 初始化命令，检查响应
5. 发送 `0x01` 查询芯片信息，确认与 AI8051U 兼容

### 阶段 2：实现烧录流程

1. 实现 Intel HEX 解析器
2. 实现解锁 → 擦除 → 写入 → 复位 完整流程
3. 每步添加超时和重试机制
4. 添加进度条（tqdm 风格）

### 阶段 3：集成与测试

1. 修改 `builder.rs` 的 `flash` 命令，改为调用 `flash.rs`
2. 用实际硬件测试完整流程
3. 实现烧录前自动编译（`flash` 命令先调 `build`）

### 阶段 4：健壮性

1. 添加写入后回读校验
2. 处理各种错误：设备断开、写入失败、校验不通过
3. 支持多设备时让用户选择

---

## 五、风险与对策

| 风险 | 概率 | 对策 |
|------|------|------|
| AI8051U 的 VID/PID 与已知不同 | 中 | 用 USB 设备树查看器确认，或从 STC 官方驱动中获取 |
| 协议命令不兼容 | 中 | 用 Wireshark/USBpcap 抓取 AiCube-ISP 的通信包对比 |
| 当前代码用 CDC 模式，HID 不可用 | 高 | 需要切换到 HID 库（`stc_usb_hid_32g_xdata.LIB`），或保持 CDC 但用 UART 协议 |
| hidapi crate 在 Windows 上编译困难 | 低 | Windows 上 hidapi 通过 MSVC 编译，通常无问题 |

> ⚠️ **关键风险**：当前项目使用的是 **USB-CDC 库**（`stc_usb_cdc_32g_xdata.LIB`），而 USB-HID 烧录需要芯片进入 **HID ISP 模式**。CDC 模式下的 USB 设备不会被 HID API 发现。需要在烧录前确保芯片支持 HID 模式。

---

## 六、参考资源

| 资源 | 说明 |
|------|------|
| [robinkrens/stc32_hid_program.py](https://gist.github.com/robinkrens/47a98e58087623059d809175a30b0f42) | 现有 HID 烧录参考实现 |
| [grigorig/stcgal](https://github.com/grigorig/stcgal) | 开源 STC ISP 工具（UART 协议） |
| `docs/AI8051U_免断电自动下载方案.md` | 项目内的自动下载方案 |
| `docs/AI8051U_HID烧录脚本调研报告.md` | 之前的调研，分析了静默失败原因 |
| `C:\Keil_v5\C251\INC\STC\AI8051U.H` | 芯片寄存器定义 |
| `Sources/lib/stc_usb_hid_32g_xdata.LIB` | STC USB HID 库（如存在） |

---

## 七、优先级建议

| 优先级 | 任务 | 理由 |
|--------|------|------|
| 🔴 P0 | 确认 AI8051U 是否支持 HID ISP 模式 | 决定方案可行性 |
| 🔴 P0 | 确认 USB VID/PID | 发现设备 |
| 🟡 P1 | 实现基础烧录流程 | 核心功能 |
| 🟡 P1 | 实现 Intel HEX 解析 | 核心功能 |
| 🟢 P2 | 集成到 builder.rs | 一键烧录 |
| 🟢 P2 | 添加校验功能 | 可靠性 |
