"""GTK4 and libadwaita interface for ErgenOS Welcome."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk  # noqa: E402

from .settings import (
    autostart_enabled,
    set_autostart_enabled,
    set_first_run_completed,
    should_autostart,
)
from .system_info import is_live_environment, read_system_info


APPLICATION_ID = "io.github.ergenossw.ergenoswelcome"
INSTALLED_LOGO_PATH = Path(
    "/usr/share/icons/hicolor/256x256/apps/io.github.ergenossw.ergenoswelcome.png"
)
SOURCE_LOGO_PATH = Path(__file__).resolve().parents[2] / "data" / (
    "io.github.ergenossw.ergenoswelcome.png"
)


def logo_path() -> Path:
    if INSTALLED_LOGO_PATH.is_file():
        return INSTALLED_LOGO_PATH
    return SOURCE_LOGO_PATH


class WelcomeWindow(Adw.ApplicationWindow):
    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application=application)
        self.set_title("ErgenOS Welcome")
        self.set_default_size(760, 680)
        self.connect("close-request", self._on_close_request)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        self.set_content(toolbar)

        scrolled = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        toolbar.set_content(scrolled)

        clamp = Adw.Clamp(maximum_size=680, tightening_threshold=520)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(32)
        clamp.set_margin_start(18)
        clamp.set_margin_end(18)
        scrolled.set_child(clamp)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(content)

        logo = Gtk.Image.new_from_file(str(logo_path()))
        logo.set_pixel_size(150)
        logo.set_accessible_role(Gtk.AccessibleRole.IMG)
        logo.update_property(
            [Gtk.AccessibleProperty.LABEL],
            ["ErgenOS logo"],
        )
        content.append(logo)

        heading = Gtk.Label(label="Welcome to ErgenOS")
        heading.add_css_class("title-1")
        content.append(heading)

        info = read_system_info()
        version = Gtk.Label(label=info.version)
        version.add_css_class("dim-label")
        content.append(version)

        if is_live_environment():
            install_button = Gtk.Button(label="Install ErgenOS")
            install_button.set_icon_name("system-software-install-symbolic")
            install_button.add_css_class("suggested-action")
            install_button.add_css_class("pill")
            install_button.set_halign(Gtk.Align.CENTER)
            install_button.connect("clicked", self._launch_installer)
            content.append(install_button)

        system_group = Adw.PreferencesGroup(title="System")
        system_group.add(self._info_row("Operating system", info.name))
        system_group.add(self._info_row("Build", info.build_id))
        system_group.add(self._info_row("Edition", info.variant))
        ergenctl_status = "Installed" if shutil.which("ergenctl") else "Not installed"
        system_group.add(self._info_row("ErgenCTL", ergenctl_status))
        content.append(system_group)

        resources = Adw.PreferencesGroup(
            title="Project resources",
            description="Documentation, source code and issue tracking",
        )
        resources.add(
            self._link_row(
                "ErgenOS on GitHub",
                "Source code and releases",
                "https://github.com/ErgenosSW/ErgenOS-Linux",
            )
        )
        resources.add(
            self._link_row(
                "ErgenCTL",
                "Diagnostics and recovery documentation",
                "https://github.com/ErgenosSW/ErgenCTL",
            )
        )
        resources.add(
            self._link_row(
                "Report a problem",
                "Open the ErgenOS issue tracker",
                "https://github.com/ErgenosSW/ErgenOS-Linux/issues",
            )
        )
        content.append(resources)

        preferences = Adw.PreferencesGroup(title="Preferences")
        launch_switch = Adw.SwitchRow(
            title="Show at every login",
            subtitle="Open ErgenOS Welcome after future sign-ins",
        )
        launch_switch.set_active(autostart_enabled())
        launch_switch.connect(
            "notify::active",
            lambda row, _value: set_autostart_enabled(row.get_active()),
        )
        preferences.add(launch_switch)
        content.append(preferences)

    @staticmethod
    def _on_close_request(_window: Gtk.Window) -> bool:
        set_first_run_completed(True)
        return False

    @staticmethod
    def _launch_installer(_button: Gtk.Button) -> None:
        Gio.Subprocess.new(
            ["sudo", "-E", "/usr/local/bin/ergenos-installer"],
            Gio.SubprocessFlags.NONE,
        )

    @staticmethod
    def _info_row(title: str, value: str) -> Adw.ActionRow:
        row = Adw.ActionRow(title=title)
        label = Gtk.Label(label=value, selectable=True, xalign=1)
        label.add_css_class("dim-label")
        row.add_suffix(label)
        return row

    @staticmethod
    def _link_row(title: str, subtitle: str, uri: str) -> Adw.ActionRow:
        row = Adw.ActionRow(title=title, subtitle=subtitle, activatable=True)
        icon = Gtk.Image.new_from_icon_name("external-link-symbolic")
        row.add_suffix(icon)
        row.connect(
            "activated",
            lambda _row: Gio.AppInfo.launch_default_for_uri(uri, None),
        )
        return row


class WelcomeApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APPLICATION_ID)

    def do_activate(self) -> None:
        window = self.props.active_window
        if window is None:
            window = WelcomeWindow(self)
        window.present()


def main() -> int:
    parser = argparse.ArgumentParser(description="ErgenOS first-login welcome application")
    parser.add_argument("--autostart", action="store_true", help="start only when enabled by the user")
    arguments = parser.parse_args()
    if arguments.autostart and not should_autostart():
        return 0

    Adw.init()
    return WelcomeApplication().run(sys.argv[:1])


if __name__ == "__main__":
    raise SystemExit(main())
