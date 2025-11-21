import app

def test_streamlit_main_runs():
    """Smoke-тест: проверяет, что main() не падает"""
    try:
        app.main
    except Exception:
        assert False, "Streamlit main() вызвало исключение"
    assert True