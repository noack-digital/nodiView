"""
Preferences window for nodiView.
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from .i18n import SUPPORTED_LANGUAGES, _, get_current_language


class SettingsDialog(Adw.PreferencesWindow):
    """Simple preferences dialog with language selector."""

    def __init__(self, parent, config, on_language_changed):
        super().__init__(transient_for=parent, modal=True)
        self.config = config
        self.on_language_changed = on_language_changed
        self.language_codes = list(SUPPORTED_LANGUAGES.keys())

        self.set_title(_("Preferences"))

        self.page = Adw.PreferencesPage()
        self.language_group = Adw.PreferencesGroup(title=_("Language"))

        self.language_row = Adw.ActionRow(title=_("Language"))
        self.language_dropdown = Gtk.DropDown(model=self._create_language_model())
        self.language_dropdown.set_selected(self._lang_index(get_current_language()))
        self.language_dropdown.connect("notify::selected", self._handle_language_change)
        self.language_row.add_suffix(self.language_dropdown)
        self.language_row.set_activatable_widget(self.language_dropdown)

        self.language_group.add(self.language_row)
        self.page.add(self.language_group)
        self.add(self.page)

    def _create_language_model(self):
        model = Gtk.StringList()
        for code in self.language_codes:
            model.append(SUPPORTED_LANGUAGES[code])
        return model

    def _lang_index(self, code: str) -> int:
        try:
            return self.language_codes.index(code)
        except ValueError:
            return 0

    def _handle_language_change(self, *_args):
        idx = self.language_dropdown.get_selected()
        if idx < 0 or idx >= len(self.language_codes):
            return
        new_lang = self.language_codes[idx]
        if new_lang == self.config.get("language"):
            return
        self.config["language"] = new_lang
        self.on_language_changed(new_lang)

    def refresh_translations(self):
        """Refresh labels after a language change."""
        self.set_title(_("Preferences"))
        self.language_group.set_title(_("Language"))
        self.language_row.set_title(_("Language"))
        # Recreate the model with updated translations
        self.language_dropdown.set_model(self._create_language_model())
        self.language_dropdown.set_selected(self._lang_index(get_current_language()))

