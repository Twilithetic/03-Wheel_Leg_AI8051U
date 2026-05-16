#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速搜索 AI8051U 芯片手册中外设时钟相关内容 - 分页渐进式搜索"""

import pdfplumber
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

if not os.path.exists(pdf_path):
    print(f"错误: 找不到文件 {pdf_path}")
    sys.exit(1)

# 关键词
keywords = [
    "外设时钟", "外设", "时钟源", "时钟分频", "系统时钟",
    "SYSCLK", "HSCLK", "MCLK", "PCLK",
    "定时器时钟", "PCA时钟", "PWM时钟",
    "SPI时钟", "I2C时钟", "UART时钟", "串口时钟",
    "时钟控制", "时钟选择", "CLKDIV", "CLKSEL",
    "主时钟", "高速时钟", "低速时钟", "内部时钟",
    "时钟系统", "时钟框图", "时钟树",
    "HIRC", "LIRC", "外部晶振",
]

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    print(f"PDF 总页数: {total}")

    # 先扫描前30页找目录
    print("\n=== 扫描前30页寻找目录和时钟相关标题 ===")
    for i in range(min(30, total)):
        text = pdf.pages[i].extract_text()
        if text:
            for kw in ["目录", "时钟", "外设", "CLOCK"]:
                if kw in text:
                    print(f"\n--- 第 {i+1} 页 (包含 '{kw}') ---")
                    lines = text.split("\n")
                    for line in lines:
                        if kw in line:
                            print(f"  {line.strip()}")
                    break

    # 搜索时钟系统相关内容页面
    print("\n\n=== 搜索时钟/外设时钟相关页面 ===")
    found = []
    for i in range(total):
        text = pdf.pages[i].extract_text()
        if text:
            score = sum(1 for kw in keywords if kw.lower() in text.lower())
            if score > 0:
                found.append((i, score, text))
    
    # 按匹配度排序，取前15页
    found.sort(key=lambda x: -x[1])
    
    print(f"找到 {len(found)} 个相关页面，以下是匹配度最高的前15页:\n")
    
    for pg, score, txt in found[:15]:
        print(f"\n{'='*80}")
        print(f"第 {pg+1} 页 (关键词匹配数: {score})")
        print(f"{'='*80}")
        lines = txt.split("\n")
        shown = 0
        for line in lines:
            match_any = any(kw.lower() in line.lower() for kw in keywords)
            if match_any:
                print(f"  {line.strip()}")
                shown += 1
            if shown > 40:
                print(f"  ... (截断)")
                break
        
        # 如果匹配度很高,打印更多上下文
        if score >= 5:
            print(f"\n--- 本页全部文本 (高匹配度页面) ---")
            print(txt[:3000])
