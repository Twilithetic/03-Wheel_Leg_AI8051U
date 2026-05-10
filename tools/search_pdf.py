# -*- coding: utf-8 -*-
"""搜索 USB 2.0 PDF 中包含 HID、CDC、Device Class 的页面"""
import pdfplumber
import os

pdf_path = os.path.join(os.path.dirname(__file__), "..", "docs", "USB 2.0 协议usb_20.pdf")
pdf_path = os.path.normpath(pdf_path)

with pdfplumber.open(pdf_path) as pdf:
    print(f"=== 总页数: {len(pdf.pages)} ===\n")
    
    keywords = ["HID", "CDC", "Device Class", "Human Interface", "Communication Device", 
                "class code", "bDeviceClass", "Interface Descriptor"]
    
    found_pages = []
    for i in range(len(pdf.pages)):
        page = pdf.pages[i]
        text = page.extract_text()
        if text:
            for kw in keywords:
                if kw.lower() in text.lower():
                    found_pages.append((i+1, kw, text[:500]))
                    break
    
    print(f"=== 找到 {len(found_pages)} 个匹配页面 ===\n")
    for pg, kw, snippet in found_pages[:20]:
        print(f"\n--- Page {pg} (匹配: {kw}) ---")
        print(snippet[:300])
        print("...")
