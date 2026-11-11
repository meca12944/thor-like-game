@echo off
chcp 65001 >nul
title 클로드 작업장 - 처음 설치
cd /d "%~dp0"
echo.
echo  ===== 클로드 작업장 처음 설치 =====
echo  필요한 프로그램을 차례로 깔아요. 중간에 "예"를 눌러 주세요.
echo.
where winget >nul 2>nul || (echo  winget 이 없어요. Microsoft Store 에서 "앱 설치 관리자"를 업데이트한 뒤 다시 해 주세요. & pause & exit /b)

echo [1/5] Node.js (회사 본체를 돌리는 프로그램)
where node >nul 2>nul && (echo   이미 있어요.) || winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements

echo [2/5] Git (게임 파일 관리, 클로드 코드에도 필요)
where git >nul 2>nul && (echo   이미 있어요.) || winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements

echo [3/5] 클로드 코드 (직원)
where claude >nul 2>nul && (echo   이미 있어요.) || powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://claude.ai/install.ps1 | iex"

echo [4/5] 게임 원본 폴더
set "GITEXE=git"
where git >nul 2>nul || set "GITEXE=%ProgramFiles%\Git\cmd\git.exe"
if exist "%USERPROFILE%\thor-like-game\.git" (
  echo   이미 있어요: %USERPROFILE%\thor-like-game
) else (
  choice /c YN /m "  게임 저장소를 %USERPROFILE%\thor-like-game 에 받을까요? (2GB 정도, 시간이 걸려요)"
  if not errorlevel 2 "%GITEXE%" clone https://github.com/meca12944/thor-like-game "%USERPROFILE%\thor-like-game"
)

echo [5/5] 바탕화면 아이콘
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\make_shortcut.ps1"

echo.
echo  이제 새 창이 열리면 클로드 코드에 로그인해 주세요 (지금 쓰는 구독 계정).
echo  로그인이 끝나면 그 창은 닫아도 돼요.
pause
start "" powershell -NoExit -NoProfile -Command "$env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')+';'+$env:USERPROFILE+'\.local\bin'; claude"
echo.
echo  다 됐어요! 바탕화면의 「클로드 작업장」 아이콘을 두 번 누르면 회사가 열려요.
echo  (아이콘이 안 열리면 PC를 한 번 다시 켜 주세요.)
pause
