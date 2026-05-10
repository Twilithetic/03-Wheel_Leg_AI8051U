# -*- coding: utf-8 -*-
"""读取 Intel 80251 编程指南中 SFR 空间和地址空间章节"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_Intel_80251_TSC80251_编程指南.pdf"
reader = PdfReader(pdf_path)

# 读 Chapter 3 (Address Spaces) 对应的大致页面范围
for pg in [17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30, 31, 32, 33]:
    page = reader.pages[pg - 1]
    text = page.extract_text()
    if text:
        print(f"\n{'='*70}")
        print(f"=== Page {pg} ===")
        print(f"{'='*70}")
        # 只显示前800字符+后200字符
        if len(text) > 1000:
            print(text[:800])
            print("...")
            print(text[-300:])
        else:
            print(text)
