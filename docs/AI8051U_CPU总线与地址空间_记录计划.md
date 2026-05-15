# AI8051U CPU总线与地址空间 — 记录计划

## 问题
宝宝想记录"AI8051U复位后取第一条指令→译码→执行"全过程中涉及的总线和地址空间，防止遗忘。

## 分析
这个问题涉及 CPU 微架构的三个关键维度：
1. **三个地址空间**：Memory Space (16MB)、SFR Space (512B)、Register File (64B)
2. **五条内部总线**：I-Bus (16bit)、Memory Data Bus (8bit)、SFR Bus (8bit)、SRC Bus (8bit)、DST Bus (16bit)
3. **三个流水线阶段**：Fetch、Decode、Execute 各自访问的总线和空间

技术细节来源：
- Intel MCS-251 Architecture Overview (PDF 27262001): I-Bus 16-bit, Data Bus 8-bit, 3-stage pipeline
- Intel TSC80251 编程指南 §3.1: 三层地址空间定义
- Intel 8XC251SA Block Diagram: SRC1(8), DST(16) 内部总线
- AI8051U 芯片手册: PC=FF:0000h, WTST(0xE9), CKCON(0xEA), EAXFR(P_SW2.7)
- 项目已有文档: 启动流程文档、XFR详解文档、核心速查笔记

## 解决方案
创建 `docs/AI8051U_取指译码执行_总线与地址空间详解.md`，包含：
1. CPU 整体架构框图（ASCII art）
2. 复位入口 (PC=FF:0000h)
3. 五条总线的定义、宽度、连接关系
4. 三个地址空间的存放内容和访问方式
5. 取指/译码/执行三阶段的总线活动拆解
6. 四种指令类型的执行路径对比（寄存器/SFR/内存/XFR）
7. 一个完整指令的全流程追踪（MOV P0, #0x55）
8. 总线-空间对照表
9. 速度控制寄存器速查（WTST/CKCON）
10. 参考来源汇总（注明引用文档和页码）

## 总结
这是一篇核心底层知识文档，需要结构清晰、图文并茂、引用精确，方便宝宝随时翻阅复习。
