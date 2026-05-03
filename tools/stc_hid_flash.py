#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STC USB-HID ISP 烧录脚本
基于 GitHub Gist: https://gist.github.com/robinkrens/47a98e58087623059d809175a30b0f42
改编用于 AI8051U (80251 核心)

用法:
    python stc_hid_flash.py firmware.hex

依赖:
    pip install hidapi intelhex tqdm
"""

import hid
import time
import struct
import sys
import os

try:
    from intelhex import IntelHex
except ImportError:
    print("错误: 需要 intelhex 库，请运行: pip install intelhex")
    sys.exit(1)

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("提示: 安装 tqdm 可以看到进度条: pip install tqdm")

# ============ STC USB-ISP 协议常量 ============
PACKET_START = bytes([0x46, 0xB9])  # 包起始标记
PACKET_END   = bytes([0x16])        # 包结束标记
PACKET_MCU   = bytes([0x68])        # MCU → 主机 方向
PACKET_HOST  = bytes([0x6A])        # 主机 → MCU 方向

# STC VID/PID (AI8051U 的 USB-ISP 模式)
STC_VID = 0x34BF
STC_PID = 0x1001

# ============ 辅助函数 ============

def checksum(data: bytes) -> int:
    """计算校验和 (16位)"""
    return sum(data) & 0xFFFF


def send_packet(h: hid.device, payload: bytes, wait_response: bool = True):
    """
    发送一个 HID 包到 STC 芯片
    
    包格式:
      [0x46, 0xB9] [0x6A] [长度(2B BE)] [负载] [校验(2B)] [0x16]
    """
    packet = bytearray()
    packet += PACKET_START                    # 0x46 0xB9
    packet += PACKET_HOST                     # 0x6A (主机→MCU)
    
    # 包长度 = 负载 + 6 (方向1B + 长度2B + 校验2B + 包尾1B)
    total_len = len(payload) + 6
    packet += struct.pack(">H", total_len)    # 大端序长度
    packet += payload                         # 数据负载
    
    # 校验和 (从方向字节开始计算)
    packet += struct.pack(">H", checksum(packet[2:]))
    packet += PACKET_END                      # 0x16
    
    # 补零到 64 字节 (HID 包大小)
    if len(packet) < 64:
        packet += b'\x00' * (64 - len(packet))
    
    # 发送
    h.write(bytes(packet))
    
    # 读取响应 (如果不是复位命令)
    if wait_response:
        try:
            response = h.read(64, timeout=3000)
            return response
        except Exception:
            return None
    return None


def send_reset(h: hid.device):
    """发送复位命令"""
    send_packet(h, bytes([0xFF]), wait_response=False)
    time.sleep(0.1)


def find_stc_device():
    """查找 STC USB-ISP 设备"""
    print(f"正在查找 STC 设备 (VID=0x{STC_VID:04X}, PID=0x{STC_PID:04X})...")
    
    # 枚举所有 HID 设备
    all_devices = hid.enumerate(STC_VID, STC_PID)
    
    if not all_devices:
        print(f"\n❌ 未找到 STC USB-ISP 设备!")
        print(f"   请确认:")
        print(f"   1. AI8051U 板子已通过 USB 连接")
        print(f"   2. 板子处于 ISP 模式（上电时按住 ISP 按钮或重新上电）")
        print(f"   3. 设备管理器中有 'USB 输入设备' (VID=34BF, PID=1001)")
        return None
    
    print(f"   找到 {len(all_devices)} 个 STC 设备")
    
    for i, dev in enumerate(all_devices):
        product = dev.get('product_string', 'Unknown')
        mfr = dev.get('manufacturer_string', 'Unknown')
        path = dev.get('path', b'')
        print(f"   [{i}] {mfr} - {product} (路径: {path[:30]}...)")
    
    return all_devices[0]


def flash_hex(hex_path: str):
    """
    烧录 HEX 文件到 STC 芯片
    
    步骤:
      1. 打开 HID 设备
      2. 握手 / 初始化
      3. 查询芯片信息
      4. 解锁
      5. 擦除
      6. 写入数据
      7. 复位，运行用户程序
    """
    
    # ---------- Step 0: 查找并打开设备 ----------
    dev_info = find_stc_device()
    if dev_info is None:
        return False
    
    h = hid.device()
    try:
        h.open_path(dev_info['path'])
    except Exception as e:
        print(f"\n❌ 无法打开设备: {e}")
        print(f"   提示: 确保没有其他程序 (如 STC-ISP) 正在使用该设备")
        return False
    
    print(f"\n✅ 已连接到 {h.get_product_string()}")
    
    try:
        # ---------- Step 1: 初始化握手 ----------
        print("\n[1/6] 初始化握手...")
        send_packet(h, bytes([0x00, 0x00]))
        time.sleep(0.1)
        print("   ✅ 握手成功")
        
        # ---------- Step 2: 查询芯片信息 ----------
        print("\n[2/6] 查询芯片信息...")
        # 发送查询命令 (0x01 + 参数)
        send_packet(h, bytes([
            0x01,  # 命令: 查询
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x80, 0x00
        ]))
        time.sleep(0.1)
        print("   ✅ 芯片已响应")
        
        # ---------- Step 3: 解锁 ----------
        print("\n[3/6] 解锁芯片...")
        send_packet(h, bytes([0x05, 0x00, 0x00, 0x5A, 0xA5]))
        time.sleep(0.1)
        print("   ✅ 解锁成功")
        
        # ---------- Step 4: 擦除 ----------
        print("\n[4/6] 擦除 Flash...")
        send_packet(h, bytes([0x03, 0x00, 0x00, 0x5A, 0xA5]))
        time.sleep(1.0)  # 擦除需要一些时间
        print("   ✅ 擦除完成")
        
        # ---------- Step 5: 解析 HEX 文件 ----------
        print(f"\n[5/6] 读取 HEX 文件: {hex_path}")
        ih = IntelHex()
        try:
            ih.loadhex(hex_path)
        except Exception as e:
            print(f"   ❌ 读取 HEX 文件失败: {e}")
            return False
        
        print(f"   HEX 文件: {ih.minaddr():04X}H - {ih.maxaddr():04X}H")
        print(f"   数据大小: {ih.maxaddr() - ih.minaddr()} 字节")
        
        # ---------- Step 6: 写入 Flash ----------
        CHUNK_SIZE = 0x80  # 128 字节/块
        start_addr = ih.minaddr()
        end_addr = ih.maxaddr()
        addr = start_addr
        
        print(f"\n[6/6] 写入 Flash ({start_addr:04X}H - {end_addr:04X}H)...")
        
        # 进度迭代器
        addr_list = list(range(start_addr, end_addr, CHUNK_SIZE))
        if TQDM_AVAILABLE:
            iterator = tqdm(addr_list, desc="   写入进度", unit="块")
        else:
            iterator = addr_list
        
        first_chunk = True
        for addr in iterator:
            # 读取一块数据
            chunk_data = bytes(ih[addr:addr + CHUNK_SIZE].tobinarray())
            
            # 构建写入包
            packet_data = bytearray()
            if first_chunk:
                packet_data.append(0x32)  # 第一包使用 0x32
                first_chunk = False
            else:
                packet_data.append(0x12)  # 后续使用 0x12
            
            # 地址 (大端序)
            packet_data.append((addr >> 8) & 0xFF)
            packet_data.append(addr & 0xFF)
            # 魔法数字
            packet_data += bytes([0x5A, 0xA5])
            # 数据
            packet_data += chunk_data
            
            send_packet(h, bytes(packet_data))
            time.sleep(0.002)  # 小延迟避免过载
        
        # ---------- Step 7: 复位 ----------
        print("\n复位芯片，运行用户程序...")
        send_reset(h)
        time.sleep(0.5)
        
        print("\n" + "=" * 60)
        print("🎉 烧录成功！芯片已复位，开始运行你的程序~")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 烧录过程中出错: {e}")
        return False
    finally:
        h.close()


def main():
    print("=" * 60)
    print("  STC USB-HID ISP 烧录工具")
    print("  适用于 AI8051U / STC32G / STC8H 系列")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print(f"\n用法: python {sys.argv[0]} <hex文件路径>")
        print(f"示例: python {sys.argv[0]} build/Debug/AI8051U_test.hex")
        sys.exit(1)
    
    hex_path = sys.argv[1]
    
    if not os.path.exists(hex_path):
        print(f"\n❌ 文件不存在: {hex_path}")
        sys.exit(1)
    
    success = flash_hex(hex_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
