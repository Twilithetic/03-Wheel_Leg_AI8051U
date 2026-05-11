# =============================================================================
#  AI8051U FOC 项目 Makefile
#  =============================================================================
#  用法:
#    make            — 编译 + 链接 (默认)
#    make all        — 同上
#    make compile    — 仅编译 C → OBJ
#    make link       — 仅链接 OBJ + LIB → HEX
#    make clean      — 清理构建产物
#    make rebuild    — 清理 + 重新构建
#    make flash      — 烧录 HEX 到芯片
#    make info       — 显示项目信息
#
#  前提:
#    - Keil C251 安装在 C:\Keil_v5\C251\
#    - GNU Make (mingw32-make 或 MSYS2 make)
# =============================================================================

# =========================== 工具链 ===========================

C251       = C:\Keil_v5\C251\BIN\C251.EXE
L251       = C:\Keil_v5\C251\BIN\L251.EXE

# =========================== 目录 ===========================

SRC_DIR   = Sources
INC_DIR   = Sources\inc
LIB_DIR   = Sources\lib
BUILD_DIR = Objects

# =========================== 源文件 ===========================
# 所有 .c 源文件
C_SOURCES  = $(wildcard $(SRC_DIR)\*.c)

# 目标文件列表（.c → .obj）
OBJS      = $(patsubst $(SRC_DIR)\\%.c,$(BUILD_DIR)\\%.obj,$(C_SOURCES))

# =========================== 库文件 ===========================
# 当前使用 CDC 库（USB 虚拟串口模式）
USB_LIB   = $(LIB_DIR)\stc_usb_cdc_32g_xdata.LIB
# 如需 HID 模式，改为:
# USB_LIB   = $(LIB_DIR)\stc_usb_hid_32g_xdata.LIB
MDU_LIB   = $(LIB_DIR)\ai8051u_32_mdu32.lib
TFPU_LIB  = $(LIB_DIR)\ai8051u_32_tfpu.lib

# =========================== 输出 ===========================

TARGET    = $(BUILD_DIR)\03-March_Wheel_leg_FOC.hex

# =========================== 链接辅助 ===========================
# 把所有 .obj + .lib 拼成逗号分隔的字符串（L251 要求逗号分隔）
comma := ,
empty :=
space := $(empty) $(empty)
ALL_FILES = $(subst $(space),$(comma),$(OBJS) $(USB_LIB) $(MDU_LIB) $(TFPU_LIB))
LINK_OPTS = REMOVEUNUSED NOOVERLAY

# =========================== 编译选项 ===========================

# C251 系统头文件路径（STC 官方芯片头文件，已复制到本地）
STC_INC   = $(SRC_DIR)\inc\stc

# C251 编译标志（必须和 Keil 工程一致！）
#   LARGE            — LARGE 内存模型
#   ROM(LARGE)       — 16MB ROM 空间
#   INTVECTOR(0xFF0000) — 中断向量基址 = FF:0000
#   INTERRUPT(4)     — 🔑 中断帧 4 字节（和库匹配！）
#   DEBUG            — 包含调试信息
#   SYMBOLS          — 生成符号表
C251_FLAGS = LARGE INTERRUPT(4) DEBUG SYMBOLS INCDIR($(INC_DIR)) INCDIR($(STC_INC))

# =========================== 目标 ===========================

.PHONY: all compile link clean rebuild flash info

# ---- 默认目标 ----
all: build

# ---- 构建 ----
build: $(TARGET)
	@echo ✅ 构建完成: $(TARGET)

# ---- 编译 C → OBJ ----
# 模式规则: build\xxx.obj ← Sources\xxx.c
$(BUILD_DIR)\\%.obj: $(SRC_DIR)\\%.c | _ensure_build_dir
	@echo 🔨 编译 $< ...
	$(C251) $< $(C251_FLAGS) OBJECT($@) PRINT(Listings\\$*.lst)

# 确保 build 目录和 listings 目录存在
.PHONY: _ensure_build_dir
_ensure_build_dir:
	@if not exist $(BUILD_DIR) mkdir $(BUILD_DIR)
	@if not exist Listings mkdir Listings

# ---- 链接 OBJ + LIB → HEX ----
$(TARGET): $(OBJS) $(USB_LIB) $(MDU_LIB) $(TFPU_LIB)
	@echo 🔗 链接...
	$(L251) $(ALL_FILES) $(LINK_OPTS) TO $@
	@echo ✅ 链接完成: $@

# ---- 仅编译 ----
compile: $(OBJS)
	@echo ✅ 编译完成

# ---- 仅链接 ----
link: $(OBJS)
	@echo 🔗 链接...
	$(L251) $(ALL_FILES) $(LINK_OPTS) TO $(TARGET)
	@echo ✅ 链接完成: $(TARGET)

# ---- 清理 ----
clean:
	@echo 🧹 清理构建产物...
	@if exist $(BUILD_DIR)\*.obj del /q $(BUILD_DIR)\*.obj
	@if exist $(BUILD_DIR)\*.hex del /q $(BUILD_DIR)\*.hex
	@if exist $(BUILD_DIR)\*.map del /q $(BUILD_DIR)\*.map
	@if exist $(BUILD_DIR)\*.m51 del /q $(BUILD_DIR)\*.m51
	@if exist $(BUILD_DIR)\*.lst del /q $(BUILD_DIR)\*.lst
	@if exist Listings\*.lst del /q Listings\*.lst
	@if exist Listings\*.map del /q Listings\*.map
	@echo ✅ 清理完成

# ---- 重建 ----
rebuild: clean build

# ---- 烧录 ----
flash: $(TARGET)
	@echo 🔥 烧录 $(TARGET) ...
	$(ISP_TOOL) /auto $(TARGET)
	@echo ✅ 烧录完成

# ---- 项目信息 ----
info:
	@echo ============================================================
	@echo   AI8051U FOC 项目信息
	@echo ============================================================
	@echo   芯片:     AI8051U (80251 兼容, LQFP48, 36MHz)
	@echo   编译器:   Keil C251 V5
	@echo   源文件:   $(C_SOURCES)
	@echo   库文件:   
	@echo     $(USB_LIB)
	@echo     $(MDU_LIB)
	@echo     $(TFPU_LIB)
	@echo   输出:     $(TARGET)
	@echo   烧录工具: $(ISP_TOOL)
	@echo ============================================================
	@echo   目标:
	@echo     make / all     — 编译 + 链接
	@echo     make compile   — 仅编译
	@echo     make link      — 仅链接
	@echo     make clean     — 清理
	@echo     make rebuild   — 清理 + 重建
	@echo     make flash     — 烧录
	@echo     make info      — 显示此信息
	@echo ============================================================
