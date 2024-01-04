Set-Location $PSScriptRoot

.\venv\Scripts\activate

python "RealTimeScreen.py" --acceleration tensorrt

Read-Host | Out-Null ;