@echo off
cd /d "C:\Users\ArjanFaberVAR\Desktop\AI-Agent\F2\F2-General-LLM"

:loop
python3 ./general_f2_bot.py
timeout /t 120 /nobreak >nul
goto loop