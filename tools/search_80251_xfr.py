# -*- coding: utf-8 -*-
"""搜索 Intel 80251 编程指南和完整手册中 XFR/扩展地址相关内容"""
from pypdf import PdfReader
import os

pdfs = [
    r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_Intel_80251_TSC80251_编程指南.pdf",
    r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_Intel_80251_完整手册.pdf",
]

for pdf_path in pdfs:
    name = os.path.basename(pdf_path)
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    print(f"\n{'='*70}")
    print(f"文件: {name}")
    print(f"总页数: {total}")
    print(f"{'='*70}")
    
    keywords = ["EAXFR", "P_SW2", "XFR", "extended", "SFR", "0xba", "P2SW", 
                "address space", "memory map", "EDATA", "XDATA"]
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
    for pg, kw, text in found[:15]:
        # 找到关键词附近上下文
        idx = text.lower().find(kw.lower())
        start = max(0, idx - 300)
        end = min(len(text), idx + 700)
        snippet = text[start:end].replace('\n', ' ')
        print(f"  Page {pg} (匹配 '{kw}'): {snippet[:400]}...")
        print()
