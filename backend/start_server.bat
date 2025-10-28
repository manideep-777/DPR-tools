@echo off
cd /d "D:\msme hackathon\backend"
call venv\Scripts\activate.bat
echo Starting FastAPI Server...
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
