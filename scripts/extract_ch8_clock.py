#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""提取 AI8051U 第8章 时钟管理 详细内容 (约500-530页)"""
import pdfplumber
import sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    
    # Based on TOC, chapter 8 starts around page 500
    # Let's extract pages 499-530 (0-indexed: 498-529)
    # Also include some peripheral-specific clock pages
    target_pages = list(range(498, 530))  # pages 499-530 (chapter 8)
    
    print("="*80)
    print("=== AI8051U 时钟管理系统 - 第8章详细内容 ===")
    print("="*80)
    
    for i in target_pages:
        if i >= total:
            break
        text = pdf.pages[i].extract_text()
        if text and ("时钟" in text or "CLK" in text.upper() or "寄存器" in text or "CLKDIV" in text or "CLKSEL" in text):
            print(f"\n{'='*80}")
            print(f"第 {i+1} 页")
            print(f"{'='*80}")
            # Print all text but skip empty lines
            for line in text.split("\n"):
                stripped = line.strip()
                if stripped:
                    print(f"  {stripped}")
    
    # Also extract specific peripheral clock pages
    # Page 511 has SPI_CLKDIV, PWMA_CLKDIV, PWMB_CLKDIV, TFPU_CLKDIV, I2S_CLKDIV
    # Page 510 has HSCLKDIV
    # Let's get page 510-513 specifically
    print("\n\n" + "="*80)
    print("=== 外设时钟分频寄存器详解 (510-513页) ===")
    print("="*80)
    
    for i in [509, 510, 511, 512]:  # pages 510-513
        if i < total:
            text = pdf.pages[i].extract_text()
            if text:
                print(f"\n--- 第 {i+1} 页 ---")
                for line in text.split("\n"):
                    stripped = line.strip()
                    if stripped:
                        print(f"  {stripped}")
