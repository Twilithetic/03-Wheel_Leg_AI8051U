# 烧录后无反应 — 诊断和修复

> **时间**：2026-05-03  
> **问题**：编译 Sources/main.c 烧录后 LED 不闪

---

## 🔍 诊断结果

**原因：`USBLIB_WaitConfiged()` 在等 USB 连接，卡住了整个程序！**

---

## 📋 代码流程分析

```c
void main(void)
{
    SYS_Init();              // ← 这里面的 USBLIB_WaitConfiged() 阻塞了！
    
    // 下面的代码永远执行不到：
    P42 = 0;                 // ❌ 没跑到
    Timer0_Init();           // ❌ 没跑到
}
```

### `SYS_Init()` 内部（第 146 行）：

```c
void SYS_Init(void)
{
    // ...
    USBLIB_Init();           // USB 初始化 ✅
    delay_ms(1);
    MATHLIB_Init();
    EnableGlobalInt();
    USBLIB_WaitConfiged();   // ⚠️ 等 USB 连上！可能会永远卡住！
}
```

### 什么时候会卡住？

| 场景 | 结果 |
|------|------|
| 板子 USB 连电脑 | ✅ USB 枚举完成 → 继续 → LED 闪 |
| 板子**独立供电**（USB 只供电不走数据） | ❌ 永远等不到 → 卡死 |
| USB 枚举慢 | ❌ 卡几秒 |

你烧录后 USB 线可能没插好，或者重新上电后 USB 还没枚举完，`USBLIB_WaitConfiged()` 就卡住了程序。

---

## ✅ 修复

### 方案 1：给等待加超时（推荐）

```c
void SYS_Init(void)
{
    // ... 前面的初始化不变 ...
    
    EnableGlobalInt();
    
    // 等待 USB 配置，最多等 2 秒
    uint16_t timeout = 2000;  // 2 秒
    while (DeviceState != DEVSTATE_CONFIGURED && --timeout)
    {
        delay_ms(1);
    }
    // 超时了也不管，继续跑
}
```

### 方案 2：直接注释掉（简单粗暴）

```c
void SYS_Init(void)
{
    // ...
    EnableGlobalInt();
    // USBLIB_WaitConfiged();   // ← 不要了
}
```

### 方案 3：先跑起来再等 USB

```c
void main(void)
{
    SYS_Init_without_wait();  // 初始化外设，不等 USB
    
    P42 = 0;
    Timer0_Init();            // 先跑起来！
    
    // 后台慢慢等 USB
    while(1)
    {
        // LED 已经在闪了
        // 这里后台处理 USB...
    }
}
```

---

## 🎯 建议

AiCube 生成的是"调试框架"——假设你一直连着 USB。改成产品时要加超时或去掉阻塞。

去 `Sources/main.c` 第 146 行，把 `USBLIB_WaitConfiged();` 注释掉试试！
