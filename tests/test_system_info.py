from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from ergenos_welcome.system_info import (
    is_live_environment,
    parse_os_release,
    read_system_info,
)


class SystemInfoTests(TestCase):
    def test_os_release_parser_handles_quotes_and_comments(self) -> None:
        values = parse_os_release('NAME="ErgenOS"\n# comment\nBUILD_ID=0.2.0-alpha\n')
        self.assertEqual(values["NAME"], "ErgenOS")
        self.assertEqual(values["BUILD_ID"], "0.2.0-alpha")

    def test_system_information_is_loaded(self) -> None:
        content = """PRETTY_NAME="ErgenOS Linux"
VERSION="0.2.0 Alpha (ItWontBootXD)"
BUILD_ID="0.2.0-alpha"
VARIANT="Alpha"
"""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "os-release"
            path.write_text(content, encoding="utf-8")
            info = read_system_info(path)
        self.assertEqual(info.name, "ErgenOS Linux")
        self.assertEqual(info.build_id, "0.2.0-alpha")
        self.assertEqual(info.variant, "Alpha")

    def test_live_environment_requires_archiso_and_installer(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run" / "archiso").mkdir(parents=True)
            self.assertFalse(is_live_environment(root))

            installer = root / "usr" / "local" / "bin" / "ergenos-installer"
            installer.parent.mkdir(parents=True)
            installer.touch()
            self.assertTrue(is_live_environment(root))
