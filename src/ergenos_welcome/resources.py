"""Localized links displayed by ErgenOS Welcome."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


ERGENOS_WEBSITE = "https://ergenossw.github.io/ErgenOS-Website/"
ERGENOS_WIKI = "https://ergenossw.github.io/ErgenOS-Wiki/"
ERGENOS_PROJECT = "https://github.com/ErgenosSW/ErgenOS-Linux"
ERGENOS_BUG_REPORT = ERGENOS_PROJECT + "/issues/new?template=01-bug-report.yml"


@dataclass(frozen=True)
class OnlineResource:
    title: str
    subtitle: str
    uri: str


def preferred_language(language_names: Sequence[str]) -> str:
    """Return the first preferred language, normalized to its language code."""
    for language_name in language_names:
        normalized = language_name.split(".", 1)[0].split("@", 1)[0]
        normalized = normalized.replace("_", "-").lower()
        if normalized in {"c", "posix"}:
            break
        if normalized:
            return normalized.split("-", 1)[0]
    return "en"


def online_resources(language_names: Sequence[str]) -> tuple[OnlineResource, ...]:
    """Build the online-resource list for the preferred desktop language."""
    polish = preferred_language(language_names) == "pl"
    locale_path = "pl/" if polish else ""
    return (
        OnlineResource(
            "Oficjalna strona" if polish else "Official website",
            "Pobieranie systemu i informacje o projekcie"
            if polish
            else "Downloads and project information",
            ERGENOS_WEBSITE + locale_path,
        ),
        OnlineResource(
            "ErgenOS Wiki",
            "Instalacja, obsługa systemu i rozwiązywanie problemów"
            if polish
            else "Installation, system administration and troubleshooting",
            ERGENOS_WIKI + locale_path,
        ),
        OnlineResource(
            "Strona projektu" if polish else "Project page",
            "Kod źródłowy i wydania" if polish else "Source code and releases",
            ERGENOS_PROJECT,
        ),
        OnlineResource(
            "Zgłoś błąd" if polish else "Report a bug",
            "Otwórz formularz zgłoszenia na GitHubie"
            if polish
            else "Open the bug report form on GitHub",
            ERGENOS_BUG_REPORT,
        ),
    )
