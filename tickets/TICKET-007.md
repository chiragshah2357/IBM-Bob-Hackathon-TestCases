# TICKET-007: Settings from environment

## Summary

Centralize configuration in `taskboard/config.py`.

## Acceptance criteria

- Frozen dataclass `Settings(db_path: str, log_level: str, export_url: str)`.
- `load_settings(env: Mapping[str, str] | None = None) -> Settings` (defaults to `os.environ`) using the variables and defaults in SPEC §4. `log_level` is validated and stored upper-case; invalid → `ValueError`.
- `get_export_token(env: Mapping[str, str] | None = None) -> str` reads `TASKBOARD_EXPORT_TOKEN`; missing or empty raises `RuntimeError` with a helpful message.
- No token values anywhere in source code (SPEC §4).
- `configure_logging(settings: Settings) -> None` applies the log level to the `taskboard` logger.
- Tests included.
