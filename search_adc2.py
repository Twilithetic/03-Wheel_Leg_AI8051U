#!/usr/bin/env python3
"""快速搜索 AI8051U 芯片手册中 ADC AMT 循环相关内容 - 用 pypdf 加速"""
import sys
import re

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

from pypdf import PdfReader
reader = PdfReader(pdf_path)
total = len(reader.pages)
print(f"总页数: {total}")

# 找 ADC 相关页面
adc_pages = []
for i in range(total):
    text = reader.pages[i].extract_text() or ""
    if re.search(r'(第\s*\d+\s*章|CHAPTER)\s*.*(ADC|模数|A/D)', text, re.IGNORECASE):
        for line in text.split('\n'):
            if re.search(r'(ADC|模数|A/D)', line, re.IGNORECASE) and len(line) > 5:
                print(f"  [{i+1}] {line.strip()[:100]}")
                adc_pages.append(i)
                break
    if i % 100 == 0:
        print(f"  扫描中... {i}/{total}", end='\r', file=sys.stderr)

print(f"\n\n找到 {len(adc_pages)} 个 ADC 相关页面")

# 集中搜索 ADC 附近页面的 AMT/循环内容
search_start = max(0, adc_pages[0] - 5) if adc_pages else 0
search_end = min(total, adc_pages[-1] + 50) if adc_pages else total
print(f"搜索范围: 第 {search_start+1} - {search_end} 页")

found_any = False
for i in range(search_start, search_end):
    text = reader.pages[i].extract_text() or ""
    if re.search(r'(AMT|自动循环|循环模式|绕回|循环缓冲|wrap|circular|重装载|起始地址)', text, re.IGNORECASE):
        found_any = True
        print(f"\n{'='*70}")
        print(f"📍 第 {i+1} 页")
        print(f"{'='*70}")
        # 打印匹配行及其上下文
        lines = text.split('\n')
        for j, line in enumerate(lines):
            if re.search(r'(AMT|自动循环|循环模式|绕回|循环缓冲|wrap|circular|重装载|起始地址|0[xX]?[fF]{4}|DMA|XDATA)', line, re.IGNORECASE):
                for k in range(max(0, j-2), min(len(lines), j+3)):
                    marker = " → " if k == j else "   "
                    print(f"{marker}{lines[k].strip()}")
                print()

if not found_any:
    print("未找到 ADC 章节中的 AMT/循环相关内容，扩大搜索...")
    for i in range(total):
        text = reader.pages[i].extract_text() or ""
        if re.search(r'(AMT|自动循环|绕回)', text, re.IGNORECASE):
            print(f"\n  第 {i+1} 页有 AMT/循环 关键词")
