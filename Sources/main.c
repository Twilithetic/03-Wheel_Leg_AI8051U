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


//<<AICUBE_USER_INCLUDE_BEGIN>>
// 在此添加用户头文件包含  
//<<AICUBE_USER_INCLUDE_END>>


//<<AICUBE_USER_GLOBAL_DEFINE_BEGIN>>
// 在此添加用户全局变量定义、用户宏定义以及函数声明 

// ==================== 全局变量 ====================
volatile unsigned int tick_10ms = 0;   // 10ms 计数器

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
    
    // 3. 设置 8 位预分频器 (需要先访问扩展寄存器)
    EAXFR = 1;                 // 允许访问扩展 XFR
    TM0PS = 11;                // 预分频 ÷ 12
    EAXFR = 0;
    
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
    tick_10ms++;               // 每 10ms +1
    
    if (tick_10ms >= 10)      // 1 秒到了（10ms × 100 = 1000ms）
    {
        tick_10ms = 0;
        P42 = ~P42;            // 翻转 LED（0.5s 亮, 0.5s 灭 = 1Hz 闪烁）
    }
}
//<<AICUBE_USER_GLOBAL_DEFINE_END>>



////////////////////////////////////////
// 项目主函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void main(void)
{
    //<<AICUBE_USER_MAIN_INITIAL_BEGIN>>
    // 在此添加用户主函数初始化代码  
    //<<AICUBE_USER_MAIN_INITIAL_END>>

    SYS_Init();

    //<<AICUBE_USER_MAIN_CODE_BEGIN>>
    // 在此添加主函数中运行一次的用户代码  
	// GPIO 初始化为准双向口
    P0M1 = 0;   P0M0 = 0;
    P1M1 = 0;   P1M0 = 0;
    P2M1 = 0;   P2M0 = 0;
    P3M1 = 0;   P3M0 = 0;
    P4M1 = 0;   P4M0 = 0;
    P5M1 = 0;   P5M0 = 0;
    P6M1 = 0;   P6M0 = 0;
    P7M1 = 0;   P7M0 = 0;
    
    // 初始化端口
    P0 = 0xFF;  P1 = 0xFF;  P2 = 0xFF;
    P3 = 0xFF;  P4 = 0xFF;  P5 = 0xFF;
    // LED 初始状态：亮
    P42 = 0;
    // 启动定时器
    Timer0_Init();
    //<<AICUBE_USER_MAIN_CODE_END>>

    while (1) 
    {
        USBLIB_OUT_Done();              //查询方式处理USB接收的数据

        //<<AICUBE_USER_MAIN_LOOP_BEGIN>>
        // 在此添加主函数中用户主循环代码  
        //<<AICUBE_USER_MAIN_LOOP_END>>
    }
}

////////////////////////////////////////
// 系统初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void SYS_Init(void)
{
    EnableAccessXFR();                  //使能访问扩展XFR
    AccessCodeFastest();                //设置最快速度访问程序代码
    AccessIXramFastest();               //设置最快速度访问内部XDATA
    IAP_SetTimeBase();                  //设置IAP等待参数,产生1us时基

    //<<AICUBE_USER_PREINITIAL_CODE_BEGIN>>
    // 在此添加用户预初始化代码  
    //<<AICUBE_USER_PREINITIAL_CODE_END>>

    PORT3_Init();                       //P3口初始化
    PORT5_Init();                       //P5口初始化
    CLK_Init();                         //时钟模块初始化
    CRE_Init();                         //自动追频模块初始化
    delay_ms(1);
    USBLIB_Init();                      //USB库初始化
    delay_ms(1);
    MATHLIB_Init();                     //MATH库初始化

    //<<AICUBE_USER_INITIAL_CODE_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_INITIAL_CODE_END>>

    EnableGlobalInt();                  //使能全局中断
    USBLIB_WaitConfiged();              //等待USB完成配置
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


