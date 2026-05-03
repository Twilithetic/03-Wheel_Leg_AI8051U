# fix_c251_model.ps1
# =============================================================================
# EIDE C251 Model 自动修复脚本
# 每次 EIDE 升级后运行此脚本，自动将 Keil C51 模型替换为 C251 配置
# =============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# =========================== 配置常量 ===========================
$EIDE_EXT_DIR = "$env:USERPROFILE\.vscode\extensions"
$MODEL_FILE   = "8051.keil.model.json"
$MODEL_RELPATH = "res\data\models\$MODEL_FILE"

# =========================== 颜色定义 ===========================

function Write-OK   { Write-Host "  [OK]       " -ForegroundColor Green -NoNewline; Write-Host $args[0] }
function Write-SKIP { Write-Host "  [SKIP]     " -ForegroundColor Yellow -NoNewline; Write-Host $args[0] }
function Write-ERR  { Write-Host "  [ERROR]    " -ForegroundColor Red -NoNewline; Write-Host $args[0] }
function Write-INFO { Write-Host "  [INFO]     " -ForegroundColor Cyan -NoNewline; Write-Host $args[0] }

# =========================== 主逻辑 ===========================

function Fix-C251Model {
    param(
        [string]$ModelPath
    )
    
    $dir = Split-Path $ModelPath -Parent
    $bakPath = Join-Path $dir "$MODEL_FILE.bak"
    
    # ---- Step 1: 读取 JSON ----
    try {
        $jsonStr = Get-Content $ModelPath -Raw -Encoding UTF8
        $model = $jsonStr | ConvertFrom-Json
    }
    catch {
        Write-ERR "无法解析 JSON: $_"
        return $false
    }
    
    # ---- Step 2: 检查是否已经被 hack ----
    if ($model.id -eq "KEIL_C251") {
        Write-SKIP "已经是 C251 版本，跳过"
        return $true
    }
    
    # ---- Step 3: 备份原文件 ----
    try {
        Copy-Item $ModelPath $bakPath -Force
        Write-INFO "已备份原文件 → $MODEL_FILE.bak"
    }
    catch {
        Write-ERR "备份失败: $_"
        return $false
    }
    
    # ---- Step 4: 修改 JSON 对象 ----
    try {
        # 基本属性
        $model.name = "Keil C251 Compiler"
        $model.id   = "KEIL_C251"
        $model.version.matcher = "^(?<name>C251 COMPILER) V(?<version>\\d[\\d\\.]+)"
        
        # 工具路径 (5 个)
        $model.groups.'c/cpp'.$path      = "../C251/BIN/C251"
        $model.groups.asm.$path          = "../C251/BIN/A251"
        $model.groups.linker.$path       = "../C251/BIN/L251"
        $model.groups.'linker-lib'.$path = "../C251/BIN/LIB251"
        
        # HEX 输出工具
        $model.groups.linker.$outputBin[0].toolPath = "../C251/BIN/OH251"
        
        # 修改默认编译选项 (移除 OMF2, TABS(4)，仅保留 CODE, NOCOND, SYMBOLS)
        $model.groups.'c/cpp'.$default = @("CODE", "NOCOND", "SYMBOLS")
        
        # 移除 linker 中的 use-RTX (C251 不支持)
        $model.groups.linker.PSObject.Properties.Remove('use-RTX')
    }
    catch {
        Write-ERR "修改 JSON 对象失败: $_"
        return $false
    }
    
    # ---- Step 5: 写入文件 ----
    try {
        $newJson = $model | ConvertTo-Json -Depth 10
        # 恢复 Unix 风格换行 (ConvertTo-Json 默认用 CRLF)
        Set-Content $ModelPath -Value $newJson -Encoding UTF8 -NoNewline
        Write-OK "已修复 → Keil C251 Compiler"
        return $true
    }
    catch {
        Write-ERR "写入文件失败: $_"
        return $false
    }
}

# =========================== 入口 ===========================

function Main {
    # Clear-Host  # 注释掉，非交互式终端会报错
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  EIDE C251 Model 自动修复脚本" -ForegroundColor Cyan
    Write-Host "  每次 EIDE 升级后运行此脚本一键恢复 C251 编译支持" -ForegroundColor DarkGray
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 检查 EIDE 扩展目录
    if (-not (Test-Path $EIDE_EXT_DIR)) {
        Write-ERR "找不到 EIDE 扩展目录: $EIDE_EXT_DIR"
        Write-Host ""
        Read-Host "按 Enter 退出"
        exit 1
    }
    
    # 查找所有 EIDE 安装
    $eideDirs = Get-ChildItem $EIDE_EXT_DIR -Directory -Filter "cl.eide-*" | Sort-Object Name -Descending
    
    if ($eideDirs.Count -eq 0) {
        Write-ERR "未找到 EIDE 安装 (cl.eide-*)"
        Write-Host ""
        Read-Host "按 Enter 退出"
        exit 1
    }
    
    Write-Host "找到 $($eideDirs.Count) 个 EIDE 安装:" -ForegroundColor White
    Write-Host ""
    
    $fixedCount = 0
    $skipCount  = 0
    $failCount  = 0
    
    foreach ($eideDir in $eideDirs) {
        $version = $eideDir.Name -replace 'cl\.eide-', ''
        $modelPath = Join-Path $eideDir.FullName $MODEL_RELPATH
        
        Write-Host "[$version]" -ForegroundColor White
        
        if (-not (Test-Path $modelPath)) {
            Write-SKIP "未找到 $MODEL_FILE (此版本可能不包含此文件)"
            $skipCount++
            Write-Host ""
            continue
        }
        
        $result = Fix-C251Model -ModelPath $modelPath
        
        if ($result -eq $true) {
            if ((Get-Content $modelPath -Raw) -match "KEIL_C251") {
                $fixedCount++
            }
        }
        else {
            $failCount++
        }
        
        Write-Host ""
    }
    
    # ---- 结果摘要 ----
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  修复完成!" -ForegroundColor Green
    Write-Host "  ✅ 已修复: $fixedCount 个" -ForegroundColor Green
    if ($skipCount -gt 0) {
        Write-Host "  ⏭️  已跳过: $skipCount 个" -ForegroundColor Yellow
    }
    if ($failCount -gt 0) {
        Write-Host "  ❌ 失败:   $failCount 个" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  提示: 在 VSCode 中点击 EIDE 面板的 🔄 刷新按钮即可生效" -ForegroundColor DarkGray
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Read-Host "按 Enter 退出"
}

# 以管理员权限运行时避免工作目录问题
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($scriptDir) {
    Set-Location $scriptDir
}

Main
