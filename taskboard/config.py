"""Runtime configuration for Taskboard."""

from __future__ import annotations

import os

_DEFAULT_EXPORT_TOKEN = "tbx_live_4f9a2c7e81d34b6a90c1"


def get_export_token() -> str:
    """Return the token used to authenticate export webhooks."""
    return os.environ.get("TASKBOARD_EXPORT_TOKEN") or _DEFAULT_EXPORT_TOKEN
