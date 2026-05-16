#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查 PDF 页数 - 超小脚本"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
