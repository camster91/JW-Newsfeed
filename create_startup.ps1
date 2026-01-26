$WshShell = New-Object -ComObject WScript.Shell
$StartupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\JW-Newsfeed-Server.lnk"
$Shortcut = $WshShell.CreateShortcut($StartupPath)
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "C:\Users\camst\JW-Newsfeed\start_server.pyw"
$Shortcut.WorkingDirectory = "C:\Users\camst\JW-Newsfeed"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
Write-Host "Startup shortcut created at: $StartupPath"
