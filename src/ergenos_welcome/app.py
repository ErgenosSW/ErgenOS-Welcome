"""GTK4 and libadwaita interface for ErgenOS Welcome."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402

from .resources import online_resources
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
        self.set_default_size(820, 700)
        self.add_css_class("ergen-shell")
        self.connect("close-request", self._on_close_request)
        self._install_styles()

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        brand = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=9)
        brand.add_css_class("ergen-header-brand")
        brand_icon = Gtk.Image.new_from_file(str(logo_path()))
        brand_icon.set_pixel_size(28)
        brand.append(brand_icon)
        brand_name = Gtk.Label(label="ErgenOS Welcome")
        brand_name.add_css_class("ergen-header-title")
        brand.append(brand_name)
        header.pack_start(brand)
        toolbar.add_top_bar(header)
        self.set_content(toolbar)

        scrolled = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        toolbar.set_content(scrolled)

        clamp = Adw.Clamp(maximum_size=680, tightening_threshold=520)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(32)
        clamp.set_margin_start(18)
        clamp.set_margin_end(18)
        scrolled.set_child(clamp)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        clamp.set_child(content)

        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        hero.add_css_class("ergen-hero")

        logo = Gtk.Image.new_from_file(str(logo_path()))
        logo.set_pixel_size(124)
        logo.set_accessible_role(Gtk.AccessibleRole.IMG)
        logo.update_property(
            [Gtk.AccessibleProperty.LABEL],
            ["ErgenOS logo"],
        )
        hero.append(logo)

        eyebrow = Gtk.Label(label="YOUR SYSTEM · YOUR RULES")
        eyebrow.add_css_class("ergen-eyebrow")
        hero.append(eyebrow)

        heading = Gtk.Label(label="Welcome to ErgenOS")
        heading.add_css_class("ergen-display")
        hero.append(heading)

        info = read_system_info()
        version = Gtk.Label(label=info.version)
        version.add_css_class("ergen-muted")
        hero.append(version)
        content.append(hero)

        if is_live_environment():
            install_button = Gtk.Button()
            install_button.add_css_class("suggested-action")
            install_button.set_halign(Gtk.Align.CENTER)
            install_button.connect("clicked", self._launch_installer)

            install_content = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=12,
            )
            install_content.set_margin_top(8)
            install_content.set_margin_bottom(8)
            install_content.set_margin_start(18)
            install_content.set_margin_end(18)
            install_content.append(
                Gtk.Image.new_from_icon_name("system-software-install-symbolic")
            )

            install_labels = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=2,
            )
            install_labels.set_halign(Gtk.Align.START)
            install_title = Gtk.Label(label="Install ErgenOS", xalign=0)
            install_title.add_css_class("heading")
            install_labels.append(install_title)
            install_labels.append(
                Gtk.Label(
                    label="Install ErgenOS on this computer",
                    xalign=0,
                )
            )
            install_content.append(install_labels)
            install_button.set_child(install_content)
            content.append(install_button)

        if shutil.which("ergenctl-gui") or shutil.which("ergenpac"):
            content.append(self._section_title("START HERE", "Your ErgenOS workspace"))
            actions = Gtk.Grid(column_spacing=14, row_spacing=14, column_homogeneous=True)
            if shutil.which("ergenpac"):
                actions.attach(
                    self._action_card(
                        "ErgenPac",
                        "Install software and update the system",
                        "io.github.ergenossw.ErgenPac",
                        self._launch_ergenpac,
                    ),
                    0, 0, 1, 1,
                )
            if shutil.which("ergenctl-gui"):
                actions.attach(
                    self._action_card(
                        "ErgenCTL",
                        "Check, repair or restore the system",
                        "ergenctl",
                        self._launch_ergenctl,
                    ),
                    1, 0, 1, 1,
                )
            content.append(actions)

        content.append(self._section_title("THIS DEVICE", "System identity"))
        system_grid = Gtk.Grid(column_spacing=12, row_spacing=12, column_homogeneous=True)
        system_grid.attach(self._detail_card("OPERATING SYSTEM", info.name), 0, 0, 1, 1)
        system_grid.attach(self._detail_card("BUILD", info.build_id), 1, 0, 1, 1)
        system_grid.attach(self._detail_card("EDITION", info.variant), 2, 0, 1, 1)
        content.append(system_grid)

        content.append(self._section_title("EXPLORE", "ErgenOS online"))
        resources = Gtk.FlowBox(
            column_spacing=12,
            row_spacing=12,
            selection_mode=Gtk.SelectionMode.NONE,
            homogeneous=True,
            max_children_per_line=2,
            min_children_per_line=2,
        )
        for resource in online_resources(GLib.get_language_names()):
            resources.append(self._resource_card(resource.title, resource.subtitle, resource.uri))
        content.append(resources)

        if not is_live_environment():
            preference = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
            preference.add_css_class("ergen-preference-card")
            preference_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            preference_text.set_hexpand(True)
            preference_title = Gtk.Label(label="Show at every login", xalign=0)
            preference_title.add_css_class("heading")
            preference_text.append(preference_title)
            preference_subtitle = Gtk.Label(
                label="Open ErgenOS Welcome after future sign-ins", xalign=0, wrap=True
            )
            preference_subtitle.add_css_class("ergen-muted")
            preference_text.append(preference_subtitle)
            preference.append(preference_text)
            launch_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
            launch_switch.set_active(autostart_enabled())
            launch_switch.connect(
                "notify::active",
                lambda switch, _value: set_autostart_enabled(switch.get_active()),
            )
            preference.append(launch_switch)
            content.append(preference)

    def _install_styles(self) -> None:
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
          window.ergen-shell {
            background: linear-gradient(145deg, #030a14, #071525);
            color: #eaf3ff;
          }
          window.ergen-shell headerbar {
            background: alpha(#030a14, 0.94);
            border-bottom: 1px solid alpha(#8fbeeb, 0.16);
            box-shadow: none;
          }
          .ergen-header-brand { margin-left: 4px; }
          .ergen-header-title { color: #eaf3ff; font-size: 16px; font-weight: 800; }
          .ergen-hero {
            padding: 28px 32px;
            border-radius: 22px;
            border: 1px solid alpha(#31b6ff, 0.28);
            background: linear-gradient(135deg, alpha(#0a2744, 0.96), alpha(#07111f, 0.96));
            box-shadow: 0 16px 42px alpha(black, 0.28);
          }
          .ergen-eyebrow {
            color: #54c3ff;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
          }
          .ergen-display {
            color: #f4f9ff;
            font-size: 30px;
            font-weight: 800;
          }
          .ergen-muted, .dim-label { color: #9db0c8; }
          .ergen-section-heading { margin-top: 8px; }
          .ergen-section-title { color: #f4f9ff; font-size: 19px; font-weight: 800; }
          .ergen-action-card, .ergen-resource-card, .ergen-detail-card, .ergen-preference-card {
            padding: 18px;
            border: 1px solid alpha(#8fbeeb, 0.16);
            border-radius: 16px;
            background: alpha(#081424, 0.92);
          }
          .ergen-action-card, .ergen-resource-card { min-height: 96px; }
          .ergen-action-card:hover, .ergen-resource-card:hover {
            border-color: alpha(#31b6ff, 0.48);
            background: alpha(#0d2c49, 0.94);
          }
          .ergen-card-title { color: #f4f9ff; font-size: 16px; font-weight: 750; }
          .ergen-card-icon { color: #54c3ff; }
          .ergen-detail-value { color: #eaf3ff; font-size: 15px; font-weight: 700; }
          .ergen-detail-card { min-height: 74px; }
          .boxed-list, preferencesgroup list {
            border: 1px solid alpha(#8fbeeb, 0.16);
            border-radius: 16px;
            background: alpha(#081424, 0.92);
          }
          row { background: transparent; }
          button.suggested-action {
            background: linear-gradient(135deg, #0aa7ff, #0068ff);
            color: white;
            font-weight: 700;
            box-shadow: 0 8px 24px alpha(#0068ff, 0.24);
          }
        """)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    @staticmethod
    def _section_title(eyebrow: str, title: str) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box.add_css_class("ergen-section-heading")
        kicker = Gtk.Label(label=eyebrow, xalign=0)
        kicker.add_css_class("ergen-eyebrow")
        box.append(kicker)
        heading = Gtk.Label(label=title, xalign=0)
        heading.add_css_class("ergen-section-title")
        box.append(heading)
        return box

    @staticmethod
    def _detail_card(label: str, value: str) -> Gtk.Widget:
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        card.add_css_class("ergen-detail-card")
        key = Gtk.Label(label=label, xalign=0)
        key.add_css_class("ergen-eyebrow")
        card.append(key)
        text = Gtk.Label(label=value, xalign=0, wrap=True, selectable=True)
        text.add_css_class("ergen-detail-value")
        card.append(text)
        return card

    @staticmethod
    def _resource_card(title: str, subtitle: str, uri: str) -> Gtk.Widget:
        button = Gtk.Button()
        button.add_css_class("ergen-resource-card")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        labels.set_hexpand(True)
        name = Gtk.Label(label=title, xalign=0)
        name.add_css_class("ergen-card-title")
        labels.append(name)
        description = Gtk.Label(label=subtitle, xalign=0, wrap=True)
        description.add_css_class("ergen-muted")
        labels.append(description)
        row.append(labels)
        row.append(Gtk.Image.new_from_icon_name("external-link-symbolic"))
        button.set_child(row)
        button.connect("clicked", lambda _button: Gio.AppInfo.launch_default_for_uri(uri, None))
        return button

    @staticmethod
    def _action_card(title: str, subtitle: str, icon_name: str, callback) -> Gtk.Widget:
        button = Gtk.Button()
        button.add_css_class("ergen-action-card")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(38)
        icon.add_css_class("ergen-card-icon")
        row.append(icon)
        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        labels.set_hexpand(True)
        name = Gtk.Label(label=title, xalign=0)
        name.add_css_class("ergen-card-title")
        labels.append(name)
        description = Gtk.Label(label=subtitle, xalign=0, wrap=True)
        description.add_css_class("ergen-muted")
        labels.append(description)
        row.append(labels)
        row.append(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        button.set_child(row)
        button.connect("clicked", callback)
        return button

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
    def _launch_ergenctl(_row: Adw.ActionRow) -> None:
        Gio.Subprocess.new(["ergenctl-gui"], Gio.SubprocessFlags.NONE)

    @staticmethod
    def _launch_ergenpac(_row: Adw.ActionRow) -> None:
        Gio.Subprocess.new(["ergenpac"], Gio.SubprocessFlags.NONE)

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

    @staticmethod
    def _action_row(
        title: str,
        subtitle: str,
        icon_name: str,
        callback,
    ) -> Adw.ActionRow:
        row = Adw.ActionRow(title=title, subtitle=subtitle, activatable=True)
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(40)
        row.add_prefix(icon)
        row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        row.connect("activated", callback)
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
