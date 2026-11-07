@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Khong tim thay Python. Cai Python 3.11 va chon Add Python to PATH.
  pause
  exit /b 1
)
if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/4] Tao moi truong Python...
  py -3.11 -m venv backend\.venv
  if errorlevel 1 goto failed
)
echo [2/4] Cap nhat pip va cai thu vien co ban...
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
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
goto end
:failed
echo Co loi cai dat. Kiem tra Python 3.11 va ket noi Internet.
pause
:end
endlocal
