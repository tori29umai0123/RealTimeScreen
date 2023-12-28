# RealTimeSketchの更新 PowerShell スクリプト

# スクリプトのあるディレクトリに移動
Set-Location $PSScriptRoot

# 更新の確認
Write-Host ""
Write-Host "■ RealTimeSketchの更新 ■"
Write-Host ""
$selected = Read-Host "実行しますか？ [YES/Y] (settings.ini はsettings.ini.oldとしてバックアップされます)"
if ($selected -eq "YES" -or $selected -eq "Y") {
    # 仮想環境の有無をチェックし、存在しない場合は作成
    if (-not (Test-Path -Path "venv")) {
        Write-Host "venv フォルダが存在しません。仮想環境を作成します..."
        python -m venv venv
    }

    # 仮想環境を有効にする
    .\venv\Scripts\Activate

    # settings.ini をバックアップまたは削除
    if (Test-Path -Path "settings.ini") {
        Write-Host "settings.ini をバックアップ (settings.ini.old) します..."
        Rename-Item -Path "settings.ini" -NewName "settings.ini.old"
    } else {
        Write-Host "settings.ini は存在しません。"
    }

    Write-Host "リポジトリを更新します..."
    git pull https://github.com/tori29umai0123/RealTimeScreen.git

    Write-Host "torch をインストールします..."
    pip install torch==2.1.1+cu121 torchvision==0.16.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
    pip install --no-deps xformers==0.0.23

    Write-Host "StreamDiffusion をインストールします..."
    pip install git+https://github.com/cumulo-autumn/StreamDiffusion.git@main#egg=streamdiffusion[tensorrt]

    pip install --pre --extra-index-url https://pypi.nvidia.com tensorrt==9.2.0.post12.dev5 --no-cache-dir

    pip install polygraphy==0.47.1 --extra-index-url https://pypi.ngc.nvidia.com

    pip install onnx-graphsurgeon==0.3.26 --extra-index-url https://pypi.ngc.nvidia.com

    pip uninstall -y nvidia-cudnn-cu12

    Write-Host "依存関係をインストールします..."
    pip install --upgrade -r requirements.txt

    Write-Host "benchmark.py を実行します..."
    python benchmark.py --acceleration tensorrt

    Write-Host "更新が完了しました。続行するには何かキーを押してください..."
    $null = Read-Host
} else {
    Write-Host "更新をキャンセルしました。"
}

