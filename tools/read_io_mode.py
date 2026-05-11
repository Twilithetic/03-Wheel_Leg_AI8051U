# -*- coding: utf-8 -*-
from pypdf import PdfReader
r = PdfReader(r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf")
for pg in range(648, 660):
    text = r.pages[pg-1].extract_text()
    if text:
        print(f"=== Page {pg} ===")
        print(text[:1500])
        print()
