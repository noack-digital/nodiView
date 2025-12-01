"""
nodiView - image viewer widget with zoom support.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gdk, GdkPixbuf, Gtk
from PIL import Image
import io


class ImageViewer(Gtk.ScrolledWindow):
    """Widget that displays images and supports zooming."""

    def __init__(self):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.picture = Gtk.Picture()
        self.picture.set_can_shrink(False)
        # Don't use CONTAIN - it overrides manual zoom scaling
        self.set_child(self.picture)

        self.current_image_path = None
        self.original_pixbuf = None
        self.current_zoom = 1.0

        self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]

        controller = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        controller.connect("scroll", self.on_scroll)
        self.add_controller(controller)

        gesture = Gtk.GestureZoom()
        gesture.connect("scale-changed", self.on_gesture_zoom)
        self.add_controller(gesture)

    def load_image(self, filepath):
        """Load an image from disk."""
        if not filepath:
            return False

        try:
            pil_image = Image.open(filepath)
            self.current_image_path = filepath

            if pil_image.mode != "RGB":
                if pil_image.mode == "RGBA":
                    background = Image.new("RGB", pil_image.size, (255, 255, 255))
                    background.paste(pil_image, mask=pil_image.split()[3])
                    pil_image = background
                else:
                    pil_image = pil_image.convert("RGB")

            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            loader = GdkPixbuf.PixbufLoader.new_with_type("png")
            loader.write(img_bytes.getvalue())
            loader.close()
            self.original_pixbuf = loader.get_pixbuf()

            self.current_zoom = 1.0
            self.update_display()

            return True

        except Exception as e:
            print(f"Failed to load image: {e}")
            return False

    def update_display(self):
        """Refresh the pixbuf at the current zoom level."""
        if not self.original_pixbuf:
            return

        width = int(self.original_pixbuf.get_width() * self.current_zoom)
        height = int(self.original_pixbuf.get_height() * self.current_zoom)

        scaled_pixbuf = self.original_pixbuf.scale_simple(
            width, height, GdkPixbuf.InterpType.BILINEAR
        )

        self.picture.set_pixbuf(scaled_pixbuf)

    def zoom_in(self):
        """Zoom in to the next predefined level."""
        for level in self.zoom_levels:
            if level > self.current_zoom:
                self.current_zoom = level
                self.update_display()
                return
        self.current_zoom *= 2.0
        self.update_display()

    def zoom_out(self):
        """Zoom out to the previous predefined level."""
        for level in reversed(self.zoom_levels):
            if level < self.current_zoom:
                self.current_zoom = level
                self.update_display()
                return
        self.current_zoom /= 2.0
        if self.current_zoom < 0.1:
            self.current_zoom = 0.1
        self.update_display()

    def zoom_fit(self):
        """Fit the image into the visible area."""
        if not self.original_pixbuf:
            return

        allocation = self.get_allocation()
        available_width = allocation.width
        available_height = allocation.height

        if available_width <= 0 or available_height <= 0:
            return

        img_width = self.original_pixbuf.get_width()
        img_height = self.original_pixbuf.get_height()

        zoom_x = available_width / img_width
        zoom_y = available_height / img_height

        self.current_zoom = min(zoom_x, zoom_y)
        self.update_display()

    def zoom_100(self):
        """Reset zoom level to 100%."""
        self.current_zoom = 1.0
        self.update_display()

    def set_zoom(self, zoom_level):
        """Set a specific zoom level."""
        self.current_zoom = max(0.1, min(5.0, zoom_level))
        self.update_display()

    def on_scroll(self, controller, dx, dy):
        """Allow zooming using Ctrl + scroll."""
        modifiers = controller.get_current_event_state()
        if modifiers & Gdk.ModifierType.CONTROL_MASK:
            if dy > 0:
                self.zoom_out()
            else:
                self.zoom_in()
            return True
        return False

    def on_gesture_zoom(self, gesture, scale):
        """Handle touchpad pinch zoom."""
        if scale > 1.0:
            self.zoom_in()
        elif scale < 1.0:
            self.zoom_out()

    def get_current_image(self):
        """Return the path to the currently loaded image."""
        return self.current_image_path

    def get_zoom_level(self):
        """Return the current zoom level."""
        return self.current_zoom

