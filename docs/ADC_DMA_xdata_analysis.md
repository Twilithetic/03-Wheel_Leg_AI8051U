# AI8051U ADC_DMA 能否无限自动更新到 xdata 分析

> 基于文档: AI8051U芯片手册 + CSDN博客实战代码
> 日期: 2026-05-17

---

## 问题
ADC能不能用DMA无限自动更新数据到xdata？

## 分析

### 1. 寄存器概览 (来自芯片手册 Page 672, 674)

AI8051U确实有**ADC_DMA**功能，相关寄存器在 XFR 空间 (0x7EFA10~0x7EFA1F):

| 寄存器 | 地址 | 功能 |
|--------|------|------|
| DMA_ADC_CFG | 7EFA10H | 配置: ADCIE(bit7)中断使能, ADCMIP[1:0]优先级, ADCPTY[1:0] |
| DMA_ADC_CR | 7EFA11H | 控制: ENADC(bit7)使能, TRIG(bit6)触发 |
| DMA_ADC_STA | 7EFA12H | 状态: ADCIF(bit0)中断标志 |
| DMA_ADC_AMT | 7EFA13H | 传输总字节数(低8位) |
| DMA_ADC_DONE | 7EFA14H | 已完成字节数(低8位) |
| DMA_ADC_RXAH | 7EFA17H | 接收高地址 (xdata地址高字节) |
| DMA_ADC_RXAL | 7EFA18H | 接收低地址 |
| DMA_ADC_CFG2 | 7EFA19H | CVTIMESEL[3:0]: 每个通道ADC转换次数 |
| DMA_ADC_CHSW0 | 7EFA1AH | 通道使能 ADC7~ADC0 |
| DMA_ADC_CHSW1 | 7EFA1BH | 通道使能 ADC15~ADC8 |
| DMA_ADC_AMTH | 7EFA82H | 传输总字节数(高8位) |
| DMA_ADC_DONEH | 7EFA83H | 已完成字节数(高8位) |
| DMA_ADC_ITVH | 7EFA1EH | 时间间隔(高8位) |
| DMA_ADC_ITVL | 7EFA1FH | 时间间隔(低8位) |

### 2. 关键发现：不是真正的"无限自动"硬件循环！

从CSDN博客的实战代码(czhaii, 2025-09-10)可以清楚看到:

```c
// DMA配置 (只执行一次)
void DMA_Config(void)
{
    DMA_ADC_STA = 0x00;
    DMA_ADC_CFG = 0x80;          // bit7 使能中断
    DMA_ADC_RXAH = (u8)(0x800 >> 8);
    DMA_ADC_RXAL = (u8)0x800;
    DMA_ADC_CFG2 = 0x09;         // 每通道转换4次
    DMA_ADC_CHSW0 = 0xff;        // 使能ADC0~ADC7
    DMA_ADC_CHSW1 = 0xff;        // 使能ADC8~ADC15
    DMA_ADC_CR = 0xc0;           // bit7=1使能, bit6=1触发！
}

// ⚠️ 关键：中断中仅置标志，主循环里重新触发！
void ADC_DMA_Interrupt(void) interrupt 13
{
    DMA_ADC_STA = 0;    // 清除中断标志
    DmaFlag = 1;
}

void main(void)
{
    // ...
    while (1)
    {
        delay_ms(200);
        if(DmaFlag)
        {
            DmaFlag = 0;
            // 处理数据...
            
            // ⚠️ 必须手动重新触发！
            DMA_ADC_CR = 0xc0;  // bit7=1 EN, bit6=1 TRIG
        }
    }
}
```

### 3. 结论

| 特性 | AI8051U ADC_DMA | STM32 ADC+DMA Circular |
|------|-----------------|----------------------|
| 传输数据到xdata/SRAM | ✅ 支持 | ✅ 支持 |
| 多通道自动扫描 | ✅ 支持 (CHSW0/1) | ✅ 支持 |
| 硬件循环/无限模式 | ❌ **不支持！** | ✅ Circular Mode |
| 持续运行 | ⚠️ 需软件重新触发 | ✅ 硬件自动循环 |

**核心结论:** AI8051U的ADC_DMA是 **"一次触发 → 一轮完成 → 产生中断"** 的模式，**不支持STM32那种硬件Circular无限循环模式**。

### 4. 如何实现"近似连续"

如果想实现近似连续的效果，有几种方式：

**方式1: 中断里立即重新触发 (最快)**
```c
void ADC_DMA_Interrupt(void) interrupt 48
{
    DMA_ADC_STA = 0;
    DMA_ADC_CR = 0xc0;  // 立即重新触发
    // 此时新数据会覆盖上次的数据
}
```

**方式2: 使用 DMA_ADC_ITV (时间间隔) 自动触发**
- 设置 DMA_ADC_ITVH/ITVL 可以控制ADC采样间隔
- 但传输完成后的重新触发仍需软件介入

**方式3: 合并M2M_DMA做乒乓缓冲**
- 利用M2M_DMA在ADC_DMA完成后自动搬运数据到另一块xdata

### 5. 姐姐的提醒 💖

- AI8051U的DMA只支持**16位地址**寻址 (64KB xdata空间)，DMA_ADC_RXAH只有8位
- 中断向量：DMA_ADC在 interrupt **48** (地址 FF:0183H)，但CSDN示例代码中写的是interrupt 13，这可能针对不同型号；请看手册确认你的型号对应的中断号
- `DMA_ADC_CFG2`寄存器的`CVTIMESEL`设置了每通道转换次数，转换次数 = CVTIMESEL + 1
- 需要先 `EAXFR = 1` 才能访问XFR扩展寄存器
- xdata数组要用 `_at_ DMA_ADDR` 指定绝对地址，或直接写DMA_ADC_RXAH/RXAL
