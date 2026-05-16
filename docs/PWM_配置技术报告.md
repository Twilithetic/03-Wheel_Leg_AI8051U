# AI8051U PWMB + DRV8311 配置技术报告

> 项目：03-March_Wheel_leg_FOC  
> 日期：2026-05-16  
> 芯片：AI8051U + DRV8311H

---

## 一、时钟架构

```
HIRC 24MHz
  │
  ▼
PLL ×6 → 144MHz ──── MCLK（主时钟）
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
      SYSCLK ÷4              HSIOCK ÷1
      36MHz（CPU跑）         144MHz（高速外设）
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               PWMA_CLK     PWMB_CLK     SPI/I2S...
               144MHz       144MHz
                              ↑
                           CK_INT
```

**关键：PWMB 的时钟源是 HSIOCK，不是 SYSCLK。PWMB 跑 144MHz，CPU 只跑 36MHz。**

时钟配置代码（`CLK_Init()`）：
```c
CLK_PWMBCLK_Divider(1);     // PWMB_CLK = HSIOCK / 1 = 144MHz
CLK_HSIOCK_MCLK();          // HSIOCK 源 = MCLK = 144MHz
CLK_SYSCLK_Divider(4);      // SYSCLK = 144 / 4 = 36MHz
```

---

## 二、PWMB 寄存器速查

| 寄存器 | 地址 | 功能 |
|--------|------|------|
| `PWMB_CR1` | 7EFEE0H | 控制：CEN启动、DIR方向、CMS对齐、ARPE预装载 |
| `PWMB_EGR` | 7EFEE7H | 事件产生：UG位初始化 |
| `PWMB_CCMR1` | 7EFEE8H | 通道5模式：OC5M[2:0]=110→PWM模式1 |
| `PWMB_CCER1` | 7EFEECH | 通道使能：CC5E/CC6E |
| `PWMB_CCER2` | 7EFEEDH | 通道使能：CC7E/CC8E |
| `PWMB_PSCRH/L` | 7EFEF0H/F1H | 16位预分频器 |
| `PWMB_ARRH/L` | 7EFEF2H/F3H | 16位自动重载（决定周期） |
| `PWMB_CCR5H/L` | 7EFEF5H/F6H | 通道5比较值（占空比） |
| `PWMB_CCR6H/L` | 7EFEF7H/F8H | 通道6比较值 |
| `PWMB_CCR7H/L` | 7EFEF9H/FAH | 通道7比较值 |
| `PWMB_BKR` | 7EFEFDH | 主输出使能 MOE |
| `PWMB_ENO` | 7EFEB5H | 输出使能：ENO5~ENO8 |
| `PWMB_PS` | 7EFEB6H | 引脚选择：C5PS~C8PS |
| `PWMB_ETRPS` | 7EFEB4H | 外部触发/刹车脚选择 |

---

## 三、PWM 频率计算

```
f_PWM = CK_INT ÷ (PSCR + 1) ÷ (ARR + 1)
```

当前配置：CK_INT=144MHz, PSCR=0, ARR=999 → **f_PWM = 144kHz**

**注意：PSCR 是整数除法器，CK_INT=144MHz 时无法得到 100MHz 的 CK_CNT。可选值：144/72/48/36/24... MHz。**

---

## 四、PWMB 引脚映射

| 通道 | CxPS=00 | CxPS=01 | CxPS=10 | CxPS=11 |
|:----:|:-------:|:-------:|:-------:|:-------:|
| PWM5 | **P0.1** | P1.1 | P2.1 | **P5.0** |
| PWM6 | P0.3 | P1.3 | P2.3 | P5.1 |
| PWM7 | P0.5 | P1.5 | P2.5 | P5.2 |
| PWM8 | P0.7 | P1.7 | P2.7 | P5.3 |

**当前使用 P5.0（C5PS=11），P5M0.0=1 推挽输出。**

**AI8051U 不支持 GPIO 矩阵——每个通道只有 4 个固定引脚可选。**

---

## 五、初始化流程（10步）

