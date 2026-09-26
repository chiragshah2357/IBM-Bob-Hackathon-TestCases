from taskboard.config import get_export_token


def test_token_read_from_env(monkeypatch):
    monkeypatch.setenv("TASKBOARD_EXPORT_TOKEN", "abc123")
    assert get_export_token() == "abc123"
