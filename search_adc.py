#!/usr/bin/env python3
"""搜索 AI8051U 芯片手册中 ADC AMT 循环相关的内容"""
import pdfplumber
import re

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

print("=" * 80)
print("开始搜索 ADC + AMT/自动循环 相关内容...")
print("=" * 80)

# 第一步：找到 ADC 章节的页码范围
adc_pages = []
with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"PDF 总页数: {total_pages}")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            # 找 ADC 章节标题页
            if re.search(r'(第\s*\d+\s*章.*ADC|ADC.*转换|模数转换)', text, re.IGNORECASE):
                # 提取标题行
                title_line = ""
                for line in text.split('\n'):
                    if re.search(r'(ADC|模数转换)', line, re.IGNORECASE):
                        title_line = line.strip()
                        break
                print(f"\n📄 第 {i+1} 页: {title_line}")
                adc_pages.append(i+1)
                # 打印该页前200字符
                print(f"   预览: {text[:200]}...")
                print("-" * 40)

print("\n" + "=" * 80)
print("第二步：搜索 AMT / 自动循环 / 绕回 相关内容")
print("=" * 80)

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            # 搜索关键词
            if re.search(r'(AMT|自动循环|循环模式|绕回|循环缓冲|wrap|circular)', text, re.IGNORECASE):
                # 提取相关内容
                lines = text.split('\n')
                matched_lines = []
                for j, line in enumerate(lines):
                    if re.search(r'(AMT|自动循环|循环模式|绕回|循环缓冲|wrap|circular|ADC)', line, re.IGNORECASE):
                        # 包含上下文
                        start = max(0, j-2)
                        end = min(len(lines), j+3)
                        context = '\n'.join(lines[start:end])
                        matched_lines.append(context)
                
                for ctx in matched_lines:
                    print(f"\n--- 第 {i+1} 页 ---")
                    print(ctx)
                    print("-" * 60)
