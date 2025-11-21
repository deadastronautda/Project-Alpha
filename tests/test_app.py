import pytest
import sys
from pathlib import Path

# Убедитесь, что путь к основному приложению доступен
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import app  # Импортируем ваше основное приложение
except ImportError as e:
    print(f"Ошибка импорта app.py: {e}")
    sys.exit(1)

def test_app_loaded():
    """Простой тест: проверяет, что модуль app загружен."""
    assert app is not None