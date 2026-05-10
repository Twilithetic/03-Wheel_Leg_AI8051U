# -*- coding: utf-8 -*-
"""搜索 AI8051U 芯片手册中 XFR/EAXFR/扩展寄存器相关内容"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)
total = len(reader.pages)
print(f"总页数: {total}")

keywords = ["EAXFR", "P_SW2", "XFR", "扩展", "特殊功能寄存器", "访问使能",
            "SFR", "7EFE", "0x7e", "XFR访问", "扩展RAM", "扩展SFR",
            "IRC32KCR", "IRC48MCR", "USBCLK", "CLKSEL"]

found = []
for i in range(total):
    page = reader.pages[i]
    text = page.extract_text()
    if text:
        for kw in keywords:
            if kw.lower() in text.lower():
                found.append((i+1, kw, text))
                break

print(f"找到 {len(found)} 个相关页面\n")
for pg, kw, text in found:
    idx = text.lower().find(kw.lower())
    start = max(0, idx - 150)
    end = min(len(text), idx + 400)
    snippet = text[start:end].replace('\n', ' ')
    print(f"  Page {pg} (匹配 '{kw}'): {snippet[:500]}")
    print()
