# AI8051U 中断系统详解 — EA 与 IE2

> 姐姐专为宝宝整理的中断速查笔记 💖

---

## 一、中断控制的两级架构

```
                    ┌─────────────────────┐
                    │   EA = 1  总闸 🔴    │  IE 寄存器 bit7
                    │  EnableGlobalInt()  │  不开=所有中断全灭
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ ET0 = 1 │          │  ES = 1 │          │EUSB = 1 │
   │ 定时器0  │          │  串口1   │          │  USB 🔵 │
   │ 分闸 ✅  │          │ 分闸 ✅  │          │ 分闸 ✅  │
   └─────────┘          └─────────┘          └─────────┘
        IE 寄存器                               IE2 寄存器
```

**中断触发 = 总闸开 + 对应分闸开，缺一不可！**

---

## 二、IE 寄存器 — 全局 + 标准中断 (地址 0xA8)

```c
sfr  IE  = 0xa8;            // 标准中断使能寄存器
sbit EA  = IE^7;            // 🔴 全局中断总开关
sbit ELVD = IE^6;           // 低压检测中断
sbit EADC = IE^5;           // ADC 中断
sbit ES  = IE^4;            // 串口 1 中断
sbit ET1 = IE^3;            // 定时器 1 中断
sbit EX1 = IE^2;            // 外部中断 1
sbit ET0 = IE^1;            // 定时器 0 中断
sbit EX0 = IE^0;            // 外部中断 0
```

| 位 | 名称 | 作用 | 你的项目 |
|:---:|------|------|:---:|
| **bit7** | **EA** 🔴 | **全局中断总闸** | ✅ `main.c:152` |
| bit6 | ELVD | 低压检测 | - |
| bit5 | EADC | ADC | - |
| bit4 | ES | 串口 1 | - |
| bit3 | ET1 | 定时器 1 | - |
| bit2 | EX1 | 外部中断 1 | - |
| bit1 | ET0 | 定时器 0 | ✅ `main.c:50` |
| bit0 | EX0 | 外部中断 0 | - |

### 宏定义速查

```c
#define EnableGlobalInt()    (EA = 1)     // 开总闸
#define DisableGlobalInt()   (EA = 0)     // 关总闸
#define TIMER0_EnableInt()   (ET0 = 1)    // 定时器0分闸
#define TIMER0_DisableInt()  (ET0 = 0)
```

---

## 三、IE2 寄存器 — 扩展中断 (地址 0xAF)

```c
sfr  IE2  = 0xaf;           // 扩展中断使能寄存器
sbit EUSB = IE2^7;           // 🔵 USB 中断 ⚡ IE2 |= 0x80
sbit ET4  = IE2^6;           // 定时器 4 中断
sbit ET3  = IE2^5;           // 定时器 3 中断
sbit ES4  = IE2^4;           // 串口 4 中断
sbit ES3  = IE2^3;           // 串口 3 中断
sbit ET2  = IE2^2;           // 定时器 2 中断
sbit ESPI = IE2^1;           // SPI 中断
sbit ES2  = IE2^0;           // 串口 2 中断
```

| 位 | 名称 | 作用 | 你的项目 |
|:---:|------|------|:---:|
| **bit7** | **EUSB** 🔵 | **USB 中断** | ✅ 库内部自动开 |
| bit6 | ET4 | 定时器 4 | - |
| bit5 | ET3 | 定时器 3 | - |
| bit4 | ES4 | 串口 4 | - |
| bit3 | ES3 | 串口 3 | - |
| bit2 | ET2 | 定时器 2 | - |
| bit1 | ESPI | SPI | - |
| bit0 | ES2 | 串口 2 | - |

### 宏定义速查

```c
#define IE2_EUSB_MSK          BIT7
#define USB_EnableInt()       SET_REG_BIT(IE2, IE2_EUSB_MSK)    // IE2 |= 0x80
#define USB_DisableInt()      CLR_REG_BIT(IE2, IE2_EUSB_MSK)    // IE2 &= ~0x80

#define TIMER2_EnableInt()    SET_REG_BIT(IE2, BIT2)
#define TIMER3_EnableInt()    SET_REG_BIT(IE2, BIT5)
#define TIMER4_EnableInt()    SET_REG_BIT(IE2, BIT6)
#define UART2_EnableInt()     SET_REG_BIT(IE2, BIT0)
#define UART3_EnableInt()     SET_REG_BIT(IE2, BIT3)
#define UART4_EnableInt()     SET_REG_BIT(IE2, BIT4)
#define SPI_EnableInt()       SET_REG_BIT(IE2, BIT1)
```

---

