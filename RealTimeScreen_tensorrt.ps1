Set-Location $PSScriptRoot

.\venv\Scripts\activate

python "main.py" --acceleration tensorrt

Read-Host | Out-Null ;