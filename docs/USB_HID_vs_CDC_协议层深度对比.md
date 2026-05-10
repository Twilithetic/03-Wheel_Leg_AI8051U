# USB HID vs CDC：协议层面深度对比

> 基于 USB 2.0 Specification + STC 官方技术手册，逐层解剖

---

## 一、你问的核心问题

> "HID 和 CDC 什么区别？不都是传输字节的？协议里规定的数据包又是什么区别？"

**答案：数据包结构几乎一样，但"调度规则"天差地别！**

---

## 二、USB 四层差异对比

### 第 0 层：物理层（电信号）— 完全相同 ✅

HID 和 CDC 都走 USB 总线，D+/D- 差分信号，NRZI 编码，bit stuffing。这层没有任何区别。

### 第 1 层：包格式（Packet）— 完全相同 ✅

来自 USB 2.0 §8，所有 USB 包都是：

```
┌──────┬─────┬──────────┬───────┬────┐
│ SYNC │ PID │  数据/地址  │ CRC16 │ EOP│
│ 8bit │ 8bit│  0~1024B  │ 16bit │ 3B │
└──────┴─────┴──────────┴───────┴────┘
```

HID 和 CDC 用的**包格式一模一样**。PID 可以是 IN/OUT/DATA0/DATA1/ACK/NAK/STALL...

### 第 2 层：事务（Transaction）— 结构相同，语义不同 ⚡

来自 USB 2.0 §5.7（Interrupt）和 §5.8（Bulk），两者的事务结构都是：

```
Token包  →  Data包  →  Handshake包
(主机发)   (设备/主机发)  (接收方回)
```

但**总线仲裁规则完全不同**：

| 事务维度 | 🔴 Interrupt（HID 用） | 🔵 Bulk（CDC 用） |
|---------|----------------------|-------------------|
| 发生时机 | **按固定周期**，主机必须准时发起 | **有空才发**，总线闲时才轮得到 |
| 带宽保证 | ✅ **保证**最小带宽 | ❌ 零保证 |
| 延迟上界 | ✅ 确定：bInterval × 125μs | ❌ 无上限，可被无限推迟 |
| 优先级 | 高（仅次于等时传输） | **最低** |
| 重试机制 | 下个周期自动重试 | 有空时重试 |
| USB 规范原文 | "**Guaranteed maximum service period**"（§5.7） | "Host Controllers are **free to determine** how..."（§5.8） |

### 第 3 层：带宽与速度 — 关键区别 📊

来自 USB 2.0 §5.7.4（Table 5-7/5-8）和 §5.8.4（Table 5-9/5-10）：

#### HID（全速 12Mbps，中断传输每包 ≤64B）

| 包大小 | 每秒最大传输次数 | 有效带宽 | 帧带宽占比 |
|--------|:---:|------|:---:|
| 1B | 107 | 107 B/s | 1% |
| 8B | 71 | 568 B/s | 1% |
| 16B | 51 | 816 B/s | 2% |
| 32B | 33 | 1056 B/s | 3% |
| **64B** | **19** | **1216 B/s** | **5%** |

> **HID 烧录 AI8051U 最大速度约 1.2KB/s（全速 64B/包）**

#### CDC（全速 12Mbps，批量传输每包 ≤64B）

| 包大小 | 每秒最大传输次数 | 有效带宽 | 帧带宽占比 |
|--------|:---:|------|:---:|
| 8B | 107 | 856 B/s | 1% |
| 16B | 100 | 1600 B/s | 1% |
| 32B | 88 | 2816 B/s | 1% |
| **64B** | **71** | **4544 B/s** | **1%** |

> **表面上批量传输每帧可传更多包，但这是在"独占总线"的理想情况下**

**实际场景**：CDC 批量传输可以占满剩余带宽，如果总线上只有这一个设备，速度可以比 HID 快 3-4 倍。但如果有多个设备竞争，批量传输第一个被牺牲。

### 第 4 层：操作系统视角 — 最大区别 🖥️

