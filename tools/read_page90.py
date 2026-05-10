# -*- coding: utf-8 -*-
"""读取 USB 2.0 Page 90 和周边页面"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\USB 2.0 协议usb_20.pdf"
reader = PdfReader(pdf_path)

for pg in [88, 89, 90, 91, 92]:
    page = reader.pages[pg - 1]
    text = page.extract_text()
    if text:
        print(f"\n{'='*70}")
        print(f"=== Page {pg} ===")
        print(f"{'='*70}")
        print(text[:1500])
        if len(text) > 1500:
            print(f"\n... (truncated, total {len(text)} chars)")
