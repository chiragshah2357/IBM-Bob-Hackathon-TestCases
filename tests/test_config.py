import logging
from collections.abc import Iterator
from dataclasses import FrozenInstanceError, fields

import pytest

from taskboard.config import Settings, configure_logging, get_export_token, load_settings

SPEC_DEFAULTS = Settings(
    db_path="taskboard.db",
    log_level="INFO",
    export_url="https://hooks.example.com/taskboard",
)


@pytest.fixture
def taskboard_logger() -> Iterator[logging.Logger]:
    package_logger = logging.getLogger("taskboard")
    original_level = package_logger.level
    yield package_logger
    package_logger.setLevel(original_level)


def test_settings_has_exactly_the_ticket_fields():
    assert [f.name for f in fields(Settings)] == ["db_path", "log_level", "export_url"]


def test_settings_is_frozen():
    settings = Settings(db_path="a.db", log_level="INFO", export_url="https://example.com")
    with pytest.raises(FrozenInstanceError):
        settings.db_path = "b.db"


def test_settings_upper_cases_log_level():
    settings = Settings(db_path="a.db", log_level="warning", export_url="https://example.com")
    assert settings.log_level == "WARNING"


def test_settings_rejects_unknown_log_level():
    with pytest.raises(ValueError):
        Settings(db_path="a.db", log_level="verbose", export_url="https://example.com")


def test_load_settings_empty_mapping_uses_spec_defaults():
    assert load_settings({}) == SPEC_DEFAULTS


def test_load_settings_empty_mapping_ignores_process_environment(monkeypatch):
    monkeypatch.setenv("TASKBOARD_DB_PATH", "from-os.db")
    monkeypatch.setenv("TASKBOARD_LOG_LEVEL", "DEBUG")
    assert load_settings({}) == SPEC_DEFAULTS


def test_load_settings_reads_every_variable():
    env = {
        "TASKBOARD_DB_PATH": "/data/tasks.db",
        "TASKBOARD_LOG_LEVEL": "DEBUG",
        "TASKBOARD_EXPORT_URL": "https://hooks.internal.test/export",
    }
    assert load_settings(env) == Settings(
        db_path="/data/tasks.db",
        log_level="DEBUG",
        export_url="https://hooks.internal.test/export",
    )


def test_load_settings_ignores_unrelated_variables():
    env = {"TASKBOARD_DB_PATHS": "other.db", "LOG_LEVEL": "DEBUG", "PATH": "/usr/bin"}
    assert load_settings(env) == SPEC_DEFAULTS


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("debug", "DEBUG"),
        ("Info", "INFO"),
        ("WARNING", "WARNING"),
        ("eRRoR", "ERROR"),
    ],
)
def test_load_settings_log_level_is_case_insensitive(raw, expected):
    assert load_settings({"TASKBOARD_LOG_LEVEL": raw}).log_level == expected


@pytest.mark.parametrize("raw", ["", "verbose", "WARN", "CRITICAL", "info!", "10"])
def test_load_settings_rejects_invalid_log_level(raw):
    with pytest.raises(ValueError, match="TASKBOARD_LOG_LEVEL"):
        load_settings({"TASKBOARD_LOG_LEVEL": raw})


def test_load_settings_defaults_to_os_environ(monkeypatch):
    monkeypatch.setenv("TASKBOARD_DB_PATH", "env.db")
    monkeypatch.setenv("TASKBOARD_LOG_LEVEL", "error")
    monkeypatch.delenv("TASKBOARD_EXPORT_URL", raising=False)
    assert load_settings() == Settings(
        db_path="env.db",
        log_level="ERROR",
        export_url="https://hooks.example.com/taskboard",
    )


def test_load_settings_os_environ_without_variables_uses_defaults(monkeypatch):
    for name in ("TASKBOARD_DB_PATH", "TASKBOARD_LOG_LEVEL", "TASKBOARD_EXPORT_URL"):
        monkeypatch.delenv(name, raising=False)
    assert load_settings() == SPEC_DEFAULTS


def test_get_export_token_reads_mapping():
    assert get_export_token({"TASKBOARD_EXPORT_TOKEN": "test-token-123"}) == "test-token-123"


def test_get_export_token_strips_surrounding_whitespace():
    assert get_export_token({"TASKBOARD_EXPORT_TOKEN": "  test-token-123\n"}) == "test-token-123"


def test_get_export_token_defaults_to_os_environ(monkeypatch):
    monkeypatch.setenv("TASKBOARD_EXPORT_TOKEN", "env-token")
    assert get_export_token() == "env-token"


def test_get_export_token_prefers_explicit_mapping(monkeypatch):
    monkeypatch.setenv("TASKBOARD_EXPORT_TOKEN", "env-token")
    assert get_export_token({"TASKBOARD_EXPORT_TOKEN": "mapping-token"}) == "mapping-token"


def test_get_export_token_is_not_logged(caplog):
    with caplog.at_level(logging.DEBUG, logger="taskboard"):
        get_export_token({"TASKBOARD_EXPORT_TOKEN": "test-token-123"})
    assert "test-token-123" not in caplog.text


@pytest.mark.parametrize(
    ("level_name", "level"),
    [
        ("DEBUG", logging.DEBUG),
        ("info", logging.INFO),
        ("Warning", logging.WARNING),
        ("ERROR", logging.ERROR),
    ],
)
def test_configure_logging_sets_package_logger_level(taskboard_logger, level_name, level):
    configure_logging(load_settings({"TASKBOARD_LOG_LEVEL": level_name}))
    assert taskboard_logger.level == level


def test_configure_logging_applies_to_child_loggers(taskboard_logger):
    configure_logging(load_settings({"TASKBOARD_LOG_LEVEL": "warning"}))
    assert logging.getLogger("taskboard.service").getEffectiveLevel() == logging.WARNING


def test_configure_logging_leaves_root_logger_alone(taskboard_logger):
    root_level = logging.getLogger().level
    configure_logging(load_settings({"TASKBOARD_LOG_LEVEL": "DEBUG"}))
    assert logging.getLogger().level == root_level
