//<<AICUBE_USER_HEADER_REMARK_BEGIN>>
////////////////////////////////////////
// 在此添加用户文件头说明信息  
// 文件名称: main.c
// 文件描述: 
// 文件版本: V1.0
// 修改记录:
//   1. (2026-05-03) 创建文件
////////////////////////////////////////
//<<AICUBE_USER_HEADER_REMARK_END>>


#include "config.h"                     //默认已包含stdio.h、intrins.h等头文件
void usb_callback();
// ==================== 全局变量 ====================
volatile unsigned int tick_1s = 0;   // 10ms 计数器
volatile unsigned int tick_1ms = 0;   // 10ms 计数器

void TIMER2_Init(void)
{
#define T2_PSCR                 (1)
#define T2_RELOAD               (65536 - (float)SYSCLK / (T2_PSCR + 1) * 1000 / 1000000) //定时周期1000微秒

    TIMER2_TimerMode();                 //设置定时器2为定时模式
    TIMER2_1TMode();                    //设置定时器2为1T模式
    TIMER2_EnableInt();                 //使能定时器2中断
    TIMER2_SetPrescale(T2_PSCR);        //设置定时器2的8位预分频
    TIMER2_SetReload16(T2_RELOAD);      //设置定时器2的16位重载值
    TIMER2_Run();                       //定时器2开始运行

    //<<AICUBE_USER_TIMER2_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_TIMER2_INITIAL_END>>
}


////////////////////////////////////////
// 定时器2中断服务程序
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void TIMER2_ISR(void) interrupt TMR2_VECTOR
{
    //<<AICUBE_USER_TIMER2_ISR_CODE1_BEGIN>>
    // 在此添加中断函数用户代码  
    // 这个时钟1ms
    tick_1s++;               // 每 10ms +1
    tick_1ms++;
    
    if (tick_1s >= 1000)      // 1 秒到了（10ms × 100 = 1000ms）
    {
        tick_1s = 0;
        P42 = ~P42;            // 翻转 LED（0.5s 亮, 0.5s 灭 = 1Hz 闪烁）
    }

    if (tick_1s >= 1000)      // 1 秒到了（10ms × 100 = 1000ms）
    {
        HSPWM_UpdateDuty(PWMB_CH5, HSPWM_ReadCapture(PWMB_CH5) + 100)
    }

    //<<AICUBE_USER_TIMER2_ISR_CODE1_END>>
}

// ==================== T0 初始化 ====================
void Timer0_Init(void)
{
    // 1. 设置为模式 0（16 位自动重装载）
    TMOD &= 0xF0;              // 清除 T0 控制字段
    TMOD |= 0x00;              // GATE=0, C/T=0, M1=0, M0=0
    
    // 2. 设置重装载值（目标：10ms 中断）
    //    系统时钟 = 24MHz (默认 HIRC)
    //    TM0PS = 11 → 预分频 12 → 定时器时钟 = 2MHz
    //    65536 - 20000 = 45536 = 0xB1E0
    TL0 = 0xE0;                // 低字节先写
    TH0 = 0xB1;                // 高字节
    
    // 3. 设置 8 位预分频器（EAXFR 已在 SYS_Init 中打开，无需重复操作）
    TM0PS = 11;                // 预分频 ÷ 12
    
    // 4. 1T 模式（不分频，速度最快）
    AUXR |= 0x80;              // T0x12 = 1
    
    // 5. 开中断
    ET0 = 1;                   // 允许 T0 中断
    EA  = 1;                   // 开总中断
    
    // 6. 启动定时器
    TR0 = 1;                   // T0 开始计数
}

// ==================== T0 中断服务程序 ====================
void Timer0_ISR(void) interrupt 1
{
    // tick_1s++;               // 每 10ms +1
    
    // if (tick_1s >= 100)      // 1 秒到了（10ms × 100 = 1000ms）
    // {
    //     tick_1s = 0;
    //     P42 = ~P42;            // 翻转 LED（0.5s 亮, 0.5s 灭 = 1Hz 闪烁）
    // }
}
//<<AICUBE_USER_GLOBAL_DEFINE_END>>

////////////////////////////////////////
// 时钟初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void CLK_Init(void)
{
    CLK_HSIOCK_Divider(1);              //设置高速外设时钟预分频系数
    CLK_SPICLK_Divider(1);              //设置SPI时钟预分频系数
    CLK_I2SCLK_Divider(1);              //设置I2S时钟预分频系数
    CLK_PWMACLK_Divider(1);             //设置PWMA时钟预分频系数
    CLK_PWMBCLK_Divider(1);             //设置PWMB时钟预分频系数
    CLK_TFPUCLK_Divider(1);             //设置TFPU时钟预分频系数

    CLK_LIRC_Enable();                  //启动内部低速LIRC
    CLK_LIRC_WaitStable();              //等待振荡器稳定

    CLK_IRC48M_Enable();                //启动内部48M高速IRC
    CLK_IRC48M_WaitStable();            //等待振荡器稳定

    CLK_SYSCLK_Divider(10);             //切换主时钟前先将系统时钟降频

    HIRC_24M();                         //选择内部预置的频率

    CLK_MCLK_HIRC();                    //选择内部高精度HIRC作为PLL输入时钟
    CLK_PLL_Output144MHz();             //选择PLL的144M作为PLL的输出时钟
    CLK_PLL_PreDivider2();              //PLL输入时钟2分频
    CLK_PLL_Enable();                   //启动PLL
    delay_ms(1);                        //等待PLL锁频

    CLK_MCLK2_PLL();                    //选择PLL的输出时钟作为主时钟

    CLK_SYSCLK_Divider(4);              //设置系统时钟分频系数

    CLK_HSIOCK_MCLK();                  //选择MCLK主时钟作为高速外设时钟源

    //<<AICUBE_USER_CLOCK_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_CLOCK_INITIAL_END>>
}


