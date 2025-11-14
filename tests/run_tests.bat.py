@echo off
echo 🧪 Запуск тестов...
pytest --cov=app --cov-report=html tests/
echo 📊 Отчет о покрытии сохранен в htmlcov/index.html
pause