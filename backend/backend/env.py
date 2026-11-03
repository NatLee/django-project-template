"""Typed readers for settings that come from environment variables.

Every value a project needs to change lives in `.env` (see `.env.example`),
so a copy of this template never has to edit code just to get going.
"""

import os

from django.core.exceptions import ImproperlyConfigured

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


def env_str(name: str, default: str | None = None, *, required: bool = False) -> str:
    """Return the variable as text; raise a readable error when a required one is missing."""
    value = os.environ.get(name)
    if value is None or value == "":
        if required:
            raise ImproperlyConfigured(
                f"Environment variable {name} is not set. Copy .env.example to .env and fill it in."
            )
        return "" if default is None else default
    return value


def env_bool(name: str, default: bool = False) -> bool:
    """Accept true/false, yes/no, on/off and 1/0 in any letter case."""
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    lowered = value.strip().lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ImproperlyConfigured(f"Environment variable {name}={value!r} is not a boolean (use true or false).")


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"Environment variable {name}={value!r} is not a whole number.") from exc


def env_list(name: str, default: str = "") -> list[str]:
    """Split a comma-separated variable into a list, dropping empty items."""
    value = os.environ.get(name)
    if value is None:
        value = default
    return [item.strip() for item in value.split(",") if item.strip()]
