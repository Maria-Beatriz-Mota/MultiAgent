@echo off
echo Reiniciando servidor API...
echo.

REM Matar processos Node.js na porta 3001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
    taskkill /PID %%a /F 2>nul
)

timeout /t 2 /nobreak >nul

REM Iniciar servidor
cd /d "%~dp0"
start "API IRIS" cmd /k "npm start"

echo.
echo Servidor reiniciado!
echo Aguarde alguns segundos...
timeout /t 3
