#!/usr/bin/env python3
"""精确提取第 1537-1550 页 ADC DMA 相关完整内容"""
import re
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)

# 打印第 1537 到 1550 页的完整文本（ADC_DMA 章节）
for pg in range(1536, 1555):  # 0-indexed, 1537-1555
    text = reader.pages[pg].extract_text() or ""
    print(f"\n{'#'*70}")
    print(f"### 第 {pg+1} 页 ###")
    print(f"{'#'*70}")
    print(text)
    print()
