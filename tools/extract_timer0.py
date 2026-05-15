#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract Timer0 related content from AI8051U manual"""

import sys
import pdfplumber
import re

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = r"docs/资料/资料_芯片外设_AI8051U芯片手册.pdf"
OUTPUT_PATH = r"tools/timer0_extracted.txt"

# Timer0 related keywords - focused on timer registers and control
KEYWORDS = [
    "TMOD", "TCON", "TH0", "TL0",
    "AUXR",
    "T0x12", "T0CLKO", "T0_GAT", "T0_C",
    "GATE", "C/T", "TR0", "TF0", "IE0", "IT0",
    "INT0", "INT1",
    "ET0", "EA", "PT0",  # interrupt
]

# More specific: match only when these appear in timer context
TIMER_SECTION_KEYWORDS = [
    "定时器", "Timer",
]

def is_timer_related(text):
    """Check if text is timer-related"""
    for kw in TIMER_SECTION_KEYWORDS:
        if kw.lower() in text.lower():
            return True
    return False

def main():
    print("Opening PDF...")
    results = []

    with pdfplumber.open(PDF_PATH) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}, scanning...")

        for i, page in enumerate(pdf.pages):
            if i % 100 == 0:
                print(f"  Progress: {i}/{total_pages} pages...")

            text = page.extract_text()
            if text is None:
                continue

            # First check if page is timer related
            if not is_timer_related(text):
                continue

            matched = []
            for kw in KEYWORDS:
                if re.search(re.escape(kw), text, re.IGNORECASE):
                    matched.append(kw)

            if matched:
                results.append((i + 1, matched, text))
                print(f"  [Page {i+1}] matched: {matched}")

    print(f"\nFound {len(results)} timer-related pages.")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("AI8051U Manual - Timer0 Related Pages\n")
        f.write("=" * 70 + "\n\n")

        for page_num, matched, text in results:
            f.write(f"\n{'=' * 70}\n")
            f.write(f"[Page {page_num}] keywords: {matched}\n")
            f.write(f"{'=' * 70}\n")
            f.write(text)
            f.write("\n\n")

    print(f"\nDone! Output: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
