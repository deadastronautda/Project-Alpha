@echo off
echo 🧪 Запуск тестов...
call venv\Scripts\activate.bat
pytest --verbose tests/
echo 📊 Тесты завершены
pause