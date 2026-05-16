#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""智能提取 AI8051U 手册中时钟相关内容：
1. 先提取目录页找时钟相关章节
2. 再用二分搜索找到时钟章节的页码范围
3. 最后提取相关内容
"""
import pdfplumber
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    print(f"PDF 总页数: {total}")
    
    # ========== 第一步: 提取前 40 页找目录 ==========
    print("\n" + "="*60)
    print("第一步: 提取前40页寻找目录和时钟章节")
    print("="*60)
    
    toc_entries = []
    for i in range(min(40, total)):
        text = pdf.pages[i].extract_text()
        if text and ("目录" in text or "时钟" in text or "外设" in text or "CLOCK" in text.upper()):
            print(f"\n--- 第 {i+1} 页 ---")
            # 只显示包含关键字的行
            for line in text.split("\n"):
                line_stripped = line.strip()
                if any(kw in line_stripped for kw in ["时钟", "外设", "目录", "CLOCK", "Timer", "定时器", "PCA", "PWM", "SPI", "I2C", "UART", "串口"]):
                    print(f"  {line_stripped}")
                    toc_entries.append((i+1, line_stripped))

    # ========== 第二步: 跳跃搜索时钟相关内容 ==========
    print("\n\n" + "="*60)
    print("第二步: 跳跃搜索'时钟'关键词定位章节")
    print("="*60)
    
    # 以步长50页搜索，快速定位
    clock_pages = []
    for i in range(0, total, 50):
        text = pdf.pages[i].extract_text()
        if text and "时钟" in text:
            # 看这一页的标题
            lines = text.split("\n")
            title_lines = [l.strip() for l in lines[:5] if l.strip()]
            print(f"  第 {i+1} 页: {' | '.join(title_lines[:3])}")
            clock_pages.append(i)
    
    if clock_pages:
        print(f"\n找到 {len(clock_pages)} 个含'时钟'的采样点:")
        first = clock_pages[0] if clock_pages else 0
        last = clock_pages[-1] if clock_pages else total
        
        # 在第一个命中点附近密集搜索
        print(f"\n--- 在首个命中区域 (第{first+1}页附近) 详细提取 ---")
        for i in range(max(0, first-3), min(total, first+20)):
            text = pdf.pages[i].extract_text()
            if text and "时钟" in text:
                print(f"\n>>> 第 {i+1} 页:")
                lines = text.split("\n")
                for line in lines:
                    if "时钟" in line:
                        print(f"  {line.strip()}")

    # ========== 第三步: 提取外设时钟具体配置 ==========
    print("\n\n" + "="*60)
    print("第三步: 搜索外设时钟相关寄存器")
    print("="*60)
    
    for i in range(0, total, 100):
        text = pdf.pages[i].extract_text()
        if text and any(kw in text for kw in ["CLKDIV", "CLKSEL", "SYSCLK", "HSCLK", "外设时钟"]):
            print(f"\n>>> 第 {i+1} 页:")
            lines = text.split("\n")
            for line in lines:
                if any(kw in line for kw in ["CLKDIV", "CLKSEL", "SYSCLK", "HSCLK", "外设时钟", "时钟源", "分频"]):
                    print(f"  {line.strip()}")
