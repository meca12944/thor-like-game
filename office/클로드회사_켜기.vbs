Option Explicit
' 클로드 작업장 켜기: 본체를 조용히(검은 창 없이) 켜고, 문이 열릴 때까지 기다렸다가 창을 앱처럼 연다.
Dim sh, fso, dir, rc, http, i, ready
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = dir
rc = sh.Run("cmd /c where node >nul 2>nul", 0, True)
If rc <> 0 Then
  MsgBox "Node.js 가 없어요. 「처음_설치.bat」 을 먼저 두 번 눌러 주세요." & vbCrLf & "(설치했는데도 이 창이 뜨면 PC 를 한 번 다시 켜 주세요.)", 48, "클로드 작업장"
  WScript.Quit
End If
If Not fso.FolderExists(dir & "\data") Then fso.CreateFolder(dir & "\data")
sh.Run "cmd /c node server.js >> data\server.log 2>&1", 0, False
ready = False
For i = 1 To 60
  WScript.Sleep 500
  On Error Resume Next
  Set http = CreateObject("MSXML2.ServerXMLHTTP")
  http.open "GET", "http://127.0.0.1:7788/api/state", False
  http.send
  If Err.Number = 0 Then
    If http.status = 200 Then ready = True
  End If
  Err.Clear
  On Error GoTo 0
  If ready Then Exit For
Next
If Not ready Then
  MsgBox "작업장 본체가 켜지지 않았어요." & vbCrLf & "폴더 안 data\server.log 를 메모장으로 열어 사진을 보내 주세요.", 48, "클로드 작업장"
  sh.Run "notepad """ & dir & "\data\server.log""", 1, False
  WScript.Quit
End If
sh.Run "cmd /c start """" msedge --app=http://127.0.0.1:7788 --window-size=1600,900", 0, False
