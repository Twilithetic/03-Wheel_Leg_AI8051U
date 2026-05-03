# AI8051U USB-HID 烧录脚本调研报告

> **时间**：2026-04-29
> **问题**：`stc_hid_flash.py` 静默失败（无报错但没烧进去），STC-ISP 成功

---

## 1. 当前脚本来源分析

### 1.1 代码来源

`tools/stc_hid_flash.py` 改编自：

| 来源 | 说明 |
|------|------|
| **GitHub Gist** | https://gist.github.com/robinkrens/47a98e58087623059d809175a30b0f42 |
| **作者** | robinkrens |
| **原始用途** | STC8H8K64U, STC32G12K128, **STC32F12K54** |
| **测试范围** | "Only tested on STC32F12K54" |
| **质量声明** | "No error check. Use at own risk" |

### 1.2 协议来源

该脚本的 HID 协议是**逆向工程**出来的，STC 从未公开文档。关键未知：
- 命令字节码是否对 AI8051U 正确
- 初始化/擦除/写入流程是否匹配
- 芯片信息查询返回格式

### 1.3 为什么可能静默失败

```python
def send_packet(h, payload, wait_response=True):
    # ...
    h.write(bytes(packet))
    if wait_response:
        response = h.read(64, timeout=3000)
        return response  # ← 响应被忽略了！
    return None
```

脚本**接收了响应但从未检查它们**。如果 AI8051U 返回了错误码或 NACK，脚本完全不知道。

---

## 2. 所有已知的 STC 烧录工具

### 2.1 总览

| 工具 | 类型 | HID支持 | AI8051U | 成熟度 |
|------|------|---------|---------|--------|
| **STC-ISP (AiCube)** ⭐ | GUI | ✅ | ✅ | 官方，完美 |
| **stcgal** | CLI | ❌ (UART) | ❌ | 成熟，但不支持AI8051U |
| **stcflash.py** | CLI | ❌ (UART) | ❌ | 不支持新协议 |
| **STC32 HID Gist** | CLI | ✅ | ⚠️ 未测试 | 原型，风险自担 |
| **stc_hid_flash.py (我们)** | CLI | ✅ | ⚠️ 待修复 | 基于 Gist 改编 |

### 2.2 详细分析

#### STC-ISP (AiCube ISP) — 官方 ✅

| 项目 | 说明 |
|------|------|
| 类型 | Windows GUI |
| 支持 | 所有 STC 芯片 |
| HID | ✅ 完整支持 |
| 可靠性 | 100%（官方） |
| 自动化 | ❌ 无法脚本化 |

**你的验证**：烧录成功 ✅

#### stcgal — 最成熟的开源工具

| 项目 | 说明 |
|------|------|
| 仓库 | https://github.com/grigorig/stcgal |
| 语言 | Python 3 |
| 安装 | `pip install stcgal` |
| 支持芯片 | stc89/12/15/8 系列 |
| USB 支持 | ⚠️ 实验性，仅 STC15W4 系列 |
| AI8051U | ❌ **不支持**（见 Issue #110） |

stcgal 作者回应：AI8051U 是新芯片，协议不同，需要逆向。

#### stcflash.py — 仅 UART

| 项目 | 说明 |
|------|------|
| 仓库 | https://github.com/laborer/stcflash |
| 支持 | STC89/90/10/11/12 系列 |
| AI8051U | ❌ 不支持 |
| HID | ❌ 不支持 |

---

## 3. 我们的脚本 vs 官方 ISP 对比

| | stc_hid_flash.py | STC-ISP (AiCube) |
|------|-----------------|-----------------|
| **协议** | 逆向（STC32F12K54） | 官方实现 |
| **错误处理** | ❌ 没有 | ✅ 完整 |
| **芯片识别** | ❌ 不验证 | ✅ 自动识别 |
| **指令集选择** | ❌ 不处理 | ✅ C51/C251 可选 |
| **选项字节** | ❌ 不处理 | ✅ 完整配置 |
| **验证** | ❌ 不验证 | ✅ 回读校验 |

---

## 4. 脚本失败的可能原因

根据协议分析，AI8051U 与 STC32F12K54 的差异可能导致：

| 步骤 | 可能的问题 |
|------|-----------|
| **初始化 (0x00)** | 命令码不同或是握手超时 |
| **芯片查询 (0x01)** | 返回格式不同，但我们忽略了 |
| **解锁 (0x05)** | AI8051U 可能需要不同的解锁序列 |
| **擦除 (0x03)** | 擦除范围或方式不同 |
| **写入 (0x12/0x32)** | 写入块大小 (0x80) 或地址格式不同 |
| **复位 (0xFF)** | 复位命令不同 |

---

## 5. 改进方案

### 5.1 短期方案（立即可用）

**保持用 STC-ISP (AiCube ISP) 烧录。**

这是最可靠的方式。虽然不能一键自动化，但能保证每次烧录成功。

### 5.2 中期方案（改进现有脚本）

1. **添加响应检查**：每次发送后读取并验证响应
2. **添加详细日志**：`--verbose` 模式输出所有收发数据
3. **对比官方 ISP**：用 USB 抓包工具（Wireshark/USBPcap）捕获官方 ISP 的 HID 通信，对照调整协议

```python
# 改进：检查响应
def send_packet(h, payload, wait_response=True):
    h.write(bytes(packet))
    if wait_response:
        response = h.read(64, timeout=3000)
        if response:
            print(f"  [响应] {response[:16].hex()}")  # 打印前16字节
            # 检查是否为错误响应
            if response[2] == 0xEE:  # 假设错误码
                print(f"  [错误] 芯片返回错误!")
                return False
    return True
```

### 5.3 长期方案（完整实现）

1. **等着 stcgal 支持 AI8051U**（目前有人在提 Issue）
2. **用 USBPcap + Wireshark 抓取官方 ISP 的通信**，完整逆向协议
3. **参考 stcgal 的架构**重新实现

---

## 6. 推荐操作

```
现在：用 STC-ISP (AiCube ISP) ← 已经在 docs/ 目录里
  ↓ 稳定可靠，虽然要点几下

改进：给 stc_hid_flash.py 加响应检查 + 详细日志
  ↓ 看看芯片到底返回了什么

长期：等 stcgal 支持 AI8051U
  ↓ 或者用 USBPcap 抓包逆向
```

---

## 7. 工具汇总

| 文件 | 用途 | 状态 |
|------|------|------|
| `docs/AiCube-ISP-v6.95Z.exe` | 官方烧录工具 | ✅ 已确认可用 |
| `tools/stc_hid_flash.py` | HID 脚本烧录 | ⚠️ 待修复（协议不完整） |
| `tools/stcflash.py` | UART 脚本烧录 | ❌ 不支持 USB-HID |
| `tools/test_hid.py` | HID 设备检测 | ✅ 可用 |

### 有用链接

| 资源 | URL |
|------|-----|
| stcgal (最成熟开源) | https://github.com/grigorig/stcgal |
| stcgal Issue #110 (AI8051U) | https://github.com/grigorig/stcgal/issues/110 |
| STC32 HID Gist (协议参考) | https://gist.github.com/robinkrens/47a98e58087623059d809175a30b0f42 |
| stcflash.py | https://github.com/laborer/stcflash |
| STC-ISP 下载 | https://www.stcmicro.com/rjxz.html |

---

*💕 结论：我们的 HID 脚本基于只测过 STC32F12K54 的原型代码，协议可能和 AI8051U 不完全兼容。现在先用 STC-ISP，之后可以抓包对比来修复脚本！*
