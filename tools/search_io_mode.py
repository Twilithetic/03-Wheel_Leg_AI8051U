# -*- coding: utf-8 -*-
"""搜索 AI8051U 手册中 I/O 端口模式的说明"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"
reader = PdfReader(pdf_path)

# 搜索 I/O 模式相关的页面
for i in range(min(len(reader.pages), 200)):
    page = reader.pages[i]
    text = page.extract_text()
    if text and ("准双向口" in text or "推挽输出" in text or "高阻输入" in text or "开漏输出" in text):
        # 只打印包含模式说明的段落
        for kw in ["准双向口", "推挽输出", "高阻输入", "开漏输出", "PxM1", "PxM0"]:
            if kw in text:
                idx = text.find(kw)
                start = max(0, idx - 100)
                end = min(len(text), idx + 300)
                snippet = text[start:end]
                print(f"Page {i+1}: ...{snippet}...")
                break
