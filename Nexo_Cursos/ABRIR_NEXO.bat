@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 iniciar.py
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Instala Python 3.10 ou mais recente e marca Add Python to PATH.
        echo Depois abre este arquivo novamente.
    ) else (
        python iniciar.py
    )
)
pause
