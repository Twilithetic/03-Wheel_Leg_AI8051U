# -*- coding: utf-8 -*-
"""从 AI8051U 手册提取仿真/调试章节"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pypdf import PdfReader

reader = PdfReader(r"D:\Learning-STC\test_8051_STC\docs\资料_芯片外设_AI8051U芯片手册.pdf")

# 仿真章节: 88-92, 195-200
for page_num in [195,196,197,198,199,200]:
    text = reader.pages[page_num-1].extract_text()
    if not text: continue
    print(f"\n{'='*60}")
    print(f"  PDF第{page_num}页")
    print(f"{'='*60}")
    for line in text.split('\n'):
        line = line.strip()
        if len(line) > 3 and 'Ai8051U' not in line[:10] and '深圳国芯' not in line:
            print(line[:300])
