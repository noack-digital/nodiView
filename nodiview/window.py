"""
nodiView - main window.
"""

from __future__ import annotations

import os
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk

from .editor.flip import flip_horizontal, flip_vertical
from .editor.rotate import rotate_image
from .i18n import _
from .image_viewer import ImageViewer
from .optimization_dialog import OptimizationDialog
from .utils.file_utils import get_image_files_in_directory


class NodiViewWindow(Adw.ApplicationWindow):
    """Primary nodiView window."""

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.set_title("nodiView")
        self.set_default_size(1200, 800)

        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)

        self.settings_menu = Gio.Menu()
        self.settings_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        self.settings_button.set_menu_model(self.settings_menu)
        self.header_bar.pack_end(self.settings_button)

        self.open_button = Gtk.Button.new_from_icon_name("document-open-symbolic")
        self.open_button.connect("clicked", self.on_open_clicked)
        self.header_bar.pack_start(self.open_button)

        self.optimize_button = Gtk.Button.new_from_icon_name("document-edit-symbolic")
        self.optimize_button.connect("clicked", self.on_optimize_clicked)
        self.header_bar.pack_start(self.optimize_button)

        self.edit_menu = Gio.Menu()
        self.edit_button = Gtk.MenuButton(icon_name="edit-symbolic")
        self.edit_button.set_menu_model(self.edit_menu)
        self.header_bar.pack_start(self.edit_button)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toolbar_view.set_content(self.main_box)

        self.image_viewer = ImageViewer()
        self.main_box.append(self.image_viewer)

        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.nav_box.set_margin_top(10)
        self.nav_box.set_margin_bottom(10)
        self.nav_box.set_halign(Gtk.Align.CENTER)

        self.prev_button = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        self.prev_button.connect("clicked", self.on_prev_clicked)
        self.nav_box.append(self.prev_button)

        self.next_button = Gtk.Button.new_from_icon_name("go-next-symbolic")
        self.next_button.connect("clicked", self.on_next_clicked)
        self.nav_box.append(self.next_button)

        self.main_box.append(self.nav_box)

        self.current_file = None
        self.file_list = []
        self.current_index = -1

        self.setup_shortcuts()
        self.setup_actions()
        self.refresh_translations()

    def setup_shortcuts(self):
        """Register keyboard shortcuts."""
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.LOCAL)

        controller.add_shortcut(
            Gtk.Shortcut.new(
                Gtk.ShortcutTrigger.parse_string("<Ctrl>o"),
                Gtk.CallbackAction.new(self.on_open_shortcut),
            )
        )
        controller.add_shortcut(
            Gtk.Shortcut.new(
                Gtk.ShortcutTrigger.parse_string("Left"),
                Gtk.CallbackAction.new(self.on_prev_shortcut),
            )
        )
        controller.add_shortcut(
            Gtk.Shortcut.new(
                Gtk.ShortcutTrigger.parse_string("Right"),
                Gtk.CallbackAction.new(self.on_next_shortcut),
            )
        )
        self.add_controller(controller)

    def on_open_clicked(self, _button):
        """Show a file chooser and open an image."""
        dialog = Gtk.FileDialog(modal=True, title=_("Open image"))
        filter_images = Gtk.FileFilter()
        filter_images.set_name(_("Images"))
        filter_images.add_mime_type("image/*")
        dialog.set_default_filter(filter_images)
        dialog.open(self, None, self.on_file_dialog_response)

    def on_file_dialog_response(self, dialog, result):
        """Handle the file chooser result."""
        try:
            file = dialog.open_finish(result)
            if file:
                self.open_file(file.get_path())
        except GLib.Error as exc:
            print(_("Could not open file: {}").format(exc))

    def open_file(self, filepath):
        """Load the requested file and prepare navigation data."""
        if not filepath:
            return

        self.current_file = filepath
        self.image_viewer.load_image(filepath)

        directory = GLib.path_get_dirname(filepath)
        self.file_list = get_image_files_in_directory(directory)
        try:
            self.current_index = self.file_list.index(filepath)
        except ValueError:
            self.current_index = -1

        self.update_navigation_buttons()
        filename = GLib.path_get_basename(filepath)
        self.set_title(f"nodiView - {filename}")

    def update_navigation_buttons(self):
        """Enable or disable navigation buttons."""
        has_prev = self.current_index > 0
        has_next = self.current_index >= 0 and self.current_index < len(self.file_list) - 1
        self.prev_button.set_sensitive(has_prev)
        self.next_button.set_sensitive(has_next)

    def on_prev_clicked(self, _button):
        """Display the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self.open_file(self.file_list[self.current_index])

    def on_next_clicked(self, _button):
        """Display the next image."""
        if self.current_index >= 0 and self.current_index < len(self.file_list) - 1:
            self.current_index += 1
            self.open_file(self.file_list[self.current_index])

    def on_open_shortcut(self, *_args):
        """Shortcut callback for opening files."""
        self.on_open_clicked(None)

    def on_prev_shortcut(self, *_args):
        """Shortcut callback for the previous image."""
        self.on_prev_clicked(None)

    def on_next_shortcut(self, *_args):
        """Shortcut callback for the next image."""
        self.on_next_clicked(None)

    def setup_actions(self):
        """Create SimpleActions for editing operations."""
        action_group = Gio.SimpleActionGroup()
        self.insert_action_group("win", action_group)

        action = Gio.SimpleAction.new("rotate90", None)
        action.connect("activate", lambda *_: self.rotate_image(90))
        action_group.add_action(action)

        action = Gio.SimpleAction.new("rotate180", None)
        action.connect("activate", lambda *_: self.rotate_image(180))
        action_group.add_action(action)

        action = Gio.SimpleAction.new("rotate270", None)
        action.connect("activate", lambda *_: self.rotate_image(270))
        action_group.add_action(action)

        action = Gio.SimpleAction.new("flip_h", None)
        action.connect("activate", lambda *_: self.flip_image("horizontal"))
        action_group.add_action(action)

        action = Gio.SimpleAction.new("flip_v", None)
        action.connect("activate", lambda *_: self.flip_image("vertical"))
        action_group.add_action(action)

    def on_optimize_clicked(self, _button):
        """Open the optimization dialog."""
        if not self.current_file:
            return
        dialog = OptimizationDialog(self, self.current_file)
        # Store reference to dialog for translation updates
        if not hasattr(self, "_optimization_dialogs"):
            self._optimization_dialogs = []
        self._optimization_dialogs.append(dialog)
        dialog.present()

    def rotate_image(self, degrees):
        """Rotate the current image by the given degrees."""
        if not self.current_file:
            return
        rotated = rotate_image(self.current_file, degrees)
        if rotated:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(self.current_file)[1], delete=False
            )
            temp_file.close()
            rotated.save(temp_file.name)
            rotated.close()
            os.replace(temp_file.name, self.current_file)
            self.image_viewer.load_image(self.current_file)

    def flip_image(self, direction):
        """Flip the current image horizontally or vertically."""
        if not self.current_file:
            return
        flipped = (
            flip_horizontal(self.current_file)
            if direction == "horizontal"
            else flip_vertical(self.current_file)
        )
        if flipped:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(self.current_file)[1], delete=False
            )
            temp_file.close()
            flipped.save(temp_file.name)
            flipped.close()
            os.replace(temp_file.name, self.current_file)
            self.image_viewer.load_image(self.current_file)

    def refresh_translations(self):
        """Refresh UI strings when the language changes."""
        self.settings_menu.remove_all()
        self.settings_menu.append(_("Settings"), "app.settings")
        self.settings_menu.append(_("About"), "app.about")
        self.open_button.set_tooltip_text(_("Open image"))
        self.optimize_button.set_tooltip_text(_("Optimize image"))
        self.edit_menu.remove_all()
        self.edit_menu.append(_("Rotate 90°"), "win.rotate90")
        self.edit_menu.append(_("Rotate 180°"), "win.rotate180")
        self.edit_menu.append(_("Rotate 270°"), "win.rotate270")
        self.edit_menu.append(_("Mirror horizontally"), "win.flip_h")
        self.edit_menu.append(_("Mirror vertically"), "win.flip_v")
        self.edit_button.set_tooltip_text(_("Edit"))
        self.prev_button.set_tooltip_text(_("Previous image"))
        self.next_button.set_tooltip_text(_("Next image"))
        # Refresh optimization dialogs if open
        if hasattr(self, "_optimization_dialogs"):
            for dialog in self._optimization_dialogs:
                if hasattr(dialog, "refresh_translations"):
                    dialog.refresh_translations()

