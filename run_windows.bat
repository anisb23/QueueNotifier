@echo off
cd /d "%~dp0companion"
pip install -r requirements.txt -q
python main.py
pause
