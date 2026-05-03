# AI8051U USB-HID 设备分析 & 脚本烧录可行性报告

> **报告时间**：2026-04-29
> **设备**：STC AI8051U
> **数据来源**：USB Device Tree Viewer 完整输出 + 网络搜索

---

## 1. AI8051U 把自己声明成了什么？

### 1.1 设备身份一览

```
┌─────────────────────────────────────────────────────────┐
│         USB 设备: AI8051U (ISP 模式)                     │
├─────────────────────────────────────────────────────────┤
│  VID:PID            │ 0x34BF : 0x1001                   │
│  Manufacturer       │ "STC"                             │
│  Product            │ "USB-ISP"                         │
│  序列号              │ 无                                │
│  USB 版本            │ 2.0 (Full-Speed 12Mbps)           │
│  设备类              │ 0x00 (由接口定义)                  │
│  电流需求            │ 100 mA                            │
│  端口位置            │ Port_#0004.Hub_#0002 (1-1-4)     │
├─────────────────────────────────────────────────────────┤
│         Windows 识别结果                                  │
├─────────────────────────────────────────────────────────┤
│  设备描述            │ "USB 输入设备"                     │
│  总线报告描述         │ "USB-ISP"                         │
│  驱动                │ hidusb.sys (Microsoft)            │
│  类                  │ HIDClass                          │
│  服务                │ HidUsb                            │
│  二级识别            │ "符合 HID 标准的用户控制设备"       │
│  HID Usage           │ UsagePage=0x0C (Consumer)         │
│                      │ Usage=0x01 (Consumer Control)     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 USB 接口配置

```
配置:    1 个配置，1 个接口
接口:    Interface 0, HID 类 (bInterfaceClass=0x03)
端点:    2 个
  ├── EP4 IN   (0x84) — Interrupt, 64字节/包, 1ms 间隔
  └── EP4 OUT  (0x04) — Interrupt, 64字节/包, 1ms 间隔

HID 报告描述符: 23 字节 (读取失败，Win32 API 限制)
```

### 1.3 关键分析

| 特征 | 含义 |
|------|------|
| **HID 设备** | AI8051U 伪装成"用户控制设备"进入 ISP 模式 |
| **Interrupt 传输** | 不是 Bulk 传输！每个包最多 64 字节，1ms 间隔 |
| **VID=0x34BF** | 已注册给 STC Al Limited（见 USB-IF 数据库） |
| **无序列号** | 无法通过序列号区分多设备 |
| **驱动免安装** | HID 设备由系统自带驱动，即插即用 ✅ |
| **HID Usage 0x0C:0x01** | Consumer Control — 故意用一个通用类型避开了 HID 协议限制 |

### 1.4 为什么是 HID 而不是 CDC/串口？

STC 选择 HID 模式的好处：
- ✅ **免驱动**：Windows/Linux/Mac 系统自带 HID 驱动
- ✅ **免配置**：不需要安装 CH340 等额外驱动
- ✅ **权限低**：HID 设备不需要管理员权限
- ⚠️ **速度慢**：Interrupt 传输最大 64KB/s，大量数据时比 UART 慢

---

## 2. 能不能用脚本烧录？

### 2.1 答案：✅ 可以！

已经有人用 Python 实现了 STC USB-HID 烧录：

**GitHub Gist**: [STC32 USB HID program ISP](https://gist.github.com/robinkrens/47a98e58087623059d809175a30b0f42)

```python
import hid
h = hid.device()
h.open(0x34bf, 0x1001)  # ← 正是 AI8051U 的 VID:PID！

# HID 数据包格式:
# [0x46, 0xB9] + [方向] + [长度] + [负载] + [校验] + [0x16]
```

### 2.2 通信协议（从开源脚本逆向）

```
HID 包结构 (64 字节 max):
┌──────┬──────┬──────┬──────┬──────────┬──────┬──────┐
│ 0x46 │ 0xB9 │ 方向  │ 长度  │  负载    │ 校验  │ 0x16 │
│  (包头) │ (0x6A=发│ (2B)  │ (变长)    │ (2B)  │ (包尾)│
│        │ 0x68=收) │       │          │      │      │
└──────┴──────┴──────┴──────┴──────────┴──────┴──────┘

