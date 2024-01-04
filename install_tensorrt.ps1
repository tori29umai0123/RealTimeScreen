Set-Location $PSScriptRoot

$Env:PIP_DISABLE_PIP_VERSION_CHECK = 1

if (!(Test-Path -Path "venv")) {
    Write-Output  "create python venv..."
    python -m venv venv
}
.\venv\Scripts\activate

Write-Output "Installing torch..."

pip install torch==2.1.1+cu121 torchvision==0.16.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
pip install --no-deps xformers==0.0.23

Write-Output "Installing StreamDiffusion..."

pip install git+https://github.com/cumulo-autumn/StreamDiffusion.git@main#egg=streamdiffusion[tensorrt]

pip install --pre --extra-index-url https://pypi.nvidia.com tensorrt==9.2.0.post12.dev5 --no-cache-dir

pip install polygraphy==0.47.1 --extra-index-url https://pypi.ngc.nvidia.com

pip install onnx-graphsurgeon==0.3.26 --extra-index-url https://pypi.ngc.nvidia.com

pip uninstall -y nvidia-cudnn-cu12

Write-Output "Installing deps..."
pip install --upgrade -r requirements.txt

python utils/benchmark.py --acceleration tensorrt

Write-Output "Install completed"
Read-Host | Out-Null ;