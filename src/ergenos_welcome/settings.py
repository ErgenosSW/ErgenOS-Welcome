"""Small per-user settings store for ErgenOS Welcome."""

from __future__ import annotations

import configparser
import os
from pathlib import Path


def config_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "ergenos-welcome" / "settings.ini"


def autostart_enabled(path: Path | None = None) -> bool:
    return _read_boolean("launch_at_login", False, path)


def first_run_completed(path: Path | None = None) -> bool:
    return _read_boolean("first_run_completed", False, path)


def should_autostart(path: Path | None = None) -> bool:
    return not first_run_completed(path) or autostart_enabled(path)


def _read_boolean(key: str, fallback: bool, path: Path | None = None) -> bool:
    parser = configparser.ConfigParser()
    target = path or config_path()
    try:
        parser.read(target, encoding="utf-8")
        return parser.getboolean("general", key, fallback=fallback)
    except (OSError, ValueError, configparser.Error):
        return fallback


def set_autostart_enabled(enabled: bool, path: Path | None = None) -> None:
    _write_boolean("launch_at_login", enabled, path)


def set_first_run_completed(completed: bool, path: Path | None = None) -> None:
    _write_boolean("first_run_completed", completed, path)


def _write_boolean(key: str, value: bool, path: Path | None = None) -> None:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    try:
        parser.read(target, encoding="utf-8")
    except (OSError, configparser.Error):
        parser = configparser.ConfigParser()
    if not parser.has_section("general"):
        parser.add_section("general")
    parser.set("general", key, "true" if value else "false")

    temporary = target.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        parser.write(stream)
    temporary.replace(target)
