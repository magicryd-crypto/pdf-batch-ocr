@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo  PDF OCR: folder input  to  folder output  [.docx]
echo  Robust mode: each volume in its own process.
echo  Threads auto-tuned to free RAM. Done volumes are skipped.
echo  Safe to stop and run again.
echo ============================================================
echo.
"venv\Scripts\python.exe" -u "run_all.py"
echo.
echo Finished. You can close this window.
pause
