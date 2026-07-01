@echo off
cd /d "C:\Users\ArjanFaberVAR\Desktop\AI-Agent\F2\F2-Sporting_Regulations_Bot"

:loop
python3 ./regulations_f2.py
timeout /t 120 /nobreak >nul
goto loop