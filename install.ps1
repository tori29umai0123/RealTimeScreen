Set-Location $PSScriptRoot

$Env:PIP_DISABLE_PIP_VERSION_CHECK = 1

if (!(Test-Path -Path "venv")) {
    Write-Output  "create python venv..."
    python -m venv venv
}
.\venv\Scripts\activate

python -m pip install pip==23.0.1

pip install torch==2.1.1+cu121 torchvision==0.16.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

pip install --no-deps xformers==0.0.23

Write-Output "Installing deps..."

python pip install git+https://github.com/cumulo-autumn/StreamDiffusion.git@main#egg=streamdiffusion[tensorrt]

pip install --pre tensorrt --extra-index-url https://pypi.nvidia.com

pip install pywin32 -i https://mirror.baidu.com/pypi/simple

Write-Output "Installing deps..."
pip install --upgrade -r requirements.txt

pip install accelerate

Write-Output "Install completed"
Read-Host | Out-Null ;

