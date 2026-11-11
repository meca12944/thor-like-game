$dir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$desk = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $desk '클로드 작업장.lnk'))
$lnk.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
$lnk.Arguments = '"' + (Join-Path $dir '클로드회사_켜기.vbs') + '"'
$lnk.WorkingDirectory = $dir
$lnk.IconLocation = (Join-Path $dir 'ui\icon.ico') + ',0'
$lnk.Description = '클로드 작업장 (게임 필멸자)'
$lnk.Save()
Write-Host '  바탕화면에 「클로드 작업장」 아이콘을 만들었어요.'
