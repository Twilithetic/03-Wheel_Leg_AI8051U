#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""USB 设备树查看器 - 类似 USB Device Tree Viewer"""

import subprocess
import sys
import os

def run_ps(cmd):
    """运行 PowerShell 命令并返回输出"""
    result = subprocess.run(
        ['pwsh.exe', '-NoProfile', '-Command', cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.stdout

def list_usb_devices():
    """列出所有 USB 相关设备"""
    # 使用 WMI 查询 USB 设备
    ps_cmd = """
$devices = Get-CimInstance Win32_PnPEntity | Where-Object { 
    $_.PNPClass -match 'Ports|USB|HIDClass|Net' -or 
    $_.Name -match 'COM|Serial|USB|STC|CH340|CH341|PL230|UART|TTL|HID|CDC|ACM'
}
Write-Host "=== USB/串口/HID 设备列表 ==="
Write-Host ""
$devices | ForEach-Object {
    $status = if ($_.Status -eq 'OK') { '[OK]' } else { '[??]' }
    Write-Host "$status $($_.Name)"
    Write-Host "     类别: $($_.PNPClass)"
    Write-Host "     设备ID: $($_.DeviceID)"
    Write-Host ""
}
"""
    print(run_ps(ps_cmd))

def list_usb_controllers():
    """列出 USB 控制器和集线器"""
    ps_cmd = """
$hubs = Get-CimInstance Win32_USBHub
Write-Host "=== USB 集线器/设备 ==="
Write-Host ""
$hubs | ForEach-Object {
    Write-Host "[$($_.DeviceID)]"
    Write-Host "  $($_.Name) - $($_.Description)"
    Write-Host "  状态: $($_.Status)"
    Write-Host ""
}
"""
    print(run_ps(ps_cmd))

def list_com_ports():
    """列出 COM 端口详情"""
    ps_cmd = """
$ports = Get-CimInstance Win32_SerialPort
Write-Host "=== COM 端口详细 ==="
Write-Host ""
if ($ports) {
    $ports | ForEach-Object {
        Write-Host "[$($_.DeviceID)]"
        Write-Host "  名称: $($_.Name)"
        Write-Host "  描述: $($_.Description)"
        Write-Host "  状态: $($_.Status)"
        Write-Host ""
    }
} else {
    Write-Host "  (无 COM 端口)"
}
"""
    print(run_ps(ps_cmd))

def list_hid_devices():
    """列出 HID 设备"""
    ps_cmd = """
$hids = Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq 'HIDClass' }
Write-Host "=== HID 设备 ==="
Write-Host ""
$hids | ForEach-Object {
    Write-Host "[HID] $($_.Name)"
    Write-Host "  ID: $($_.DeviceID)"
    Write-Host "  状态: $($_.Status)"
    Write-Host ""
}
"""
    print(run_ps(ps_cmd))

def check_driver_info():
    """检查 USB 转串口驱动"""
    print("=== 常见 USB 转串口驱动检查 ===")
    print("")
    
    # 检查是否有设备在"其他设备"中（未安装驱动的）
    ps_cmd = """
$unknown = Get-CimInstance Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 }
if ($unknown) {
    Write-Host "!!! 以下设备可能有驱动问题:"
    $unknown | ForEach-Object {
        Write-Host "  [$($_.ConfigManagerErrorCode)] $($_.Name) - $($_.DeviceID)"
    }
} else {
    Write-Host "  无驱动问题设备"
}
"""
    print(run_ps(ps_cmd))
    
    # 检查 CH340/CH341 驱动
    print("")
    ps_cmd2 = """
$ch340 = Get-CimInstance Win32_PnPSignedDriver | Where-Object { $_.DeviceName -match 'CH34|wch|WCH' }
if ($ch340) {
    Write-Host "CH34x 驱动已安装:"
    $ch340 | ForEach-Object { Write-Host "  $($_.DeviceName) v$($_.DriverVersion)" }
} else {
    Write-Host "CH340/CH341 驱动: 未安装"
}
"""
    print(run_ps(ps_cmd2))

if __name__ == '__main__':
    print("🔍 USB 设备树查看器")
    print("=" * 60)
    print()
    list_usb_devices()
    list_com_ports()
    list_hid_devices()
    check_driver_info()
    print()
    print("=" * 60)
    print("提示：如果 AI8051U 显示为 HID 设备而不是 COM 口，")
    print("需要用 STC-ISP 官方工具烧录（支持 HID/USB 模式）。")
    print("stcflash.py 仅支持 COM 口（UART）烧录。")
