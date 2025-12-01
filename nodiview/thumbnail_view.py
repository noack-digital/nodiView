"""
Thumbnail grid for navigating folders.
"""

import gi
import os
from pathlib import Path

gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk, GdkPixbuf, GLib
from .utils.file_utils import get_image_files_in_directory, is_image_file


class ThumbnailView(Gtk.ScrolledWindow):
    """Display thumbnails for all images in a directory."""

    def __init__(self, thumbnail_size=150):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.thumbnail_size = thumbnail_size

        self.flow_box = Gtk.FlowBox()
        self.flow_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.flow_box.set_max_children_per_line(10)
        self.flow_box.set_column_spacing(10)
        self.flow_box.set_row_spacing(10)
        self.flow_box.connect("child-activated", self.on_thumbnail_activated)
        self.set_child(self.flow_box)

        self.current_directory = None
        self.thumbnails = {}
        self.selection_callback = None

    def load_directory(self, directory):
        """Load every supported image from the provided directory."""
        if not directory or not os.path.isdir(directory):
            return

        self.current_directory = directory

        # Leere Flow Box
        while self.flow_box.get_first_child():
            child = self.flow_box.get_first_child()
            self.flow_box.remove(child)

        self.thumbnails = {}

        # Hole alle Bilddateien
        image_files = get_image_files_in_directory(directory)

        # Erstelle Thumbnails
        for filepath in image_files:
            self.create_thumbnail(filepath)

    def create_thumbnail(self, filepath):
        """Create a thumbnail widget for a file."""
        try:
            # Lade Bild
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(filepath)

            width = pixbuf.get_width()
            height = pixbuf.get_height()

            # Berechne Skalierung
            if width > height:
                new_width = self.thumbnail_size
                new_height = int(height * (self.thumbnail_size / width))
            else:
                new_height = self.thumbnail_size
                new_width = int(width * (self.thumbnail_size / height))

            # Skaliere
            scaled_pixbuf = pixbuf.scale_simple(
                new_width, new_height, GdkPixbuf.InterpType.BILINEAR
            )

            # Erstelle Container
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            box.set_margin_start(5)
            box.set_margin_end(5)
            box.set_margin_top(5)
            box.set_margin_bottom(5)

            # Bild
            picture = Gtk.Picture.new_for_pixbuf(scaled_pixbuf)
            picture.set_can_shrink(True)
            picture.set_content_fit(Gtk.ContentFit.CONTAIN)
            box.append(picture)

            # Dateiname
            filename = os.path.basename(filepath)
            label = Gtk.Label(label=filename)
            label.set_max_width_chars(20)
            label.set_ellipsize(GLib.PangoEllipsizeMode.MIDDLE)
            label.add_css_class("caption")
            box.append(label)

            box.set_data("filepath", filepath)

            self.flow_box.append(box)
            self.thumbnails[filepath] = box

        except Exception as e:
            print(f"Failed to build thumbnail for {filepath}: {e}")

    def on_thumbnail_activated(self, flow_box, child):
        """Emit callback when a thumbnail is activated."""
        filepath = child.get_child().get_data("filepath")
        if filepath and self.selection_callback:
            self.selection_callback(filepath)

    def set_selection_callback(self, callback):
        """Register a callback executed when a thumbnail is selected."""
        self.selection_callback = callback

    def set_thumbnail_size(self, size):
        """Change the thumbnail size and reload the directory."""
        self.thumbnail_size = size
        # Lade Verzeichnis neu wenn eines geladen ist
        if self.current_directory:
            self.load_directory(self.current_directory)

    def get_current_directory(self):
        """Return the current directory shown in the grid."""
        return self.current_directory

