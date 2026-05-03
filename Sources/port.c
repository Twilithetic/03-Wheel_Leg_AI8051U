//<<AICUBE_USER_HEADER_REMARK_BEGIN>>
////////////////////////////////////////
// 在此添加用户文件头说明信息  
// 文件名称: port.c
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
// P3口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT3_Init(void)
{
    SetP3nInitLevelHigh(PIN_ALL);       //设置P3初始化电平
    SetP3nQuasiMode(PIN_7 | PIN_6 | PIN_5 | PIN_4 | PIN_3 | PIN_2); //设置P3.7,P3.6,P3.5,P3.4,P3.3,P3.2为准双向口模式
    SetP3nHighZInputMode(PIN_1 | PIN_0); //设置P3.1,P3.0为高阻输入模式
    SetP3nManualMode(PIN_ALL);          //设置P3手动配置端口模式

    DisableP3nPullUp(PIN_ALL);          //关闭P3内部上拉电阻
    DisableP3nPullDown(PIN_ALL);        //关闭P3内部下拉电阻
    EnableP3nSchmitt(PIN_ALL);          //使能P3施密特触发
    SetP3nSlewRateNormal(PIN_ALL);      //设置P3一般翻转速度
    SetP3nDrivingNormal(PIN_ALL);       //设置P3一般驱动能力
    SetP3nDigitalInput(PIN_ALL);        //使能P3数字信号输入功能

    //<<AICUBE_USER_PORT3_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT3_INITIAL_END>>
}

////////////////////////////////////////
// P5口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT5_Init(void)
{
    SetP5nInitLevelHigh(PIN_ALL);       //设置P5初始化电平
    SetP5nQuasiMode(PIN_5 | PIN_4 | PIN_3 | PIN_2 | PIN_1 | PIN_0); //设置P5.5,P5.4,P5.3,P5.2,P5.1,P5.0为准双向口模式
    SetP5nHighZInputMode(PIN_7 | PIN_6); //设置P5.7,P5.6为高阻输入模式
    SetP5nManualMode(PIN_ALL);          //设置P5手动配置端口模式

    DisableP5nPullUp(PIN_ALL);          //关闭P5内部上拉电阻
    DisableP5nPullDown(PIN_ALL);        //关闭P5内部下拉电阻
    EnableP5nSchmitt(PIN_ALL);          //使能P5施密特触发
    SetP5nSlewRateNormal(PIN_ALL);      //设置P5一般翻转速度
    SetP5nDrivingNormal(PIN_ALL);       //设置P5一般驱动能力
    SetP5nDigitalInput(PIN_5 | PIN_4 | PIN_3 | PIN_2 | PIN_1 | PIN_0); //使能P5.5,P5.4,P5.3,P5.2,P5.1,P5.0数字信号输入功能
    SetP5nAnalogInput(PIN_7 | PIN_6);   //使能P5.7,P5.6模拟信号输入功能

    //<<AICUBE_USER_PORT5_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT5_INITIAL_END>>
}



//<<AICUBE_USER_FUNCTION_IMPLEMENT_BEGIN>>
// 在此添加用户函数实现代码  
//<<AICUBE_USER_FUNCTION_IMPLEMENT_END>>


