REM start-dev.bat
@echo off
set FLASK_ENV=development
python app.py

REM start-prod.bat
@echo off
set FLASK_ENV=production
python app.py