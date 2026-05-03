# -*- coding: utf-8 -*-
"""简单测试：检测 STC HID 设备"""
import hid
import sys

VID = 0x34BF
PID = 0x1001

print(f"Searching STC devices (VID=0x{VID:04X}, PID=0x{PID:04X})...")
devices = hid.enumerate(VID, PID)

if not devices:
    print("NOT FOUND!")
    print("Please check:")
    print("  1. AI8051U board is connected via USB")
    print("  2. Board is in ISP mode (power cycle)")
    sys.exit(1)

print(f"Found {len(devices)} device(s):")
for d in devices:
    print(f"  Product: {d.get('product_string', '?')}")
    print(f"  Manufacturer: {d.get('manufacturer_string', '?')}")
    print(f"  Path: {d.get('path', b'?')!r}")
print("\nDevice detected! Script should work.")