| 维度 | HID | CDC |
|------|-----|-----|
| **OS 识别为** | HID 兼容设备 | COM 端口（虚拟串口） |
| **设备管理器里** | "人体学输入设备" | "端口 (COM 和 LPT)" |
| **驱动** | 系统自带，永远不需要装 | Win 需 .inf（Win10+ 内置 usbser.sys） |
| **应用程序 API** | `HidD_GetInputReport()` / `WriteFile()` | `CreateFile("COM3")` + `ReadFile/WriteFile` |
| **数据语义** | **有结构**（Report Descriptor 定义格式） | **无结构**（纯字节流，跟串口一样） |

---

## 三、数据格式的区别（这一层最容易被忽视！）

### HID：数据有"说明书"——Report Descriptor

HID 协议不光传字节，还附带一份 **Report Descriptor** 告诉主机：

```
"我发过来的数据第0字节是X轴(12bit)，第2字节是Y轴(12bit)，
 第3字节 bit0 是左键，bit1 是右键..."
```

来自 USB HID 规范 — Report Descriptor 决定了：
- 每个 Report 多长（固定大小）
- 每段数据代表什么（Usage Page + Usage ID）
- 数据的范围（Logical Minimum/Maximum）

### CDC：数据是"裸字节流"——没有说明书

CDC-ACM 模拟的是传统串口，数据就是纯粹的字节序列：

```
发：0x48 0x65 0x6C 0x6C 0x6F
收：H    e    l    l    o
```

**没有结构，没有元数据，你发什么对方收什么。**

这就是为什么 printf 能用 CDC 而不能用 HID——printf 输出的是字节流，CDC 直接透传，而 HID 需要包装成 Report 格式。

---

## 四、STC AI8051U 的实际表现

| 场景 | HID 模式 | CDC 模式 |
|------|---------|---------|
| **烧录速度** | ~1-2 KB/s（全速64B/包） | 更快（批量传输占满剩余带宽） |
| **即插即用** | ✅ 插上就能烧 | ⚠️ 先装驱动才能烧 |
| **printf 调试** | ❌ 不行（HID 不是字节流） | ✅ 虚拟串口透传 |
| **仿真/断点调试** | ❌ 不支持 | ✅ CDC 仿真功能 |
| **不停电下载** | ✅ `@STCISP#` | ✅ 也支持 |
| **现场升级** | ✅ 推荐（免驱！） | ⚠️ 客户还得装驱动 |

---

## 五、协议层差异总结图

```
                    ┌──────────────┐
  应用层            │ HID Report   │  CDC 字节流
  (数据语义)         │ 结构化数据    │  原始透传
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
  OS 驱动层          │ HID 类驱动   │  CDC 类驱动
  (需要装吗？)        │ ✅ 系统自带   │  ⚠️ Win需要.inf
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
  传输类型            │ Interrupt   │  Bulk
  (调度策略)          │ 固定周期轮询  │  有空才传
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
  事务结构            │ Token→Data→HS│  Token→Data→HS
  (一模一样)          │   完全相同的包格式    │
                    └──────────────┘
```

**一句话总结：包格式一样，但 HD 是"公交车"（固定班次），CDC 是"出租车"（有空位就上，但可能等很久）。**

---

## 六、参考来源

1. **USB 2.0 Specification §5.7 (Page 76-79)**: Interrupt Transfers — "Guaranteed maximum service period"
2. **USB 2.0 Specification §5.8 (Page 80-84)**: Bulk Transfers — "Host Controllers are free to determine how the individual bus transactions are moved"
3. **USB 2.0 Specification §5.5.3 (Page 67)**: Control Transfer max packet = 64B (full-speed)
4. **USB 2.0 Specification Table 5-7 (Page 78)**: Full-speed Interrupt Transaction Limits
5. **USB 2.0 Specification Figure 5-14 (Page 90)**: 四种传输类型的 IRP→Transaction 结构对比
6. **USB 2.0 Specification §4.8 (Page 50)**: *"USB devices are divided into device classes such as hub, human interface..."*
7. **STC8H 系列单片机技术参考手册** — *"STC 的带硬件USB 的MCU 支持用硬件USB 下载，因为用的是USB-HID 通信协议，不需要安装任何驱动"*
