# Move to the directory where the script is located
Set-Location $PSScriptRoot

# Check for updates
Write-Host ""
Write-Host "Å° Updating RealTimeScreen Å°"
Write-Host ""
$selected = Read-Host "Do you want to proceed? [YES/Y] (settings.ini will be backed up as settings.ini.old)"
if ($selected -eq "YES" -or $selected -eq "Y") {
    # Check for the existence of a virtual environment, create one if it doesn't exist
    if (-not (Test-Path -Path "venv")) {
        Write-Host "No venv folder found. Creating a virtual environment..."
        python -m venv venv
    }

    # Activate the virtual environment
    .\venv\Scripts\Activate

    # Backup or delete settings.ini
    if (Test-Path -Path "settings.ini") {
        Write-Host "Backing up settings.ini (to settings.ini.old)..."
        Rename-Item -Path "settings.ini" -NewName "settings.ini.old"
    } else {
        Write-Host "settings.ini does not exist."
    }

    Write-Host "Updating the repository..."
    git pull https://github.com/tori29umai0123/RealTimeScreen.git

    Write-Host "Running install_tensorrt.ps1..."
    .\install_tensorrt.ps1

    Write-Host "Update complete. Press any key to continue..."
    $null = Read-Host
} else {
    Write-Host "Update cancelled."
}
