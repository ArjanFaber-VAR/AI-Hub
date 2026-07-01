@echo off
cd /d "C:\Users\ArjanFaberVAR\Desktop\AI-Agent\Calendar-Tool\"

:loop
python3 ./calendar-tool.py
timeout /t 120 /nobreak >nul
goto loop