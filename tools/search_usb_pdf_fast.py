# -*- coding: utf-8 -*-
"""用 pypdf 快速搜索 USB 2.0 规范 PDF 中 HID/CDC/Device Class 相关页面"""
import sys
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\USB 2.0 协议usb_20.pdf"

reader = PdfReader(pdf_path)
total = len(reader.pages)
print(f"总页数: {total}")

# 搜索关键词（不区分大小写）
keywords = ["HID", "CDC", "Device Class", "Human Interface", "Communication Device Class",
            "class code", "bDeviceClass", "0x03", "0x02", "Interface Descriptor",
            "Device Descriptor", "HID class", "vendor-specific", "class-specific"]

found = []
for i in range(total):
    page = reader.pages[i]
    text = page.extract_text()
    if not text:
        continue
    text_upper = text.upper()
    for kw in keywords:
        if kw.upper() in text_upper:
            found.append((i+1, kw))
            break

print(f"\n找到 {len(found)} 个相关页面")
for pg, kw in found:
    print(f"  Page {pg}: 匹配 '{kw}'")

# 打印前几个匹配页面的内容片段
print("\n" + "="*60)
for pg, kw in found[:10]:
    page = reader.pages[pg-1]
    text = page.extract_text()
    # 找到关键词附近的文本
    idx = text.upper().find(kw.upper())
    start = max(0, idx - 200)
    end = min(len(text), idx + 800)
    snippet = text[start:end]
    print(f"\n--- Page {pg} (匹配: {kw}) ---")
    print(snippet[:1000])
    print("...")
