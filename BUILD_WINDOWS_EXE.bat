@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>&1
if errorlevel 1 (
  echo Python 3 is required to build Alphabetic Keyboarding Revived.
  echo Download Python from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)
%PY% -m unittest discover -p "test_*.py" -v
if errorlevel 1 goto failed
%PY% -m pip install pyinstaller
if errorlevel 1 goto failed
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name AlphabeticKeyboardingRevived --version-file version_info.txt --icon app_icon.ico --add-data "app_icon.ico;." --add-data "app_icon.png;." --add-data "splash.png;." app.py
if errorlevel 1 goto failed
echo.
echo Build created: dist\AlphabeticKeyboardingRevived.exe
pause
exit /b 0
:failed
echo Build failed. Read errors above for details.
pause
exit /b 1
