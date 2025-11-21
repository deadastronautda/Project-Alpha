@echo off
call venv\Scripts\activate

pytest --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing

pause
