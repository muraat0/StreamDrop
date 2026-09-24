@echo off
title Video Indirici Baslatici
chcp 65001 >nul
cls

:: Scriptin bulundugu klasore kilitlen (Bosluklu yollar ve dosya bulma icin sart)
cd /d "%~dp0"

echo ===================================================
echo        EVRENSEL VIDEO INDIRICI BASLATILIYOR
echo ===================================================
echo.

echo [1/3] Kutuphaneler kontrol ediliyor...
python -m pip install --upgrade yt-dlp >nul 2>&1

echo [2/3] Tarayici baslatma gorevi hazirlaniyor...
:: Sunucu ayaga kalkarken arka planda 2 saniye bekleyip tarayiciyi acar
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080"

echo [3/3] Sunucu 8080 portunda calisiyor...
echo Kapatmak icin bu pencereyi kapatabilir veya Ctrl+C yapabilirsiniz.
echo.
python "server.py"

pause