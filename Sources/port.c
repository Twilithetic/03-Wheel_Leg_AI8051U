////////////////////////////////////////
// P1口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT1_Init(void)
{
    SetP1nInitLevelHigh(PIN_ALL);       //设置P1初始化电平
    SetP1nQuasiMode(PIN_7 | PIN_6 | PIN_5 | PIN_4 | PIN_3); //设置P1.7,P1.6,P1.5,P1.4,P1.3为准双向口模式
    SetP1nHighZInputMode(PIN_2 | PIN_1 | PIN_0); //设置P1.2,P1.1,P1.0为高阻输入模式
    SetP1nManualMode(PIN_ALL);          //设置P1手动配置端口模式

    DisableP1nPullUp(PIN_ALL);          //关闭P1内部上拉电阻
    DisableP1nPullDown(PIN_ALL);        //关闭P1内部下拉电阻
    EnableP1nSchmitt(PIN_ALL);          //使能P1施密特触发
    SetP1nSlewRateNormal(PIN_ALL);      //设置P1一般翻转速度
    SetP1nDrivingNormal(PIN_ALL);       //设置P1一般驱动能力
    SetP1nDigitalInput(PIN_ALL);        //使能P1数字信号输入功能

    //<<AICUBE_USER_PORT1_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT1_INITIAL_END>>
}

////////////////////////////////////////
// P2口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT2_Init(void)
{
    SetP2nInitLevelHigh(PIN_ALL);       //设置P2初始化电平
    SetP2nQuasiMode(PIN_ALL);           //设置P2为准双向口模式
    SetP2nManualMode(PIN_ALL);          //设置P2手动配置端口模式

    DisableP2nPullUp(PIN_ALL);          //关闭P2内部上拉电阻
    DisableP2nPullDown(PIN_ALL);        //关闭P2内部下拉电阻
    EnableP2nSchmitt(PIN_ALL);          //使能P2施密特触发
    SetP2nSlewRateNormal(PIN_ALL);      //设置P2一般翻转速度
    SetP2nDrivingNormal(PIN_ALL);       //设置P2一般驱动能力
    SetP2nDigitalInput(PIN_ALL);        //使能P2数字信号输入功能

    //<<AICUBE_USER_PORT2_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT2_INITIAL_END>>
}

////////////////////////////////////////
// P3口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT3_Init(void)
{
    SetP3nInitLevelHigh(PIN_ALL);       //设置P3初始化电平
    SetP3nQuasiMode(PIN_ALL);           //设置P3为准双向口模式
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
// P4口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT4_Init(void)
{
    SetP4nInitLevelHigh(PIN_ALL);       //设置P4初始化电平
    SetP4nQuasiMode(PIN_ALL);           //设置P4为准双向口模式
    SetP4nManualMode(PIN_ALL);          //设置P4手动配置端口模式

    DisableP4nPullUp(PIN_ALL);          //关闭P4内部上拉电阻
    DisableP4nPullDown(PIN_ALL);        //关闭P4内部下拉电阻
    EnableP4nSchmitt(PIN_ALL);          //使能P4施密特触发
    SetP4nSlewRateNormal(PIN_ALL);      //设置P4一般翻转速度
    SetP4nDrivingNormal(PIN_ALL);       //设置P4一般驱动能力
    SetP4nDigitalInput(PIN_ALL);        //使能P4数字信号输入功能

    //<<AICUBE_USER_PORT4_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT4_INITIAL_END>>
}

////////////////////////////////////////
// P5口初始化函数
// 入口参数: 无
// 函数返回: 无
////////////////////////////////////////
void PORT5_Init(void)
{
    SetP5nInitLevelHigh(PIN_ALL);       //设置P5初始化电平
    SetP5nQuasiMode(PIN_7 | PIN_6 | PIN_5 | PIN_4 | PIN_3); //设置P5.7,P5.6,P5.5,P5.4,P5.3为准双向口模式
    SetP5nPushPullMode(PIN_2 | PIN_1 | PIN_0); //设置P5.2,P5.1,P5.0为推挽输出模式
    SetP5nManualMode(PIN_ALL);          //设置P5手动配置端口模式

    DisableP5nPullUp(PIN_ALL);          //关闭P5内部上拉电阻
    DisableP5nPullDown(PIN_ALL);        //关闭P5内部下拉电阻
    EnableP5nSchmitt(PIN_ALL);          //使能P5施密特触发
    SetP5nSlewRateNormal(PIN_ALL);      //设置P5一般翻转速度
    SetP5nDrivingNormal(PIN_ALL);       //设置P5一般驱动能力
    SetP5nDigitalInput(PIN_ALL);        //使能P5数字信号输入功能

    //<<AICUBE_USER_PORT5_INITIAL_BEGIN>>
    // 在此添加用户初始化代码  
    //<<AICUBE_USER_PORT5_INITIAL_END>>
}

