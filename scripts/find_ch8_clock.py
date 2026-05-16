#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""精确定位第8章时钟管理 - 搜索章节标题"""
import pdfplumber
import sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    
    # Search for "时钟管理" or "8 时钟" or "系统时钟控制" across all pages
    # but jump every 5 pages for speed, then refine
    print("=== 搜索第8章'时钟管理'标题 ===")
    
    for i in range(0, total, 5):
        text = pdf.pages[i].extract_text()
        if text and ("时钟管理" in text or "系统时钟控制" in text):
            print(f"\n找到! PDF第 {i+1} 页:")
            lines = text.split("\n")
            for j, line in enumerate(lines[:20]):
                print(f"  [{j}] {line.strip()}")
            
            # Now extract the surrounding pages in detail
            print(f"\n--- 周围页面详细内容 (PDF页 {i-2} 到 {i+30}) ---")
            for p in range(max(0, i-2), min(total, i+35)):
                text2 = pdf.pages[p].extract_text()
                if text2:
                    # Check if this page has clock-related content
                    has_clock = any(kw in text2 for kw in ["CLK", "时钟", "HIRC", "PLL", "CLKDIV", "CLKSEL", "系统时钟", "外设时钟", "主时钟", "分频"])
                    if has_clock:
                        print(f"\n>>> PDF第 {p+1} 页:")
                        for line in text2.split("\n"):
                            stripped = line.strip()
                            if stripped:
                                print(f"  {stripped}")
            break