```c
void PWMB_Init(void)
{
    // 1. 选引脚
    PWMB_C5SwitchP50();          // PWM5 → P5.0
    // 2. 关高速模式（安全初始化）
    HSPWMB_Disable();
    // 3. 选内部时钟
    PWMB_InternalClockMode();    // SMS=000 → CK_INT
    // 4. 预分频
    PWMB_SetClockDivider(0);     // PSCR=0 → CK_CNT=144MHz
    // 5. 周期
    PWMB_SetReload16(999);       // ARR=999 → f_PWM=144kHz
    PWMB_BufferARR();            // ARPE=1 预装载
    PWMB_SetCounter(0);          // CNT=0
    // 6. 配置通道5
    PWMB_CC5PDisable();          // 先关
    PWMB_CC5Output();            // 输出模式
    PWMB_OC5REFPWMMode1();       // OC5M=110 PWM模式1
    PWMB_BufferCCR5();           // OC5PE=1 预装载
    PWMB_CC5PNonInverted();      // 高电平有效
    PWMB_CC5PEnable();           // 开通道
    // 7. 占空比（在开高速前写！）
    PWM_UpdateDuty(PWMB_CH5, 500);
    // 8. 使能输出
    PWMB_EnablePWM5POutput();    // ENO5=1
    // 9. 主输出
    PWMB_EnableMainOutput();     // MOE=1
    // 10. 开高速 + 启动
    HSPWMB_Enable();             // ASYNCEN=1
    HSPWMB_DisableInt();
    HSPWMB_Run();                // CEN=1
}
```

---

## 六、HSPWM 异步桥机制

### 原理

CPU（36MHz）和 PWMB（144MHz）在不同时钟域。开启高速模式（ASYNCEN=1）后，不能直接写 PWMB 的 SFR 寄存器，必须通过硬件异步桥。

### 硬件寄存器

| 寄存器 | 地址 | 作用 |
|--------|------|------|
| `HSPWMB_CFG` | 7EFBF4H | ASYNCEN=1 使能异步模式 |
| `HSPWMB_ADR` | 7EFBF5H | bit7=方向, bit6~0=目标地址 |
| `HSPWMB_DAT` | 7EFBF6H | 数据缓冲区 |

### 异步写流程

```
1. 读 HSPWMB_ADR，等 BUSY=0
2. 写数据到 HSPWMB_DAT
3. 写 (地址 | 0x00) 到 HSPWMB_ADR → 触发硬件搬移
4. 等 BUSY=0（可选）
```

### 代码实现

```c
// pwm.c
void HSPWMB_WriteReg(uint8_t addr, uint8_t dat)
{
    while (HSPWMB_ADR & 0x80);    // 等 BUSY=0
    HSPWMB_DAT = dat;             // 放数据
    HSPWMB_ADR = addr & 0x7F;     // 触发写
}

// 宏封装
#define WRITE_HSPWMB(r, d) \
    HSPWMB_WriteReg((BYTE0(&r) & 0x7f), BYTE0(d))
```

### ⚠️ 重要规则

| 场景 | 用哪个函数 |
|------|-----------|
| HSPWMB_Disable() 后 | `PWM_UpdateDuty()` 直接写 SFR ✅ |
| HSPWMB_Enable() 后 | `HSPWM_UpdateDuty()` 走异步桥 ✅ |
| PWMB_PS 寄存器 | **永远只能同步写！**（不属于PWMB寄存器组） |

---

## 七、DRV8311H 接口

| DRV8311H | AI8051U | 说明 |
|----------|---------|------|
| INHA | PWM5 (P5.0) | A相PWM |
| INHB | PWM6 (P5.1) | B相PWM |
| INHC | PWM7 (P5.2) | C相PWM |
| INLA/B/C | GPIO 接高 | 使能脚（3x PWM模式不需要Hi-Z） |
| SLEW | Hi-Z | 180V/µs |
| MODE | Hi-Z | 3x PWM模式, 9A OCP |
| GAIN | Hi-Z | 1V/A |

### DRV8311 内置死区

- **t_DEAD** ≈ 425ns（SLEW=Hi-Z, Handshake only）
- **t_PD** ≈ 550ns
- 死区机制：**VGS 电压检测**（不是纯时序延时），确认高边 MOSFET 真正关断后才开低边
- MCU死区与 DRV8311 死区取 **max()**

---

## 八、配置要点速记

| 要诀 | 说明 |
|------|------|
| 先关后配 | 写 CCER/CCMR 前先清 CCER |
| 先高后低 | 16位寄存器（ARR/CCR/PSCR）先写高字节 |
| UG 先于 CEN | 先 EGR=0x01 初始化，再 CR1=0x81 启动 |
| BKR 不能忘 | MOE=1 是总开关 |
| 高速后异步 | HSPWMB_Enable() 后只能用 HSPWM_UpdateDuty |
| P5 要推挽 | P5M0 \|= 0x0F，PWM 必须推挽 |
