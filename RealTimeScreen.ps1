Set-Location $PSScriptRoot

.\venv\Scripts\activate

python "main.py" --acceleration xformers

Read-Host | Out-Null ;