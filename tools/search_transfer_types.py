# -*- coding: utf-8 -*-
"""读取 USB 2.0 规范中 Interrupt Transfer 和 Bulk Transfer 章节"""
from pypdf import PdfReader

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\USB 2.0 协议usb_20.pdf"
reader = PdfReader(pdf_path)

# 先搜 "Interrupt Transfer" 和 "Bulk Transfer" 在哪些页
print("=== 搜索 Interrupt Transfer 关键页面 ===")
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text and ("Interrupt Transfer" in text or "Bulk Transfer" in text):
        # 看是否是章节标题
        if "5.6" in text or "5.7" in text or "5.8" in text:
            print(f"  Page {i+1}: 找到章节标题")
        elif "Interrupt" in text[:200] or "Bulk" in text[:200]:
            print(f"  Page {i+1}: 可能相关")

print("\n=== 章节 5.6-5.8 详细内容 ===")
# 读取关键页面
for pg in range(68, 85):  # 大约 Ch5 后半部分
    page = reader.pages[pg - 1]
    text = page.extract_text()
    if text and ("5.6" in text[:200] or "5.7" in text[:200] or "5.8" in text[:200] 
                 or "Interrupt" in text[:300] or "Bulk" in text[:300]):
        print(f"\n--- Page {pg} ---")
        print(text[:1500])
        print("...")
