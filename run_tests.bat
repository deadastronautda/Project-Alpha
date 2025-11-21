@echo off
echo 🧪 Запуск тестов...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if exist requirements_test.txt pip install -r requirements_test.txt
pytest --verbose tests/
echo 📊 Тесты завершены
pause