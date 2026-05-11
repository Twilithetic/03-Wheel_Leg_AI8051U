//<<AICUBE_USER_HEADER_REMARK_BEGIN>>
////////////////////////////////////////
// 在此添加用户文件头说明信息  
// 文件名称: usblib.c
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
// USB库初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void USBLIB_Init(void)
{
    usb_init();                         //初始化USB模块
    //USB_SetIntPriority(0);              //设置中断为最低优先级
    set_usb_ispcmd("@STCISP#");         //设置USB不停电下载命令

    //<<AICUBE_USER_USBLIB_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_USBLIB_INITIAL_END>>
}

////////////////////////////////////////
// 等待USB配置完成函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void USBLIB_WaitConfiged(void)
{
    while (DeviceState != DEVSTATE_CONFIGURED) //等待USB完成配置
        WDT_Clear();                    //清看门狗定时器 (防止硬件自动使能看门狗)
}

////////////////////////////////////////
// USB设备接收数据处理程序
// 入口参数: 无
// 函数返回: 无
// bUsbOutReady：USB设备接收数据标志位
// OutNumber：USB设备接收到的数据长度
// UsbOutBuffer：保存USB设备接收到的数据
////////////////////////////////////////
void USBLIB_OUT_Done(void)
{
    if (bUsbOutReady)                   //查询是否有接收到USB主机发送数据
    {
        //<<AICUBE_USER_USBLIB_ISR_CODE1_BEGIN>>
        // 在此添加中断函数用户代码  
        USB_SendData(UsbOutBuffer, OutNumber); //原路返回, 用于测试
        //在此处添加用户处理接收数据的代码
        //<<AICUBE_USER_USBLIB_ISR_CODE1_END>>
        usb_OUT_done();                 //当前包的数据处理完成,通知USB主机可以发送下一包数据
    }
}



//<<AICUBE_USER_FUNCTION_IMPLEMENT_BEGIN>>
// 在此添加用户函数实现代码  
//<<AICUBE_USER_FUNCTION_IMPLEMENT_END>>


