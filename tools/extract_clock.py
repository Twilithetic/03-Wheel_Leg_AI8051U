# -*- coding: utf-8 -*-
"""从 AI8051U 手册提取时钟管理章节"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pypdf import PdfReader

pdf_path = r"D:\Learning-STC\test_8051_STC\docs\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)

# 时钟管理章节: PDF 539-560页 (手册第8章, 内部页码 500-520)
for page_num in range(538, min(560, len(reader.pages))):
    text = reader.pages[page_num].extract_text()
    if not text:
        continue
    
    print(f"\n{'='*60}")
    print(f"  PDF第{page_num+1}页")
    print(f"{'='*60}")
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # 跳过页首页脚
        skip = (
            line.startswith('Ai8051U') or
            line.startswith('深圳国芯') or
            line.startswith('官方网站') or
            (line.startswith('- ') and line.endswith(' -')) or
            len(line) < 3
        )
        if not skip:
            print(line[:300])
