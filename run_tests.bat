@echo off
call venv\Scripts\activate

echo Установка пакета в editable-режиме...
pip install -e . --quiet

echo Запуск тестов...
pytest --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing

pause
