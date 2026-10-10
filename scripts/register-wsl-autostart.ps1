$ErrorActionPreference = 'Stop'

$distro = 'AlmaLinux-10'
$wsl = Join-Path $env:WINDIR 'System32\wsl.exe'
$startup = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startup 'Coffee Deal Observer WSL.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $wsl
$shortcut.Arguments = "-d $distro -u mg --exec /usr/bin/true"
$shortcut.WorkingDirectory = $env:USERPROFILE
$shortcut.Description = 'Starts AlmaLinux WSL so systemd can start Coffee Deal Observer.'
$shortcut.Save()

Write-Host "Created '$shortcutPath' to start $distro at Windows user logon."
