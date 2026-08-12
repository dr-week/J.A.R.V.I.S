from importlib import reload


def test_litellm_config_contract(monkeypatch):
    monkeypatch.setenv("JARVIS_LLM_PROVIDER", "litellm")
    monkeypatch.setenv("JARVIS_LITELLM_BASE_URL", "http://127.0.0.1:4000/v1")
    monkeypatch.setenv("JARVIS_LITELLM_MODEL", "gemini-2.0-flash")
    monkeypatch.setenv("JARVIS_LITELLM_API_KEY", "sk-test")

    import backend.app.config as config_module

    config = reload(config_module)

    assert config.LLM_PROVIDER == "litellm"
    assert config.LITELLM_BASE_URL == "http://127.0.0.1:4000/v1"
    assert config.LITELLM_MODEL == "gemini-2.0-flash"
    assert config.LITELLM_API_KEY == "sk-test"
    assert config.llm_ready() is True
