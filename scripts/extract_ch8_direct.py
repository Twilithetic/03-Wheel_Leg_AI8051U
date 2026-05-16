#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接提取第8章时钟管理 (PDF 530-575页)"""
import pdfplumber
import sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    
    # 从TOC已知第8章在手册第500-527页
    # PDF页码大约对应手册页码, 从530开始
    start, end = 529, 580  # 0-indexed
    
    print(f"=== AI8051U 第8章 时钟管理 (PDF第{start+1}-{end}页) ===")
    print("提取条件: 页面包含'时钟'、'CLK'、'分频'、'CLKDIV'、'CLKSEL'、'PLL'等关键词\n")
    
    for i in range(start, min(end, total)):
        text = pdf.pages[i].extract_text()
        if text:
            has_clock = any(kw in text for kw in [
                "时钟", "CLKDIV", "CLKSEL", "PLL时钟", "系统时钟",
                "HIRC", "主时钟", "SYSCLK", "HSCLKDIV", "USBCLK",
                "分频", "振荡", "晶振", "时钟源", "MCLK"
            ])
            if has_clock:
                print(f"\n{'='*80}")
                print(f"PDF第 {i+1} 页")
                print(f"{'='*80}")
                for line in text.split("\n"):
                    stripped = line.strip()
                    if stripped:
                        print(f"  {stripped}")
