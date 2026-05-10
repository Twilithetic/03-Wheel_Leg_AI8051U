# -*- coding: utf-8 -*-
"""搜索 AI8051U 芯片手册前 200 页中 XFR/EAXFR/扩展寄存器"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)
total = len(reader.pages)
print(f"总页数: {total}，只扫描前 200 页")

keywords = ["EAXFR", "P_SW2", "XFR", "扩展", "特殊功能寄存器", "访问使能",
            "SFR", "7EFE", "7efe", "使能访问扩展", "扩展SFR", "扩展RAM管理"]

found = []
for i in range(min(total, 200)):
    page = reader.pages[i]
    text = page.extract_text()
    if text:
        for kw in keywords:
            if kw.lower() in text.lower():
                found.append((i+1, kw, text))
                break

print(f"找到 {len(found)} 个相关页面\n")
for pg, kw, text in found[:30]:
    idx = text.lower().find(kw.lower())
    start = max(0, idx - 200)
    end = min(len(text), idx + 600)
    snippet = text[start:end]
    # 显示中文字符
    print(f"\n--- Page {pg} (匹配: {kw}) ---")
    # 提取关键词附近 3 行
    lines = snippet.split('\n')
    for line in lines:
        if kw.lower() in line.lower() or any(k.lower() in line.lower() for k in keywords[:3]):
            print(f"  >> {line.strip()[:200]}")
    if len(snippet) < 800:
        print(snippet[:600])
    print()
