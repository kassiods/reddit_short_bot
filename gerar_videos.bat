REM ===================================
REM SCRIPT WINDOWS - GERAR VIDEOS
REM ===================================
REM Duplo clique neste arquivo para gerar videos automaticamente

@echo off
title Reddit Shorts Bot - Gerador de Videos
color 0A

echo.
echo ==========================================
echo    REDDIT SHORTS BOT - MODO BATCH
echo ==========================================
echo.
echo Quantos videos deseja gerar?
echo.
echo [1] 1 video (teste rapido)
echo [2] 3 videos
echo [3] 5 videos
echo [4] 10 videos
echo.
set /p opcao="Escolha (1-4): "

if "%opcao%"=="1" set quantidade=1
if "%opcao%"=="2" set quantidade=3
if "%opcao%"=="3" set quantidade=5
if "%opcao%"=="4" set quantidade=10

echo.
echo Gerando %quantidade% video(s)...
echo.

cd /d "%~dp0"
python main.py %quantidade%

echo.
echo ==========================================
echo Videos gerados com sucesso!
echo Verifique a pasta: assets\output\
echo ==========================================
echo.
pause
