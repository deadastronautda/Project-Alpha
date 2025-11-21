@echo off
echo 🧪 Запуск тестов...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if exist requirements-test.txt pip install -r requirements-test.txt
pytest --verbose tests/
echo 📊 Тесты завершены
pause