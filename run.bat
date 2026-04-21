@echo off
:: FileSage — Windows Launcher
:: Requires Python 3.9+ from python.org or Microsoft Store

echo.
echo ✦ FileSage — AI File Intelligence
echo ──────────────────────────────────

:: ── Find Python ──────────────────────────────────────────────────────────────
set PYTHON=
for %%p in (python3.12 python3.11 python3.10 python3.9 python3 python) do (
    where %%p >nul 2>&1
    if not errorlevel 1 (
        set PYTHON=%%p
        goto :found_python
    )
)

echo ❌  Python 3.9+ not found.
echo     Download from: https://www.python.org/downloads/
echo     Make sure to check "Add Python to PATH" during install.
pause
exit /b 1

:found_python
for /f "tokens=*" %%v in ('%PYTHON% --version 2^>^&1') do echo ✓  %%v

:: ── Virtual environment ───────────────────────────────────────────────────────
set VENV_DIR=%~dp0.venv

if not exist "%VENV_DIR%" (
    echo →  Creating virtual environment...
    %PYTHON% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌  Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set PIP=%VENV_DIR%\Scripts\pip.exe
set PY=%VENV_DIR%\Scripts\python.exe

:: ── Dependencies ──────────────────────────────────────────────────────────────
echo →  Checking dependencies...
"%PIP%" install --quiet --upgrade pip 2>nul
"%PIP%" install --quiet PyQt6 requests 2>nul
echo ✓  Dependencies ready

:: ── Launch ────────────────────────────────────────────────────────────────────
echo →  Launching FileSage...
echo.

set PYTHONWARNINGS=ignore::DeprecationWarning,ignore::UserWarning
"%PY%" -W ignore main.py

if errorlevel 1 (
    echo.
    echo ❌  FileSage exited with an error.
    echo     Check the output above for details.
    pause
)