## 四、中断优先级 — IP / IP2 寄存器

AI8051U 的中断优先级是 **2-bit** 的（4 个级别）：

| 优先级 | IP位 | IPH位 | 含义 |
|:---:|:---:|:---:|------|
| 0 (最低) | 0 | 0 | 你的 USB 设的级别 |
| 1 | 1 | 0 | |
| 2 | 0 | 1 | |
| 3 (最高) | 1 | 1 | |

### IP 寄存器 (地址 0xB8) — 标准中断优先级

```c
sfr  IP  = 0xb8;    // 低优先级位
sfr  IPH = 0xb7;    // 高优先级位 (High)

// 各中断源: PPCA, PLVD, PADC, PS, PT1, PX1, PT0, PX0
```

### IP2 寄存器 (地址 0xB5) — 扩展中断优先级

```c
sfr  IP2  = 0xb5;    // 低优先级位
sfr  IP2H = 0xb6;    // 高优先级位 (High)

// bit7 = PUSB/PUSBH  — USB 中断优先级
// bit6 = PI2C/PI2CH  — I2C 中断优先级
// bit5 = PCMP/PCMPH  — 比较器中断优先级
// bit4 = PX4/PX4H    — 外部中断4优先级
// bit3 = PPWMB/PPWMBH— PWMB 中断优先级
// bit2 = PPWMA/PPWMAH— PWMA 中断优先级
// bit1 = PSPI/PSPIH  — SPI 中断优先级
// bit0 = PS2/PS2H    — 串口2中断优先级
```

### USB 优先级设置宏

```c
#define IP2_PUSB_MSK      BIT7
#define IP2H_PUSBH_MSK    BIT7

#define USB_SetIntPriority(n)  \
    MODIFY_REG(IP2, IP2_PUSB_MSK, (((n) & 1) << 7));   \
    MODIFY_REG(IP2H, IP2H_PUSBH_MSK, ((((n) >> 1) & 1) << 7))
```

**你的代码调用**：
```c
USB_SetIntPriority(0);   // n=0 → IP2.7=0, IP2H.7=0 → 优先级0 (最低)
                         // 等价于 IP2 &= ~0x80; IP2H &= ~0x80
```

---

## 五、你项目中的实际调用链路

```
SYS_Init()                          main.c:121
│
├── usb_init()                      usblib.c:34
│     └── 库内部自动: IE2 |= 0x80   ← EUSB 分闸 🔵 由库完成
│
├── USB_SetIntPriority(0)           usblib.c:35
│     └── IP2 &= ~0x80             ← USB 优先级设为最低
│         IP2H &= ~0x80
│
└── EnableGlobalInt()               main.c:152
      └── EA = 1                    ← 总闸 🔴 最后拉！

结果: EA=1 + EUSB=1 → USB 中断可用 ✅
```

---

## 六、三个 `|= 0x80` 终极对比

| 写法 | 寄存器 | 地址 | bit7名称 | 功能 | 代码位置 |
|------|--------|:---:|---------|------|---------|
| `EA = 1` | **IE** | 0xA8 | **EA** 🔴 | 全局中断总闸 | `main.c:51, 152` |
| `IE2 \|= 0x80` | **IE2** | 0xAF | **EUSB** 🔵 | USB中断分闸 | `usb_init()` 库内部 |
| `P_SW2 \|= 0x80` | **P_SW2** | 0xBA | **EAXFR** 🟢 | XFR扩展寄存器访问 | `main.c:123` |

**记忆口诀**：
```
EA → 总闸 🔴
EUSB → USB闸 🔵  
EAXFR → 大门钥匙 🟢
```

---

## 七、完整中断寄存器地址速查表

| 寄存器 | 地址 | 所属空间 | 功能 |
|--------|:---:|---------|------|
| **IE** | 0xA8 | 标准 SFR | 全局+标准中断使能 |
| **IE2** | 0xAF | 标准 SFR | 扩展中断使能 |
| **IP** | 0xB8 | 标准 SFR | 标准中断低优先级 |
| **IPH** | 0xB7 | 标准 SFR | 标准中断高优先级 |
| **IP2** | 0xB5 | 标准 SFR | 扩展中断低优先级 |
| **IP2H** | 0xB6 | 标准 SFR | 扩展中断高优先级 |
| **IP3** | 0xDF | 标准 SFR | 更多扩展低优先级 |
| **IP3H** | 0xEE | 标准 SFR | 更多扩展高优先级 |

> 以上寄存器全部在标准 SFR 空间（0x80-0xFF），**不需要** EAXFR 使能即可访问！

---

*姐姐随时帮宝宝更新~ 💖*
