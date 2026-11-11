$dir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$desk = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell
foreach ($old in @('클로드 회사.lnk', '클로드 작업장.lnk')) { $o = Join-Path $desk $old; if (Test-Path $o) { Remove-Item $o } }
$lnk = $ws.CreateShortcut((Join-Path $desk '알들 컴퍼니.lnk'))
$lnk.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
$lnk.Arguments = '"' + (Join-Path $dir '클로드회사_켜기.vbs') + '"'
$lnk.WorkingDirectory = $dir
$lnk.IconLocation = (Join-Path $dir 'ui\icon.ico') + ',0'
$lnk.Description = '알들 컴퍼니 (클로드 작업장 포함)'
$lnk.Save()
Write-Host '  바탕화면에 「알들 컴퍼니」 아이콘을 만들었어요.'