ISP 指令序列:
  1. 0x00 0x00          → 握手/初始化
  2. 0x01 + 芯片信息     → 查询芯片型号/容量
  3. 0x05 + 0x5A 0xA5   → 解锁
  4. 0x03 + 0x5A 0xA5   → 擦除 Flash
  5. 0x12/0x32 + 地址    → 写入数据 (每包 128 字节)
  6. 0xFF                → 复位，运行用户程序
```

### 2.3 需要的 Python 库

| 库 | 用途 | 安装 |
|-----|------|------|
| `hidapi` | USB HID 通信 | `pip install hidapi` |
| `intelhex` | 解析 HEX 文件 | `pip install intelhex` |
| `tqdm` | 进度条（可选） | `pip install tqdm` |

### 2.4 现有开源方案

| 工具 | HID 支持 | 状态 | 说明 |
|------|---------|------|------|
| **STC32 HID ISP (Gist)** | ✅ | 原型 | 已测试 STC32F12K54，协议通用 |
| **stcgal** | ⚠️ 实验性 | `usb15` 协议 | 仅支持 STC15W4 系列 USB-HID |
| **stcflash.py** | ❌ | 仅 UART | 项目已有 |
| **STC-ISP (官方)** | ✅ | 图形界面 | 功能完整但需要手动操作 |

---

## 3. 实现自动烧录的建议

### 3.1 路线图

```
           ┌──────────────────────┐
           │  参考开源 HID 脚本     │
           │  (Gist + stcgal)      │
           └──────────┬───────────┘
                      │
           ┌──────────▼───────────┐
           │  写 Python HID 烧录   │
           │  脚本 (hidapi +       │
           │  intelhex)            │
           └──────────┬───────────┘
                      │
           ┌──────────▼───────────┐
           │  集成到 EIDE 烧录     │
           │  (替换 stcflash.py)   │
           └──────────────────────┘
```

### 3.2 需要的库安装

```powershell
# 系统 Python (EIDE 烧录用)
python -m pip install hidapi intelhex tqdm
```

### 3.3 EIDE 烧录命令（替换后）

```yaml
# eide.yml
uploadConfigMap:
  Custom:
    commandLine: python ./tools/stc_hid_flash.py "${hexFile}"
```

---

## 4. 总结

| 问题 | 答案 |
|------|------|
| AI8051U 声明的设备类型？ | **HID** 设备（VID=0x34BF, PID=0x1001, Product="USB-ISP"） |
| 为什么要伪装成 Consumer Control？ | 免驱动，通用 HID Usage 避免权限限制 |
| 能用脚本烧录吗？ | ✅ 可以！有人已经用 Python hidapi 实现了 |
| stcflash.py 能用吗？ | ❌ 不能，它只支持 COM 口 |
| stcgal 能用吗？ | ⚠️ 实验性 USB 支持（仅 STC15 系列） |
| 最佳方案？ | 基于开源 Gist 写一个 `stc_hid_flash.py` |

---

## 5. 参考来源

| 来源 | 链接 |
|------|------|
| STC32 HID ISP Python 脚本 | https://gist.github.com/robinkrens/47a98e58087623059d809175a30b0f42 |
| stcgal (USB 支持) | https://github.com/grigorig/stcgal/blob/master/doc/USAGE.md |
| hidapi Python 库 | https://pypi.org/project/hidapi/ |
| intelhex Python 库 | https://pypi.org/project/intelhex/ |

---

*💕 总结：AI8051U 的 USB 模式是一个"特洛伊木马"——看起来是 Consumer Control HID 设备，实际上是 ISP 烧录通道。好消息是已经有人破解了协议，可以用 Python 脚本烧录！*
