# build_exe.ps1
# 用于将 convnew/main.py 打包为 Windows 可执行文件（.exe）
# 需先安装 pyinstaller：pip install pyinstaller

$ErrorActionPreference = 'Stop'

# 1. 检查 pyinstaller 是否已安装
if (-not (pip show pyinstaller 2>$null)) {
    Write-Host "PyInstaller 未安装，正在安装..."
    pip install pyinstaller
}

# 2. 执行打包
pyinstaller --onefile --name convert_main .\convnew\main.py

Write-Host "打包完成，生成的 exe 文件在 dist 目录下。"
