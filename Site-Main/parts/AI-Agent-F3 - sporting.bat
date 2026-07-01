@echo off
cd /d "C:\Users\ArjanFaberVAR\Desktop\AI-Agent\F3\F3-Sporting_Regulations_Bot"

:loop
python3 ./regulations_f3.py
timeout /t 120 /nobreak >nul
goto loop