////////////////////////////////////////
// 项目主函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void main(void)
{
    EAXFR = 1;			//允许访问扩展的特殊寄存器，XFR
	WTST = 0;				//设置取程序代码等待时间，赋值为0表示不等待，程序以最快速度运行
	CKCON = 0;			//设置访问片内的xdata速度，赋值为 0表示用最快速度访问，不增加额外的等待时间 
    P0M1 = 0x00;   P0M0 = 0x00;
    P1M1 = 0x00;   P1M0 = 0x00;
    P2M1 = 0x00;   P2M0 = 0x00;
    P3M1 = 0x00;   P3M0 = 0x00;
    P4M1 = 0x00;   P4M0 = 0x00;
    P5M1 = 0x00;   P5M0 = 0x00;
    P6M1 = 0x00;   P6M0 = 0x00;
    P7M1 = 0x00;   P7M0 = 0x00;
    CLK_Init();
    USBLIB_Init();                                     //USB CDC 接口配置
    
    
    //set_usb_ispcmd(0);  //禁用不停电下载功能会提升传输速度
    EA = 1;
    // LED 初始状态：亮
    P42 = 0;
    // 启动定时器
    // 芯片外设初始化
    PORT5_Init();
    // 外设控制初始化
    DRV8311_init();
    // 启动任务
    TIMER2_Init();
    //<<AICUBE_USER_MAIN_CODE_END>>、
    // DRV8311H配置 
    // GAIN: 1V/A (Pin to Hi-Z)
    // SLEW: 180V/us 
    // MODE: 3xPWM Mode and 9A OCP LEVEL
    // t_dead = 425ns, t_pd= 550ns 加上两个180V/us = 1.107us
    while (1)
    {

    }
}

////////////////////////////////////////
// P5口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT5_Init(void)
{
    SetP5nInitLevelHigh(PIN_ALL);       //设置P5初始化电平
    SetP5nQuasiMode(PIN_7 | PIN_6 | PIN_5 | PIN_4); //设置P5.7,P5.6,P5.5,P5.4为准双向口模式
    SetP5nPushPullMode(PIN_3 | PIN_2 | PIN_1 | PIN_0); //设置P5.3,P5.2,P5.1,P5.0为推挽输出模式
    SetP5nAutoMode(PIN_ALL);            //设置P5自动配置端口模式

    DisableP5nPullUp(PIN_ALL);          //关闭P5内部上拉电阻
    DisableP5nPullDown(PIN_ALL);        //关闭P5内部下拉电阻
    EnableP5nSchmitt(PIN_ALL);          //使能P5施密特触发
    SetP5nSlewRateFast(PIN_ALL);        //设置P5快速翻转速度
    SetP5nDrivingStrong(PIN_ALL);       //设置P5增强驱动能力
    SetP5nAnalogInput(PIN_ALL);         //使能P5模拟信号输入功能

    //<<AICUBE_USER_PORT5_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT5_INITIAL_END>>
}

////////////////////////////////////////
// USB库初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void USBLIB_Init(void)
{
    usb_init();                         //初始化USB模块
    set_usb_OUT_callback(usb_callback);             //设置中断回调回调函数

    //<<AICUBE_USER_USBLIB_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_USBLIB_INITIAL_END>>
}

void usb_callback()
{
    USB_SendData(UsbOutBuffer,OutNumber);           //发送数据缓冲区，长度（接收数据原样返回, 用于测试）
}



////////////////////////////////////////
// 微秒延时函数
// 入口参数: us (设置延时的微秒值)
// 函数返回: 无
////////////////////////////////////////
void delay_us(uint16_t us)
{
    do
    {
        NOP(30);                        //(MAIN_Fosc + 500000) / 1000000 - 6
    } while (--us);
}


////////////////////////////////////////
// 毫秒延时函数
// 入口参数: ms (设置延时的毫秒值)
// 函数返回: 无
////////////////////////////////////////
void delay_ms(uint16_t ms)
{
    uint16_t i;

    do
    {
        i = MAIN_Fosc / 6000;
        while (--i);
    } while (--ms);
}


//<<AICUBE_USER_FUNCTION_IMPLEMENT_BEGIN>>
// 在此添加用户函数实现代码  
//<<AICUBE_USER_FUNCTION_IMPLEMENT_END>>


