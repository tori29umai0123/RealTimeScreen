Set-Location $PSScriptRoot

.\venv\Scripts\activate

python "RealTimeScreen.py" --acceleration xformers

Read-Host | Out-Null ;