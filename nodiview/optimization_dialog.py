"""
Optimization dialog with preview and conversion tools.
"""

from __future__ import annotations

import os
import shutil
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")

from gi.repository import Adw, Gdk, GLib, Gtk

from .converter.image_converter import ImageConverter
from .i18n import _
from .image_viewer import ImageViewer
from .optimizer.gif_optimizer import GIFOptimizer
from .optimizer.jpeg_optimizer import JPEGOptimizer
from .optimizer.png_optimizer import PNGOptimizer
from .optimizer.resize import ImageResizer

FORMAT_CHOICES = [
    ("jpeg", "JPEG"),
    ("png", "PNG"),
    ("gif", "GIF"),
    ("webp", "WebP"),
    ("tiff", "TIFF"),
]


class OptimizationDialog(Adw.Window):
    """Dialog window for optimization, resizing, and conversion."""

    def __init__(self, parent, image_path):
        super().__init__(transient_for=parent, modal=True, title=_("Optimize image"))
        self.set_default_size(1200, 800)
        self.set_resizable(True)

        self.image_path = image_path
        self.preview_path = None
        self.temp_dir = tempfile.mkdtemp()

        # Create toolbar view with header bar for window controls
        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        # Add header bar with window controls
        header_bar = Adw.HeaderBar()
        header_bar.set_show_end_title_buttons(True)
        header_bar.set_show_start_title_buttons(True)
        toolbar_view.add_top_bar(header_bar)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        toolbar_view.set_content(main_box)

        # Top row: Format selection and resize options
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        top_row.set_margin_bottom(10)

        # Left side: Format selection
        format_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        format_label = Gtk.Label(label=_("Output format:"))
        format_label.add_css_class("title-4")
        format_label.set_halign(Gtk.Align.START)
        format_left.append(format_label)

        format_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.format_buttons = {}
        first_button = None
        for code, label in FORMAT_CHOICES:
            btn = Gtk.ToggleButton(label=label)
            if first_button is None:
                first_button = btn
                if code == "jpeg":
                    btn.set_active(True)
            else:
                btn.set_group(first_button)
            btn.connect("toggled", self.on_format_changed, code)
            self.format_buttons[code] = btn
            format_box.append(btn)

        format_left.append(format_box)
        top_row.append(format_left)

        # Right side: Resize options
        resize_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        resize_label = Gtk.Label(label=_("Size:"))
        resize_label.add_css_class("title-4")
        resize_label.set_halign(Gtk.Align.START)
        resize_right.append(resize_label)

        resize_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        resize_box.set_valign(Gtk.Align.CENTER)

        # Create CSS provider for compact spinbuttons with fixed height
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            .compact-spin {
                min-height: 32px;
                max-height: 32px;
                padding: 0px;
                margin: 0px;
            }
            .compact-spin > entry {
                min-height: 0px;
                max-height: 28px;
                padding: 0px 6px;
                margin: 0px;
                font-size: 0.9em;
            }
            .compact-spin > button {
                min-height: 0px;
                min-width: 0px;
                max-height: 14px;
                padding: 0px 4px;
                margin: 0px;
            }
            .compact-spin text {
                min-height: 0px;
            }
            """, -1
        )
        
        # Width
        width_label = Gtk.Label(label=_("Width"))
        width_label.set_margin_end(5)
        width_label.set_valign(Gtk.Align.CENTER)
        resize_box.append(width_label)
        self.width_spin = Gtk.SpinButton.new_with_range(0, 10000, 1)
        self.width_spin.set_value(0)  # 0 means not set
        self.width_spin.set_width_chars(6)
        self.width_spin.set_margin_top(0)
        self.width_spin.set_margin_bottom(0)
        # Apply compact CSS class
        self.width_spin.add_css_class("compact-spin")
        self.width_spin.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.width_spin.connect("value-changed", self.on_width_changed)
        resize_box.append(self.width_spin)

        x_label = Gtk.Label(label="x")
        x_label.set_valign(Gtk.Align.CENTER)
        x_label.set_margin_start(5)
        x_label.set_margin_end(5)
        resize_box.append(x_label)

        # Height
        height_label = Gtk.Label(label=_("Height"))
        height_label.set_margin_end(5)
        height_label.set_valign(Gtk.Align.CENTER)
        resize_box.append(height_label)
        self.height_spin = Gtk.SpinButton.new_with_range(0, 10000, 1)
        self.height_spin.set_value(0)  # 0 means not set
        self.height_spin.set_width_chars(6)
        self.height_spin.set_margin_top(0)
        self.height_spin.set_margin_bottom(0)
        # Apply compact CSS class
        self.height_spin.add_css_class("compact-spin")
        self.height_spin.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.height_spin.connect("value-changed", self.on_height_changed)
        resize_box.append(self.height_spin)

        # Percent
        percent_label = Gtk.Label(label=_("Percent"))
        percent_label.set_margin_start(10)
        percent_label.set_margin_end(5)
        percent_label.set_valign(Gtk.Align.CENTER)
        resize_box.append(percent_label)
        self.percent_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 500, 1)
        self.percent_scale.set_value(100)
        self.percent_scale.set_draw_value(False)  # Disable built-in value display
        self.percent_scale.set_hexpand(False)
        self.percent_scale.set_size_request(150, -1)
        self.percent_scale.connect("value-changed", self.on_percent_scale_changed)
        resize_box.append(self.percent_scale)

        # Add entry field for percent input
        self.percent_entry = Gtk.SpinButton.new_with_range(1, 500, 1)
        self.percent_entry.set_value(100)
        self.percent_entry.set_width_chars(4)
        self.percent_entry.set_margin_start(5)
        self.percent_entry.connect("value-changed", self.on_percent_entry_changed)
        resize_box.append(self.percent_entry)

        percent_unit_label = Gtk.Label(label="%")
        percent_unit_label.set_margin_start(2)
        resize_box.append(percent_unit_label)

        # Proportional checkbox
        self.maintain_aspect_switch = Gtk.Switch()
        self.maintain_aspect_switch.set_active(True)
        self.maintain_aspect_switch.set_valign(Gtk.Align.CENTER)
        aspect_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        aspect_row.set_valign(Gtk.Align.CENTER)
        aspect_label = Gtk.Label(label=_("Proportional"))
        aspect_label.set_margin_start(10)
        aspect_label.set_valign(Gtk.Align.CENTER)
        aspect_row.append(aspect_label)
        aspect_row.append(self.maintain_aspect_switch)
        resize_box.append(aspect_row)

        # Store original image dimensions for proportional calculation
        self.original_width = 0
        self.original_height = 0
        self._updating_dimensions = False  # Prevent recursive updates
        self._load_original_dimensions()

        resize_right.append(resize_box)
        top_row.append(resize_right)
        top_row.set_hexpand(True)

        main_box.append(top_row)

        # Comparison view container
        comparison_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Centered zoom controls for both images
        zoom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        zoom_bar.set_halign(Gtk.Align.CENTER)
        zoom_bar.set_margin_bottom(10)

        zoom_label = Gtk.Label(label=_("Zoom:"))
        zoom_bar.append(zoom_label)

        zoom_out_btn = Gtk.Button.new_from_icon_name("zoom-out-symbolic")
        zoom_out_btn.set_tooltip_text(_("Zoom out"))
        zoom_out_btn.connect("clicked", self.on_zoom_both_out)
        zoom_bar.append(zoom_out_btn)

        self.zoom_label_btn = Gtk.Button(label="100%")
        self.zoom_label_btn.set_tooltip_text(_("Reset zoom"))
        self.zoom_label_btn.connect("clicked", self.on_zoom_both_reset)
        zoom_bar.append(self.zoom_label_btn)

        zoom_in_btn = Gtk.Button.new_from_icon_name("zoom-in-symbolic")
        zoom_in_btn.set_tooltip_text(_("Zoom in"))
        zoom_in_btn.connect("clicked", self.on_zoom_both_in)
        zoom_bar.append(zoom_in_btn)

        comparison_box.append(zoom_bar)

        # Horizontal split: Original (left) and Preview (right)
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(600)  # Split in the middle
        comparison_box.append(paned)

        # Left side: Original image
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_box.set_margin_start(10)
        left_box.set_margin_end(10)
        left_box.set_margin_top(10)
        left_box.set_margin_bottom(10)

        # Original header with controls
        original_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        original_label = Gtk.Label(label=_("Original"))
        original_label.add_css_class("title-3")
        original_label.set_halign(Gtk.Align.START)
        original_label.set_hexpand(True)
        original_header.append(original_label)

        original_fullscreen = Gtk.Button.new_from_icon_name("view-fullscreen-symbolic")
        original_fullscreen.set_tooltip_text(_("Fullscreen"))
        original_fullscreen.connect("clicked", self.on_fullscreen_original_btn)
        original_header.append(original_fullscreen)

        left_box.append(original_header)

        original_scrolled = Gtk.ScrolledWindow()
        original_scrolled.set_min_content_height(300)
        original_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.original_viewer = ImageViewer()
        self.original_viewer.load_image(image_path)
        original_scrolled.set_child(self.original_viewer)

        left_box.append(original_scrolled)

        # Original file info
        self.original_info = self._create_info_box(image_path, is_original=True)
        left_box.append(self.original_info)

        paned.set_start_child(left_box)

        # Right side: Optimized preview
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_box.set_margin_start(10)
        right_box.set_margin_end(10)
        right_box.set_margin_top(10)
        right_box.set_margin_bottom(10)

        # Preview header with controls
        preview_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        preview_label = Gtk.Label(label=_("Preview"))
        preview_label.add_css_class("title-3")
        preview_label.set_halign(Gtk.Align.START)
        preview_label.set_hexpand(True)
        preview_header.append(preview_label)

        preview_fullscreen = Gtk.Button.new_from_icon_name("view-fullscreen-symbolic")
        preview_fullscreen.set_tooltip_text(_("Fullscreen"))
        preview_fullscreen.connect("clicked", self.on_fullscreen_preview_btn)
        preview_header.append(preview_fullscreen)

        right_box.append(preview_header)

        preview_scrolled = Gtk.ScrolledWindow()
        preview_scrolled.set_min_content_height(300)
        preview_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.preview_viewer = ImageViewer()
        self.preview_viewer.load_image(image_path)
        preview_scrolled.set_child(self.preview_viewer)

        right_box.append(preview_scrolled)

        # Preview file info
        self.preview_info = self._create_info_box(None, is_original=False)
        right_box.append(self.preview_info)

        paned.set_end_child(right_box)

        # Add comparison view to main box
        main_box.append(comparison_box)

        # Parameters panel (below the comparison view)
        params_label = Gtk.Label(label=_("Parameters"))
        params_label.add_css_class("title-4")
        params_label.set_halign(Gtk.Align.START)
        params_label.set_margin_top(10)
        main_box.append(params_label)

        # Initialize filter combo first
        self.resize_filter_combo = Gtk.ComboBoxText()
        self.resize_filter_combo.append("nearest", _("Nearest Neighbor"))
        self.resize_filter_combo.append("bilinear", _("Bilinear"))
        self.resize_filter_combo.append("bicubic_mitchell", _("Bicubic (Mitchell-Netravali)"))
        self.resize_filter_combo.append("bicubic_catmull", _("Bicubic (Catmull-Rom)"))
        self.resize_filter_combo.append("bicubic_bspline", _("B-Spline"))
        self.resize_filter_combo.append("lanczos3", _("Lanczos3"))
        self.resize_filter_combo.set_active_id("lanczos3")

        self.params_stack = Adw.ViewStack()
        self.params_stack.add_titled(self.create_jpeg_params(), "jpeg", "JPEG")
        self.params_stack.add_titled(self.create_png_params(), "png", "PNG")
        self.params_stack.add_titled(self.create_gif_params(), "gif", "GIF")
        self.params_stack.add_titled(self.create_resize_params(), "resize", _("Resize"))
        self.params_stack.set_visible_child_name("jpeg")

        params_scrolled = Gtk.ScrolledWindow()
        params_scrolled.set_min_content_height(200)
        params_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        params_scrolled.set_child(self.params_stack)
        main_box.append(params_scrolled)

        # Buttons at the bottom
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(20)

        cancel_button = Gtk.Button(label=_("Cancel"))
        cancel_button.connect("clicked", lambda *_: self.close())
        button_box.append(cancel_button)

        preview_button = Gtk.Button(label=_("Generate preview"))
        preview_button.add_css_class("suggested-action")
        preview_button.connect("clicked", self.on_preview_clicked)
        button_box.append(preview_button)

        save_button = Gtk.Button(label=_("Save"))
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.on_save_clicked)
        button_box.append(save_button)

        main_box.append(button_box)

        self.current_format = "jpeg"
        self._update_preview_info()

    def on_zoom_both_out(self, button):
        """Zoom out both images."""
        current_zoom = getattr(self, '_current_zoom', 1.0)
        new_zoom = max(0.1, current_zoom - 0.5)
        self._current_zoom = new_zoom
        self.original_viewer.set_zoom(new_zoom)
        self.preview_viewer.set_zoom(new_zoom)
        self.zoom_label_btn.set_label(f"{int(new_zoom * 100)}%")

    def on_zoom_both_in(self, button):
        """Zoom in both images."""
        current_zoom = getattr(self, '_current_zoom', 1.0)
        new_zoom = min(5.0, current_zoom + 0.5)
        self._current_zoom = new_zoom
        self.original_viewer.set_zoom(new_zoom)
        self.preview_viewer.set_zoom(new_zoom)
        self.zoom_label_btn.set_label(f"{int(new_zoom * 100)}%")

    def on_zoom_both_reset(self, button):
        """Reset zoom to 100%."""
        self._current_zoom = 1.0
        self.original_viewer.set_zoom(1.0)
        self.preview_viewer.set_zoom(1.0)
        self.zoom_label_btn.set_label("100%")

    def on_fullscreen_original_btn(self, button):
        """Show original in fullscreen."""
        dialog = Adw.Window(transient_for=self, modal=True, title=_("Original - Fullscreen"))
        dialog.set_default_size(1000, 800)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dialog.set_content(box)

        # Header with close button
        header = Adw.HeaderBar()
        box.append(header)

        # Image viewer
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        viewer = ImageViewer()
        viewer.load_image(self.image_path)
        scrolled.set_child(viewer)
        box.append(scrolled)

        dialog.present()

    def on_fullscreen_preview_btn(self, button):
        """Show preview in fullscreen."""
        if not self.preview_path or not os.path.exists(self.preview_path):
            return

        dialog = Adw.Window(transient_for=self, modal=True, title=_("Preview - Fullscreen"))
        dialog.set_default_size(1000, 800)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dialog.set_content(box)

        # Header with close button
        header = Adw.HeaderBar()
        box.append(header)

        # Image viewer
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        viewer = ImageViewer()
        viewer.load_image(self.preview_path)
        scrolled.set_child(viewer)
        box.append(scrolled)

        dialog.present()

    def refresh_translations(self):
        """Refresh UI strings when language changes."""
        # Update filter combo translations
        if self.resize_filter_combo:
            selected_id = self.resize_filter_combo.get_active_id()
            self.resize_filter_combo.remove_all()
            self.resize_filter_combo.append("nearest", _("Nearest Neighbor"))
            self.resize_filter_combo.append("bilinear", _("Bilinear"))
            self.resize_filter_combo.append("bicubic_mitchell", _("Bicubic (Mitchell-Netravali)"))
            self.resize_filter_combo.append("bicubic_catmull", _("Bicubic (Catmull-Rom)"))
            self.resize_filter_combo.append("bicubic_bspline", _("B-Spline"))
            self.resize_filter_combo.append("lanczos3", _("Lanczos3"))
            if selected_id:
                self.resize_filter_combo.set_active_id(selected_id)

    def _load_original_dimensions(self):
        """Load original image dimensions for proportional calculations."""
        try:
            from PIL import Image
            with Image.open(self.image_path) as img:
                self.original_width = img.width
                self.original_height = img.height
        except Exception as e:
            print(f"Failed to load image dimensions: {e}")
            self.original_width = 0
            self.original_height = 0

    def on_width_changed(self, spin_button):
        """Handle width change - update height if proportional."""
        if self._updating_dimensions:
            return
        if not self.maintain_aspect_switch.get_active():
            return
        width = int(spin_button.get_value())
        if width > 0 and self.original_width > 0:
            self._updating_dimensions = True
            proportional_height = int((width / self.original_width) * self.original_height)
            self.height_spin.set_value(proportional_height)
            # Reset percent scale
            self.percent_scale.set_value(100)
            self._updating_dimensions = False

    def on_height_changed(self, spin_button):
        """Handle height change - update width if proportional."""
        if self._updating_dimensions:
            return
        if not self.maintain_aspect_switch.get_active():
            return
        height = int(spin_button.get_value())
        if height > 0 and self.original_height > 0:
            self._updating_dimensions = True
            proportional_width = int((height / self.original_height) * self.original_width)
            self.width_spin.set_value(proportional_width)
            # Reset percent scale
            self.percent_scale.set_value(100)
            self._updating_dimensions = False

    def on_percent_scale_changed(self, scale):
        """Handle percent scale change - sync with entry and update dimensions."""
        if self._updating_dimensions:
            return
        self._updating_dimensions = True
        value = int(scale.get_value())
        self.percent_entry.set_value(value)
        self._updating_dimensions = False
        self._apply_percent_change(value)

    def on_percent_entry_changed(self, spinbutton):
        """Handle percent entry change - sync with scale and update dimensions."""
        if self._updating_dimensions:
            return
        self._updating_dimensions = True
        value = int(spinbutton.get_value())
        self.percent_scale.set_value(value)
        self._updating_dimensions = False
        self._apply_percent_change(value)

    def _apply_percent_change(self, percent):
        """Apply percent change to width/height if proportional."""
        if not self.maintain_aspect_switch.get_active():
            return
        if percent != 100 and self.original_width > 0 and self.original_height > 0:
            scale_factor = percent / 100.0
            new_width = int(self.original_width * scale_factor)
            new_height = int(self.original_height * scale_factor)
            self.width_spin.set_value(new_width)
            self.height_spin.set_value(new_height)

    def on_quality_scale_changed(self, scale):
        """Sync quality scale with entry."""
        if getattr(self, '_updating_quality', False):
            return
        self._updating_quality = True
        value = int(scale.get_value())
        self.quality_entry.set_value(value)
        self._updating_quality = False

    def on_quality_entry_changed(self, spinbutton):
        """Sync quality entry with scale."""
        if getattr(self, '_updating_quality', False):
            return
        self._updating_quality = True
        value = int(spinbutton.get_value())
        self.quality_scale.set_value(value)
        self._updating_quality = False

    def on_png_compression_scale_changed(self, scale):
        """Sync PNG compression scale with entry."""
        if getattr(self, '_updating_png_compression', False):
            return
        self._updating_png_compression = True
        value = int(scale.get_value())
        self.png_compression_entry.set_value(value)
        self._updating_png_compression = False

    def on_png_compression_entry_changed(self, spinbutton):
        """Sync PNG compression entry with scale."""
        if getattr(self, '_updating_png_compression', False):
            return
        self._updating_png_compression = True
        value = int(spinbutton.get_value())
        self.png_compression_scale.set_value(value)
        self._updating_png_compression = False

    def on_gif_colors_scale_changed(self, scale):
        """Sync GIF colors scale with entry."""
        if getattr(self, '_updating_gif_colors', False):
            return
        self._updating_gif_colors = True
        value = int(scale.get_value())
        self.gif_colors_entry.set_value(value)
        self._updating_gif_colors = False

    def on_gif_colors_entry_changed(self, spinbutton):
        """Sync GIF colors entry with scale."""
        if getattr(self, '_updating_gif_colors', False):
            return
        self._updating_gif_colors = True
        value = int(spinbutton.get_value())
        self.gif_colors_scale.set_value(value)
        self._updating_gif_colors = False

    def _create_info_box(self, filepath, is_original):
        """Create an info box showing file details."""
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.add_css_class("card")
        info_box.set_margin_top(10)

        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            size_bytes = os.path.getsize(filepath)
            size_kb = size_bytes / 1024
            size_mb = size_bytes / (1024 * 1024)

            name_label = Gtk.Label(label=_("File: {}").format(filename))
            name_label.set_halign(Gtk.Align.START)
            name_label.add_css_class("caption")
            info_box.append(name_label)

            if size_mb >= 1:
                size_text = _("Size: {:.2f} MB").format(size_mb)
            else:
                size_text = _("Size: {:.2f} KB").format(size_kb)
            size_label = Gtk.Label(label=size_text)
            size_label.set_halign(Gtk.Align.START)
            size_label.add_css_class("caption")
            info_box.append(size_label)
        else:
            placeholder = Gtk.Label(label=_("No preview generated"))
            placeholder.set_halign(Gtk.Align.START)
            placeholder.add_css_class("caption")
            placeholder.add_css_class("dim-label")
            info_box.append(placeholder)

        return info_box

    def _update_preview_info(self):
        """Update the preview info box with current preview file."""
        # Remove old children
        while self.preview_info.get_first_child():
            child = self.preview_info.get_first_child()
            self.preview_info.remove(child)

        if self.preview_path and os.path.exists(self.preview_path):
            filename = os.path.basename(self.preview_path)
            preview_size = os.path.getsize(self.preview_path)
            original_size = os.path.getsize(self.image_path)

            name_label = Gtk.Label(label=_("File: {}").format(filename))
            name_label.set_halign(Gtk.Align.START)
            name_label.add_css_class("caption")
            self.preview_info.append(name_label)

            preview_kb = preview_size / 1024
            preview_mb = preview_size / (1024 * 1024)
            if preview_mb >= 1:
                size_text = _("Size: {:.2f} MB").format(preview_mb)
            else:
                size_text = _("Size: {:.2f} KB").format(preview_kb)
            size_label = Gtk.Label(label=size_text)
            size_label.set_halign(Gtk.Align.START)
            size_label.add_css_class("caption")
            self.preview_info.append(size_label)

            # Calculate savings
            saved_bytes = original_size - preview_size
            saved_kb = saved_bytes / 1024
            saved_percent = (saved_bytes / original_size * 100) if original_size > 0 else 0

            if saved_bytes > 0:
                if saved_kb >= 1:
                    saved_text = _("Saved: {:.2f} KB ({:.1f}%)").format(saved_kb, saved_percent)
                else:
                    saved_text = _("Saved: {:.0f} bytes ({:.1f}%)").format(saved_bytes, saved_percent)
                saved_label = Gtk.Label(label=saved_text)
                saved_label.set_halign(Gtk.Align.START)
                saved_label.add_css_class("caption")
                saved_label.add_css_class("success")
                self.preview_info.append(saved_label)
            elif saved_bytes < 0:
                increased_kb = abs(saved_bytes) / 1024
                increased_text = _("Increased: {:.2f} KB ({:.1f}%)").format(
                    increased_kb, abs(saved_percent)
                )
                increased_label = Gtk.Label(label=increased_text)
                increased_label.set_halign(Gtk.Align.START)
                increased_label.add_css_class("caption")
                increased_label.add_css_class("warning")
                self.preview_info.append(increased_label)

    def on_format_changed(self, button, format_code):
        """Handle format button toggle."""
        if button.get_active():
            self.current_format = format_code
            # Update params stack
            if format_code in ("jpeg", "png", "gif"):
                self.params_stack.set_visible_child_name(format_code)
            else:
                # For other formats, show JPEG params as default (they're similar)
                self.params_stack.set_visible_child_name("jpeg")
            # Auto-generate preview after a short delay to allow UI to update
            GLib.idle_add(self.on_preview_clicked, None)

    def create_jpeg_params(self):
        """Create JPEG optimization parameters."""
        page = self._base_page()

        quality_label = Gtk.Label(label=_("Quality:"))
        quality_label.set_halign(Gtk.Align.START)
        page.append(quality_label)

        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.quality_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 100, 1)
        self.quality_scale.set_value(85)
        self.quality_scale.set_draw_value(False)
        self.quality_scale.set_hexpand(True)
        self.quality_scale.connect("value-changed", self.on_quality_scale_changed)
        quality_box.append(self.quality_scale)

        self.quality_entry = Gtk.SpinButton.new_with_range(1, 100, 1)
        self.quality_entry.set_value(85)
        self.quality_entry.set_width_chars(3)
        self.quality_entry.connect("value-changed", self.on_quality_entry_changed)
        quality_box.append(self.quality_entry)

        page.append(quality_box)

        chroma_label = Gtk.Label(label=_("Chroma subsampling:"))
        chroma_label.set_halign(Gtk.Align.START)
        page.append(chroma_label)

        self.chroma_combo = Gtk.ComboBoxText()
        self.chroma_combo.append("none", _("None (4:4:4)"))
        self.chroma_combo.append("low", _("Low (4:2:2)"))
        self.chroma_combo.append("medium", _("Medium (4:2:0)"))
        self.chroma_combo.append("high", _("High (4:1:1)"))
        self.chroma_combo.set_active_id("medium")
        page.append(self.chroma_combo)

        self.progressive_switch = self._toggle_row(page, _("Progressive JPEG:"))
        self.grayscale_switch = self._toggle_row(page, _("Grayscale:"))
        self.keep_exif_switch = self._toggle_row(page, _("Keep EXIF metadata:"), default=True)

        return page

    def create_png_params(self):
        """Create PNG optimization parameters."""
        page = self._base_page()

        compression_label = Gtk.Label(label=_("Compression level:"))
        compression_label.set_halign(Gtk.Align.START)
        page.append(compression_label)

        compression_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.png_compression_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 9, 1
        )
        self.png_compression_scale.set_value(6)
        self.png_compression_scale.set_draw_value(False)
        self.png_compression_scale.set_hexpand(True)
        self.png_compression_scale.connect("value-changed", self.on_png_compression_scale_changed)
        compression_box.append(self.png_compression_scale)

        self.png_compression_entry = Gtk.SpinButton.new_with_range(0, 9, 1)
        self.png_compression_entry.set_value(6)
        self.png_compression_entry.set_width_chars(2)
        self.png_compression_entry.connect("value-changed", self.on_png_compression_entry_changed)
        compression_box.append(self.png_compression_entry)

        page.append(compression_box)

        self.png_reduce_palette_switch = self._toggle_row(page, _("Reduce color palette:"))
        self.png_keep_alpha_switch = self._toggle_row(
            page, _("Keep alpha channel:"), default=True
        )
        self.png_interlaced_switch = self._toggle_row(page, _("Interlaced:"))

        return page

    def create_gif_params(self):
        """Create GIF optimization parameters."""
        page = self._base_page()

        self.gif_reduce_palette_switch = self._toggle_row(
            page, _("Reduce color palette:"), default=True
        )

        colors_label = Gtk.Label(label=_("Number of colors:"))
        colors_label.set_halign(Gtk.Align.START)
        page.append(colors_label)

        colors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.gif_colors_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 2, 256, 1)
        self.gif_colors_scale.set_value(256)
        self.gif_colors_scale.set_draw_value(False)
        self.gif_colors_scale.set_hexpand(True)
        self.gif_colors_scale.connect("value-changed", self.on_gif_colors_scale_changed)
        colors_box.append(self.gif_colors_scale)

        self.gif_colors_entry = Gtk.SpinButton.new_with_range(2, 256, 1)
        self.gif_colors_entry.set_value(256)
        self.gif_colors_entry.set_width_chars(3)
        self.gif_colors_entry.connect("value-changed", self.on_gif_colors_entry_changed)
        colors_box.append(self.gif_colors_entry)

        page.append(colors_box)

        self.gif_dither_switch = self._toggle_row(page, _("Dithering:"), default=True)
        self.gif_keep_animation_switch = self._toggle_row(
            page, _("Preserve animation:"), default=True
        )

        return page

    def create_resize_params(self):
        """Create resize parameters (filter selection only)."""
        page = self._base_page()

        filter_label = Gtk.Label(label=_("Interpolation filter:"))
        filter_label.set_halign(Gtk.Align.START)
        page.append(filter_label)

        page.append(self.resize_filter_combo)

        return page

    def _base_page(self):
        """Create a base page container."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        return box

    def _toggle_row(self, parent, label_text, default=False):
        """Create a toggle switch row."""
        switch = Gtk.Switch(active=default)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        row.append(label)
        row.append(switch)
        row.set_halign(Gtk.Align.START)
        parent.append(row)
        return switch

    def _determine_resize(self):
        """Determine resize parameters from UI."""
        width = int(self.width_spin.get_value())
        height = int(self.height_spin.get_value())
        percent = int(self.percent_scale.get_value())
        use_width = width > 0
        use_height = height > 0
        maintain_aspect = self.maintain_aspect_switch.get_active()

        # If percent is not 100, use scale
        if percent != 100:
            return {"scale": percent / 100.0, "maintain_aspect": maintain_aspect}

        # If both width and height are set
        if use_width and use_height:
            return {"width": width, "height": height, "maintain_aspect": maintain_aspect}

        # If only width is set and proportional is enabled
        if use_width and maintain_aspect:
            return {"width": width, "maintain_aspect": True}

        # If only height is set and proportional is enabled
        if use_height and maintain_aspect:
            return {"height": height, "maintain_aspect": True}

        # If only width is set without proportional
        if use_width:
            return {"width": width, "maintain_aspect": False}

        # If only height is set without proportional
        if use_height:
            return {"height": height, "maintain_aspect": False}

        return {}

    def _apply_resize(self, input_path):
        """Apply resize to the image."""
        resize_params = self._determine_resize()
        if not resize_params:
            return input_path

        # Get maintain_aspect from params and remove it
        maintain_aspect = resize_params.pop("maintain_aspect", True)

        resizer = ImageResizer()
        resizer.set_filter(self.resize_filter_combo.get_active_id())
        resizer.set_maintain_aspect_ratio(maintain_aspect)

        # Determine output extension (keep original extension for resize)
        resized_path = os.path.join(self.temp_dir, "resized" + os.path.splitext(input_path)[1])
        result = resizer.resize(input_path, resized_path, **resize_params)

        if result and os.path.exists(resized_path):
            return resized_path
        return input_path

    def _optimize_by_format(self, source_path, format_code):
        """Optimize image based on selected format."""
        extension_map = {
            "jpeg": ".jpg",
            "png": ".png",
            "gif": ".gif",
            "webp": ".webp",
            "tiff": ".tiff",
        }
        extension = extension_map.get(format_code, ".jpg")
        preview_file = os.path.join(self.temp_dir, "preview" + extension)

        # Resize is already applied before calling this function

        try:
            if format_code == "jpeg":
                optimizer = JPEGOptimizer()
                optimizer.set_quality(int(self.quality_scale.get_value()))
                optimizer.set_chroma_subsampling(self.chroma_combo.get_active_id())
                optimizer.set_progressive(self.progressive_switch.get_active())
                optimizer.set_grayscale(self.grayscale_switch.get_active())
                optimizer.set_keep_exif(self.keep_exif_switch.get_active())
                result = optimizer.optimize(source_path, preview_file)
                if not result:
                    # Fallback: use converter
                    converter = ImageConverter()
                    converter.set_quality(int(self.quality_scale.get_value()))
                    converter.convert(source_path, preview_file, "JPEG")
            elif format_code == "png":
                optimizer = PNGOptimizer()
                optimizer.set_compression_level(int(self.png_compression_scale.get_value()))
                optimizer.set_reduce_palette(self.png_reduce_palette_switch.get_active())
                optimizer.set_keep_alpha(self.png_keep_alpha_switch.get_active())
                optimizer.set_interlaced(self.png_interlaced_switch.get_active())
                result = optimizer.optimize(source_path, preview_file)
                if not result:
                    # Fallback: use converter
                    converter = ImageConverter()
                    converter.convert(source_path, preview_file, "PNG")
            elif format_code == "gif":
                optimizer = GIFOptimizer()
                optimizer.set_reduce_palette(self.gif_reduce_palette_switch.get_active())
                optimizer.set_palette_colors(int(self.gif_colors_scale.get_value()))
                optimizer.set_dither(self.gif_dither_switch.get_active())
                optimizer.set_keep_animation(self.gif_keep_animation_switch.get_active())
                result = optimizer.optimize(source_path, preview_file)
                if not result:
                    # Fallback: use converter
                    converter = ImageConverter()
                    converter.convert(source_path, preview_file, "GIF")
            else:
                # Convert to other formats (WebP, TIFF, etc.)
                converter = ImageConverter()
                format_name = format_code.upper()
                if format_name == "JPEG":
                    format_name = "JPEG"
                converter.set_quality(85)  # Default quality for lossy formats
                result = converter.convert(source_path, preview_file, format_name)
                if not result:
                    print(f"Failed to convert to {format_name}")

            # Verify file was created
            if not os.path.exists(preview_file):
                print(f"Preview file was not created: {preview_file}")
                return None

            return preview_file
        except Exception as e:
            print(f"Error optimizing image: {e}")
            import traceback
            traceback.print_exc()
            return None

    def process_image(self):
        """Process the image with current settings."""
        # Apply resize first, then optimize/convert
        resized_path = self._apply_resize(self.image_path)
        return self._optimize_by_format(resized_path, self.current_format)

    def on_preview_clicked(self, _button):
        """Generate a preview image."""
        try:
            self.preview_path = self.process_image()
            if self.preview_path and os.path.exists(self.preview_path):
                # Verify file is not empty
                if os.path.getsize(self.preview_path) > 0:
                    self.preview_viewer.load_image(self.preview_path)
                    self._update_preview_info()
                else:
                    print(f"Preview file is empty: {self.preview_path}")
            else:
                print(f"Preview generation failed or file not found: {self.preview_path}")
        except Exception as e:
            print(f"Error generating preview: {e}")
            import traceback
            traceback.print_exc()

    def on_save_clicked(self, _button):
        """Save the optimized image."""
        dialog = Gtk.FileDialog(modal=True, title=_("Save"))
        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        extension_map = {
            "jpeg": ".jpg",
            "png": ".png",
            "gif": ".gif",
            "webp": ".webp",
            "tiff": ".tiff",
        }
        ext = extension_map.get(self.current_format, ".jpg")
        dialog.set_initial_name(f"{base_name}_optimized{ext}")
        dialog.save(self, None, self.on_save_dialog_response)

    def on_save_dialog_response(self, dialog, result):
        """Handle save response."""
        try:
            file = dialog.save_finish(result)
            if not file:
                return
            output_path = file.get_path()
            self.on_preview_clicked(None)
            if self.preview_path and os.path.exists(self.preview_path):
                shutil.copy2(self.preview_path, output_path)
                self.close()
        except GLib.Error as exc:
            print(f"Save failed: {exc}")

    def close(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        super().close()
