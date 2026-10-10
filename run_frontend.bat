@echo off
cd /d "%~dp0frontend"
if not exist "node_modules" (
  echo Installing frontend dependencies...
  npm install
)
echo Starting React frontend...
npm run dev
pause
