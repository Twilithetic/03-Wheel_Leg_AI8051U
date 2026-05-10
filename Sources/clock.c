//<<AICUBE_USER_HEADER_REMARK_BEGIN>>
////////////////////////////////////////
// 在此添加用户文件头说明信息  
// 文件名称: clock.c
// 文件描述: 
// 文件版本: V1.0
// 修改记录:
//   1. (2026-05-03) 创建文件
////////////////////////////////////////
//<<AICUBE_USER_HEADER_REMARK_END>>


#include "config.h"


//<<AICUBE_USER_INCLUDE_BEGIN>>
// 在此添加用户头文件包含  
//<<AICUBE_USER_INCLUDE_END>>


//<<AICUBE_USER_GLOBAL_DEFINE_BEGIN>>
// 在此添加用户全局变量定义、用户宏定义以及函数声明  
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



//<<AICUBE_USER_FUNCTION_IMPLEMENT_BEGIN>>
// 在此添加用户函数实现代码  
//<<AICUBE_USER_FUNCTION_IMPLEMENT_END>>


