"""Read the installed ErgenOS identity without changing the system."""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SystemInfo:
    name: str
    version: str
    build_id: str
    variant: str


def parse_os_release(content: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        try:
            parsed = shlex.split(raw_value, posix=True)
        except ValueError:
            continue
        values[key] = parsed[0] if parsed else ""
    return values


def read_system_info(path: Path = Path("/etc/os-release")) -> SystemInfo:
    try:
        values = parse_os_release(path.read_text(encoding="utf-8"))
    except OSError:
        values = {}

    return SystemInfo(
        name=values.get("PRETTY_NAME", values.get("NAME", "ErgenOS")),
        version=values.get("VERSION", "Development build"),
        build_id=values.get("BUILD_ID", "unknown"),
        variant=values.get("VARIANT", "unknown"),
    )


def is_live_environment(root: Path = Path("/")) -> bool:
    return (root / "run" / "archiso").is_dir() and (
        root / "usr" / "local" / "bin" / "ergenos-installer"
    ).is_file()
