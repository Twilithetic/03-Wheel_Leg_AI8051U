# ADC DMA 循环与扫描间隔分析

> 基于: main.c + adc.c + adc.h + ai8051u_def.h + 芯片手册
> 日期: 2026-05-18

---

## 问题1: 现在的工程能一直循环吗？

### 答案: ❌ 不能！

### 原因分析

**触发流程:**
```
main() line 139 → ADC_Init() → 配置DMA，但不触发
main() line 140 → DMA_ADC_Trigger() → 触发一次
main() line 151 → while(1) { } → 空循环！什么都不做
```

**具体证据:**

1. **只触发一次** (main.c:140):
```c
DMA_ADC_Trigger();   // 触发了就完事
```

2. **没有使能中断** — `DMA_ADC_EnableInt()` 从未被调用
   - `DMA_ADC_CFG bit7 (ADCIE)` = 0，中断关闭

3. **没有ISR** — 整个工程中不存在 `interrupt 48` (DMA_ADC中断) 的函数

4. **while(1) 是空的** (main.c:151-154):
```c
while (1)
{
    // 啥都没有！
}
```

5. **没有轮询标志** — 没有代码读取 `DMA_ADC_STA`

### 当前行为:
```
上电 → 初始化 → 触发一次ADC DMA → 3个通道各采1次 → 数据写入xdata → DMA停止 → CPU永远空转
```

---

## 问题2: ADC DMA 扫描间隔时间是什么？设成0会怎样？

### 答案: 有两个层面的"间隔"

#### 层面1: 通道间间隔 — `DMA_ADC_ITVH/ITVL` (已设为0)

```c
// adc.h:21
#define ADC_DMAITV  0   // ← 你设的这个

// adc.c:50
DMA_ADC_SetInterval(ADC_DMAITV);
// → DMA_ADC_ITVH = 0, DMA_ADC_ITVL = 0
```

**含义:** DMA在切换ADC通道时的**额外等待时间**（系统时钟数）

**ITV=0 的效果:** 通道间无额外延迟，DMA以硬件最大速度连续扫描各通道。这是**最快的模式**！

#### 层面2: 每通道转换次数 — `DMA_ADC_CFG2[3:0]` (CVTIMESEL=0)

```c
// adc.c:37
ADC_DisableRepeatConv();  // CVTIMESEL = 0

// adc.c:52  
DMA_ADC_DisableRepeatConv();  // 每个通道只转换1次
```

转换次数 = CVTIMESEL + 1 = 0 + 1 = **1次**

---

## 实际时序计算

### 系统时钟
```
PLL = 144MHz
SYSCLK = 144MHz / 4 = 36MHz   (CLK_SYSCLK_Divider(4))
ADC时钟 = SYSCLK = 36MHz       (ADC时钟不分频)
```

### 单通道ADC时间
```
建立时间 (STPCYC): 0  ADC时钟
保持时间 (HLDCYC): 1  ADC时钟
采样时间 (SMPCYC): 11 ADC时钟
转换时间 (SPEED+1)×32: (0+1)×32 = 32 ADC时钟
──────────────────────────
每通道总计: 0+1+11+32 = 44 ADC时钟 ≈ 1.22μs
```

### 一轮完整扫描 (3通道)
```
3通道 × 44 ADC时钟 = 132 ADC时钟 ≈ 3.67μs
+ DMA传输时间 (硬件处理，可忽略)
+ ITV间隔 = 0 (无额外延迟)
──────────────────────────
一轮总时间 ≈ 3.67μs  (理论最小)
```

---

## 如何改成持续循环？

### 方案A: 中断中重新触发（推荐，开销最小）

```c
// 1. 在ADC_Init()中加上中断使能:
DMA_ADC_EnableInt();   // 打开ADC DMA中断

// 2. 添加ISR (中断号48, 向量FF:0183H):
void ADC_DMA_ISR(void) interrupt 48
{
    DMA_ADC_ClearFlag();     // 清除中断标志
    DMA_ADC_Trigger();       // 立即重新触发！
    // 数据已被自动写入 pu8ADCDMABuffer[]
}
```

### 方案B: 主循环中轮询

```c
// 在ADC_Init()中:
DMA_ADC_EnableInt();  // 打开中断

// ISR只置标志:
bit g_bADCDMA_Done;
void ADC_DMA_ISR(void) interrupt 48
{
    DMA_ADC_ClearFlag();
    g_bADCDMA_Done = 1;
}

// 主循环:
while(1)
{
    if(g_bADCDMA_Done)
    {
        g_bADCDMA_Done = 0;
        // 处理 pu8ADCDMABuffer[] 数据...
        DMA_ADC_Trigger();  // 重新触发
    }
}
```

### 方案C: 增加重复转换次数（同一轮内多采几次）

```c
// DMA_ADC_CFG2 CVTIMESEL 可以设置每通道在一轮中重复转换次数:
DAM_ADC_SetRepeatTimes(3);  // CVTIMESEL=3 → 每通道转4次
// 但轮完成后仍需要重新触发！
```

---

## 总结

| 问题 | 答案 |
|------|------|
| 能一直循环吗？ | ❌ 不能，只触发一次就停了 |
| ITV=0 的意思？ | 通道间无额外延迟，最快速度扫描 |
| ITV设成会怎样？ | 已经设成0了，已是最快 |
| 一轮扫描多久？ | ~3.67μs (3通道，每个通道1次转换) |
| 要循环怎么办？ | 加中断ISR，在里面重新触发 |
