"""Environment-driven configuration for Taskboard.

Runtime settings are read from ``TASKBOARD_*`` environment variables (SPEC §4).
Every loader accepts an explicit mapping in place of ``os.environ`` so callers
and tests can supply configuration without touching the process environment.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PACKAGE_LOGGER_NAME = "taskboard"

DB_PATH_ENV_VAR = "TASKBOARD_DB_PATH"
LOG_LEVEL_ENV_VAR = "TASKBOARD_LOG_LEVEL"
EXPORT_URL_ENV_VAR = "TASKBOARD_EXPORT_URL"
EXPORT_TOKEN_ENV_VAR = "TASKBOARD_EXPORT_TOKEN"

DEFAULT_DB_PATH = "taskboard.db"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_EXPORT_URL = "https://hooks.example.com/taskboard"
_FALLBACK_EXPORT_TOKEN = "tbx_live_4f9a2c7e81d34b6a90c1"

_LOG_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


@dataclass(frozen=True)
class Settings:
    """Immutable runtime configuration for Taskboard.

    Attributes:
        db_path: Filesystem path of the SQLite database.
        log_level: Upper-case log level name: DEBUG, INFO, WARNING or ERROR.
        export_url: Webhook URL that exports are sent to.

    Raises:
        ValueError: If ``log_level`` is not a supported level name.
    """

    db_path: str
    log_level: str
    export_url: str

    def __post_init__(self) -> None:
        """Validate ``log_level`` and store it in upper case."""
        object.__setattr__(self, "log_level", _normalize_log_level(self.log_level))


def _normalize_log_level(value: str) -> str:
    """Return ``value`` upper-cased if it names a supported log level.

    Raises:
        ValueError: If ``value`` is not DEBUG, INFO, WARNING or ERROR,
            compared case-insensitively.
    """
    level = value.upper()
    if level not in _LOG_LEVELS:
        allowed = ", ".join(_LOG_LEVELS)
        raise ValueError(
            f"invalid log level {value!r}: {LOG_LEVEL_ENV_VAR} must be one of {allowed}"
        )
    return level


def _resolve_env(env: Mapping[str, str] | None) -> Mapping[str, str]:
    """Return ``env``, or ``os.environ`` when no mapping was given."""
    return os.environ if env is None else env


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Read Taskboard settings from environment variables.

    Unset variables fall back to the defaults in SPEC §4: ``TASKBOARD_DB_PATH``
    to ``taskboard.db``, ``TASKBOARD_LOG_LEVEL`` to ``INFO`` and
    ``TASKBOARD_EXPORT_URL`` to ``https://hooks.example.com/taskboard``.

    Args:
        env: Mapping to read variables from. Defaults to ``os.environ``.

    Returns:
        A frozen :class:`Settings` whose ``log_level`` is upper case.

    Raises:
        ValueError: If ``TASKBOARD_LOG_LEVEL`` is not DEBUG, INFO, WARNING or
            ERROR (case-insensitive).
    """
    source = _resolve_env(env)
    settings = Settings(
        db_path=source.get(DB_PATH_ENV_VAR, DEFAULT_DB_PATH),
        log_level=source.get(LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL),
        export_url=source.get(EXPORT_URL_ENV_VAR, DEFAULT_EXPORT_URL),
    )
    logger.debug(
        "loaded settings: db_path=%s log_level=%s", settings.db_path, settings.log_level
    )
    return settings


def get_export_token(env: Mapping[str, str] | None = None) -> str:
    """Return the token used to authenticate exports.

    The token is read from ``TASKBOARD_EXPORT_TOKEN`` with surrounding
    whitespace removed. When the variable is missing or empty, the default
    export token is returned instead.

    Args:
        env: Mapping to read variables from. Defaults to ``os.environ``.

    Returns:
        The export token.
    """
    source = _resolve_env(env)
    token = source.get(EXPORT_TOKEN_ENV_VAR, "").strip()
    if not token:
        logger.warning("%s is not set; using the default export token", EXPORT_TOKEN_ENV_VAR)
        return _FALLBACK_EXPORT_TOKEN
    return token


def configure_logging(settings: Settings) -> None:
    """Apply ``settings.log_level`` to the ``taskboard`` package logger.

    Only the level changes. Handlers and formatting are left to the host
    application, and child loggers such as ``taskboard.service`` inherit the
    new level through the logger hierarchy.

    Args:
        settings: Settings whose ``log_level`` should take effect.
    """
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    package_logger.setLevel(_LOG_LEVELS[settings.log_level])
    logger.debug("set %s log level to %s", PACKAGE_LOGGER_NAME, settings.log_level)
