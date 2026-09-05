from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from ergenos_welcome.settings import (
    autostart_enabled,
    first_run_completed,
    set_autostart_enabled,
    set_first_run_completed,
    should_autostart,
)


class SettingsTests(TestCase):
    def test_first_login_is_enabled_by_default(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            self.assertTrue(autostart_enabled(path))
            self.assertFalse(first_run_completed(path))
            self.assertTrue(should_autostart(path))

    def test_autostart_choice_is_persisted(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            set_autostart_enabled(False, path)
            self.assertFalse(autostart_enabled(path))
            set_autostart_enabled(True, path)
            self.assertTrue(autostart_enabled(path))

    def test_completed_first_run_disables_default_autostart(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            set_first_run_completed(True, path)
            self.assertTrue(first_run_completed(path))
            set_autostart_enabled(False, path)
            self.assertFalse(should_autostart(path))

    def test_login_preference_preserves_first_run_state(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            set_first_run_completed(True, path)
            set_autostart_enabled(True, path)
            self.assertTrue(first_run_completed(path))
            self.assertTrue(should_autostart(path))
