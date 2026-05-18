# ADC printf 输出修复计划

## 问题描述
当前 `TIMER2_ISR` 中断服务程序中，每秒触发一次的 `printf` 只输出 `"Hello USB!\r\n"`，没有把采集到的 ADC 值（`adc1`, `adc2`, `adc3`）一并输出到 USB 虚拟串口。

## 问题分析

### 当前代码逻辑（main.c 第 44-73 行）
```
TIMER2_ISR（1ms 中断）:
  ├── tick_1s++, tick_1ms++
  ├── 如果 tick_1s >= 1000（每秒）:
  │     ├── 翻转 LED
  │     ├── 修改 PWM 占空比
  │     └── printf("Hello USB!\r\n")    ← 这里没输出 ADC！
  └── 如果 tick_1ms >= 1（每 1ms）:
        ├── adc1 = ADC_Convert(1)
        ├── adc2 = ADC_Convert(2)
        └── adc3 = ADC_Convert(3)
```

### 技术细节
1. **printf 重定向链路**：`printf` →（宏替换）→ `printf_usb`，由 `stc_usb_cdc_32g_xdata.lib` 预编译库实现，通过 USB CDC Bulk IN 端点发送到 PC 虚拟串口
2. **ADC 全局变量**：`uint16_t adc1, adc2, adc3`（在 main.c 第 36-38 行定义），每 1ms 更新一次
3. **执行顺序**：同一中断内先 printf 后 ADC 采样，printf 输出的是**上一个 1ms 周期**的 ADC 值（对 1 秒级输出来说完全够用）
4. **format 占位符**：`%u` 用于无符号 16 位整数（`uint16_t`），C251 编译器完全支持标准 printf 格式

## 解决方案

### 修改内容
将第 63 行的：
```c
printf("Hello USB!\r\n");
```
改为：
```c
printf("ADC1=%u ADC2=%u ADC3=%u\r\n", adc1, adc2, adc3);
```

### 修改位置
- **文件**：`Sources/main.c`
- **行号**：第 63 行
- **影响范围**：仅修改 printf 格式字符串和参数，不影响其他逻辑

### 输出效果示例
```
ADC1=2048 ADC2=1536 ADC3=3120
ADC1=2047 ADC2=1538 ADC3=3119
...
```
每秒一行，刷新在串口助手中。

## 总结
- 改动极小，仅一行代码
- 不涉及中断时序变更
- ADC 采样速率（每 1ms 三通道）和 printf 输出速率（每秒一次）互相独立
- 如有需要后续可增加时间戳、单位换算（如 mV）等功能
