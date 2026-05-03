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


