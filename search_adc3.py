#!/usr/bin/env python3
"""搜索 ADC 相关 DMA 和 AMT 的内容"""
import sys, re
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

reader = PdfReader(pdf_path)
total = len(reader.pages)

# 精确搜索 ADC 相关关键词
keywords = [
    r'DMA_ADC', r'ADC_DMA', r'ADC.*AMT', r'AMT.*ADC',
    r'ADC.*传输总字节', r'ADC.*循环', r'ADC.*绕回',
    r'ADC_CFG', r'ADC_CR', r'ADC_STA', r'ADC_AMT',
    r'ADC.*自动', r'ADC.*DMA',
]

print("搜索 ADC DMA/AMT 相关内容...")
print("=" * 80)

found_pages = set()
for i in range(total):
    text = reader.pages[i].extract_text() or ""
    for kw in keywords:
        if re.search(kw, text, re.IGNORECASE):
            found_pages.add(i+1)

print(f"找到相关页面: {sorted(found_pages)}")
print()

# 提取这些页面的详细内容
for pg in sorted(found_pages):
    text = reader.pages[pg - 1].extract_text() or ""
    print(f"\n{'='*70}")
    print(f"📍 第 {pg} 页")
    print(f"{'='*70}")
    
    lines = text.split('\n')
    for j, line in enumerate(lines):
        for kw in keywords:
            if re.search(kw, line, re.IGNORECASE):
                # 打印上下文
                for k in range(max(0, j-3), min(len(lines), j+4)):
                    marker = " → " if k == j else "   "
                    print(f"{marker}{lines[k].strip()}")
                print()
                break

# 如果没找到，搜索整个 ADC 章节
if not found_pages:
    print("\n未找到 ADC DMA，搜索整个 ADC 章节...")
    for i in range(total):
        text = reader.pages[i].extract_text() or ""
        if re.search(r'(第\s*\d+\s*章.*ADC|ADC.*模数转换器)', text, re.IGNORECASE):
            print(f"\n找到 ADC 章节标题在第 {i+1} 页:")
            for line in text.split('\n')[:15]:
                print(f"  {line.strip()}")
            break
