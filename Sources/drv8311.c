#include "config.h"                     //默认已包含stdio.h、intrins.h等头文件
#include "drv8311.h"

void DRV8311_init(void){
    PWMB_Init();
    HSPWM_UpdateDuty(PWMB_CH5, 800);   // ← HSPWM 版！
    HSPWM_UpdateDuty(PWMB_CH6, 800);
    HSPWM_UpdateDuty(PWMB_CH7, 800);
}
