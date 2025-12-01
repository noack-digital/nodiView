#!/usr/bin/env python3
"""
nodiView - Application entry point.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk

from .i18n import _, set_language
from .settings import SettingsDialog
from .utils.config import load_config, save_config
from .window import NodiViewWindow


class NodiViewApplication(Adw.Application):
    """Main application class."""

    def __init__(self):
        self.config = load_config()
        set_language(self.config.get("language", "en"))
        super().__init__(
            application_id="com.nodiview.NodiView",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self.connect("activate", self.on_activate)
        self.connect("open", self.on_open)
        self._settings_dialog = None
        self._register_actions()

    def on_activate(self, app):
        """Called when the app is activated."""
        self.win = NodiViewWindow(application=app, config=self.config)
        self.win.present()

    def on_open(self, app, files, n_files, hint):
        """Handle files opened via the desktop shell."""
        if not hasattr(self, "win") or not self.win:
            self.win = NodiViewWindow(application=app, config=self.config)
        self.win.present()
        if n_files > 0:
            self.win.open_file(files[0].get_path())

    def _register_actions(self):
        """Create application-level actions."""
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.on_settings_action)
        self.add_action(settings_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_action)
        self.add_action(about_action)

    def on_settings_action(self, *_args):
        """Open the preferences window."""
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog(
                parent=self.win,
                config=self.config,
                on_language_changed=self.apply_language_change,
            )
        self._settings_dialog.present()

    def on_about_action(self, *_args):
        """Show about dialog."""
        about = Adw.AboutWindow(
            application_name="nodiView",
            version="0.1.0",
            developer_name="nodiView Team",
            issue_url="https://github.com/nodiview/nodiview/issues",
            website="https://github.com/nodiview/nodiview",
            comments=_("Image viewer"),
            license_type=Gtk.License.GPL_3_0_ONLY,
        )
        about.set_transient_for(self.win)
        about.present()

    def apply_language_change(self, new_language: str):
        """Persist new language and refresh UI texts."""
        self.config["language"] = new_language
        save_config(self.config)
        set_language(new_language)
        if hasattr(self, "win") and self.win:
            self.win.refresh_translations()
        if self._settings_dialog:
            self._settings_dialog.refresh_translations()


def main(version=None):
    """Application entry point."""
    app = NodiViewApplication()
    return app.run(sys.argv)

