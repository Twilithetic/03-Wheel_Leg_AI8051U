# -*- coding: utf-8 -*-
"""搜索 AI8051U 手册中 WTST 相关内容"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)

for i in range(min(len(reader.pages), 300)):
    page = reader.pages[i]
    text = page.extract_text()
    if text and ("WTST" in text or "等待时间" in text or "程序代码等待" in text):
        idx = text.find("WTST" if "WTST" in text else "等待时间" if "等待时间" in text else "程序代码等待")
        start = max(0, idx - 200)
        end = min(len(text), idx + 500)
        print(f"\n--- Page {i+1} ---")
        print(text[start:end])
        print()
