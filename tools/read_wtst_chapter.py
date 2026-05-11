# -*- coding: utf-8 -*-
"""搜索 AI8051U 手册中 复位、PC、启动流程、WTST 详细说明"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)

# 找 WTST 详细章节（12.1.1 附近，约 580 页）
for pg in [579, 580, 581, 582, 583, 584, 585]:
    page = reader.pages[pg - 1]
    text = page.extract_text()
    if text:
        print(f"\n{'='*70}")
        print(f"=== Page {pg} ===")
        print(f"{'='*70}")
        print(text[:1500])
        if len(text) > 1500:
            print(f"\n... (total {len(text)} chars)")
