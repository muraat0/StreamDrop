@echo off
title Video Indirici Kurulum
chcp 65001 >nul
cls

echo ===================================================
echo     EVRENSEL VIDEO INDIRICI - KURULUM ARACI
echo ===================================================
echo.

echo [1/2] Python ve pip kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Sisteminizde Python bulunamadi! Lutfen Python yukleyin.
    pause
    exit
)

echo [2/2] requirements.txt üzerinden kutuphaneler yukleniyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ===================================================
echo               KURULUM TAMAMLANDI!
echo ===================================================
echo Artik uygulamayi baslat.bat ile calistirabilirsiniz.
echo.
pause