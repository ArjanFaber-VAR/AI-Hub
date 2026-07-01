@echo off
cd /d "C:\Users\ArjanFaberVAR\Desktop\AI-Agent\F3\F3-General-LLM"

:loop
python3 ./general_f3_bot.py
timeout /t 120 /nobreak >nul
goto loop