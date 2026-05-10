# -*- coding: utf-8 -*-
"""读取 USB 2.0 协议 PDF"""
import pdfplumber
import os

pdf_path = os.path.join(os.path.dirname(__file__), "..", "docs", "USB 2.0 协议usb_20.pdf")
pdf_path = os.path.normpath(pdf_path)

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    print(f"=== PDF 总页数: {total} ===\n")
    
    # 读取前几页,找到目录和关键章节
    for i in range(min(total, 30)):
        page = pdf.pages[i]
        text = page.extract_text()
        if text:
            # 找包含 HID 或 CDC 的页面
            if "HID" in text or "CDC" in text or "Device Class" in text or "设备类" in text or "Human Interface" in text or "Communication" in text:
                print(f"\n--- Page {i+1} ---")
                print(text[:2000])
        elif i < 10:
            print(f"\n--- Page {i+1} (no text, may be image) ---")
