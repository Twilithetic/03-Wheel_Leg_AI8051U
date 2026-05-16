#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""搜索 AI8051U 手册中 ADC 相关内容"""
import pdfplumber, sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\03-March_Wheel_leg\03-Wheel_leg_AI8051U\docs\资料\资料_芯片外设_AI8051U芯片手册.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total = len(pdf.pages)
    
    # 从目录知 ADC 在第23章，约1125页附近
    # 先搜索 "ADC" 标题定位章节首页
    print("=== 第一步：定位 ADC 章节首页 ===")
    adc_start = None
    for i in range(1100, min(1200, total), 1):
        text = pdf.pages[i].extract_text()
        if text and ("ADC" in text or "模数转换" in text or "A/D" in text):
            # 检查是否是章节标题
            if any(hdr in text for hdr in ["23 ", "23.", "ADC控制", "ADC相关", "ADC输入通道", "ADC转换"]):
                print(f"找到ADC内容在第 {i+1} 页")
                adc_start = i
                break
    
    if adc_start is None:
        # 扩大搜索
        for i in range(0, total, 10):
            text = pdf.pages[i].extract_text()
            if text and "ADC输入通道" in text:
                adc_start = i
                print(f"找到ADC在第 {i+1} 页")
                break
    
    # 第二步：提取 ADC 相关页面
    if adc_start:
        print(f"\n=== 第二步：提取 ADC 详细内容 (第{adc_start+1}页起) ===")
        for p in range(max(0, adc_start-2), min(total, adc_start+40)):
            text = pdf.pages[p].extract_text()
            if text:
                has_adc = any(kw in text for kw in [
                    "ADC", "A/D", "模数", "通道", "CHS", "ADC_CONTR",
                    "ADCTIM", "ADCCFG", "ADC_POWER", "ADC_EPWMT",
                    "ADC输入", "ADC速度", "ADC_RES"
                ])
                if has_adc:
                    print(f"\n{'='*80}")
                    print(f"PDF第 {p+1} 页")
                    print(f"{'='*80}")
                    for line in text.split("\n"):
                        s = line.strip()
                        if s:
                            print(f"  {s}")
    else:
        # 没找到，用步进搜索
        print("\n=== 步进搜索 ADC 关键词 ===")
        for i in range(0, total, 50):
            text = pdf.pages[i].extract_text()
            if text and "ADC" in text:
                # 找章节标题
                lines = text.split("\n")
                for line in lines[:5]:
                    if "ADC" in line:
                        print(f"  第{i+1}页: {line.strip()}")
                        break
