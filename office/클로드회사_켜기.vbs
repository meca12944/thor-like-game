Option Explicit
' 클로드 회사 켜기: 본체를 조용히(검은 창 없이) 켜고, 회사 창을 앱처럼 연다.
Dim sh, fso, dir, rc
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = dir
rc = sh.Run("cmd /c where node >nul 2>nul", 0, True)
If rc <> 0 Then
  MsgBox "Node.js 가 없어요. 「처음_설치.bat」 을 먼저 두 번 눌러 주세요.", 48, "클로드 회사"
  WScript.Quit
End If
If Not fso.FolderExists(dir & "\data") Then fso.CreateFolder(dir & "\data")
sh.Run "cmd /c node server.js >> data\server.log 2>&1", 0, False
WScript.Sleep 1500
sh.Run "cmd /c start """" msedge --app=http://127.0.0.1:7788 --window-size=1600,900", 0, False
