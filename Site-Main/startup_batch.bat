@echo off

start "Script f3 page" cmd /k python main_f2.py
start "Script f2 page" cmd /k python main_f3.py
start "Script calendar page" cmd /k python main_calendar.py
start "Script landing page" cmd /k python landing_page.py