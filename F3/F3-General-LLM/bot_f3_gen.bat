@echo off
cd /d "C:\Users\ArjanFaberVAR\OneDrive - Van Amersfoort Racing B.V\Regulations-VAR - Documenten"

:loop
python ./scanner.py
timeout /t 10 /nobreak >nul
goto loop