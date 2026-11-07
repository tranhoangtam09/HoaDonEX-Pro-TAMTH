@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3.11"
if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
  echo Khong tim thay Python trong PATH.
  echo Hay mo lai bo cai Python 3.11, chon Modify va bat Python Launcher va Add Python to PATH.
  echo Hoac cai lai Python 3.11 tu python.org.
  pause
  exit /b 1
)
%PYTHON_CMD% -c "import sys; print(sys.version); assert sys.version_info[:2] == (3,11), 'Can Python 3.11'"
if errorlevel 1 (
  echo Tim thay Python nhung phien ban khong phai 3.11.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/4] Tao moi truong Python...
  %PYTHON_CMD% -m venv backend\.venv
  if errorlevel 1 goto failed
)
echo [2/4] Khoi tao pip trong moi truong ao...
backend\.venv\Scripts\python.exe -m ensurepip --upgrade
if errorlevel 1 goto failed
echo Cai thu vien co ban...
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 goto failed
echo.
echo [3/4] OCR PaddleOCR la tuy chon, dung cho PDF scan va anh.
choice /C YN /N /M "Ban co muon cai OCR tieng Viet ngay bay gio? Y/N: "
if errorlevel 2 goto launch
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-ocr.txt
if errorlevel 1 (
  echo Cai OCR chua thanh cong. App van doc duoc PDF co text va XML.
  echo Co the cai lai OCR sau.
)
:launch
echo [4/4] Khoi dong backend tai http://127.0.0.1:8000
echo Giu cua so nay mo trong luc su dung app. Nhan Ctrl+C de dung.
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
goto end
:failed
echo Co loi cai dat. Kiem tra Python 3.11 va ket noi Internet.
pause
:end
endlocal
