# -*- coding: utf-8 -*-
"""读取 USB 2.0 规范中关键页面的详细内容"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\USB 2.0 协议usb_20.pdf"
reader = PdfReader(pdf_path)

# 关键页面：设备类概述、描述符、bDeviceClass
key_pages = [50, 51, 52, 66, 67, 436, 437, 438, 439, 440, 441, 442]

for pg in key_pages:
    page = reader.pages[pg - 1]
    text = page.extract_text()
    if text:
        print(f"\n{'='*70}")
        print(f"=== Page {pg} ===")
        print(f"{'='*70}")
        print(text[:2000])
        if len(text) > 2000:
            print(f"\n... (truncated, total {len(text)} chars)")
