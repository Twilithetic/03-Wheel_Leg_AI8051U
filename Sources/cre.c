//<<AICUBE_USER_HEADER_REMARK_BEGIN>>
////////////////////////////////////////
// 在此添加用户文件头说明信息  
// 文件名称: cre.c
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
// 自动追频初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void CRE_Init(void)
{
    uint32_t cnt;
    uint32_t res;

    CLK_HIRC_44MHzBand();               //选择44MHz频段

    CRE_OneStepMode();                  //设置单步追频模式
    CRE_CalibCycle_1ms();               //设置追频周期

    cnt = CRE_LFCNT(CRE_FREQ);          //设置自动追频的频率
    res = CRE_LFERROR(CRE_FREQ, CRE_ERROR); //设置自动追频的误差
    CRE_SetCalibCounter(cnt);           //设置自动追频的计数值
    CRE_SetCalibError(res);             //设置自动追频的误差值

    CRE_Enable();                       //启动自动追频

    //<<AICUBE_USER_CRE_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_CRE_INITIAL_END>>
}



//<<AICUBE_USER_FUNCTION_IMPLEMENT_BEGIN>>
// 在此添加用户函数实现代码  
//<<AICUBE_USER_FUNCTION_IMPLEMENT_END>>


