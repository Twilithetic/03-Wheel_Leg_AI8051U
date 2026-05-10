# -*- coding: utf-8 -*-
"""读取 AI8051U 手册第 12.2.12 节 EAXFR 使用说明 (大约 580-600 页)"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)

# 搜索 580-610 页中关于 EAXFR/XFR 的详细内容
for pg in range(585, 610):
    page = reader.pages[pg - 1]
    text = page.extract_text()
    if text and ("EAXFR" in text or "XFR" in text or "扩展" in text or "7efe" in text.lower()):
        print(f"\n{'='*70}")
        print(f"=== Page {pg} ===")
        print(f"{'='*70}")
        print(text[:2000])
        if len(text) > 2000:
            print(f"\n... (total {len(text)} chars)")
