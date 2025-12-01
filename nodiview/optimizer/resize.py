"""
Image resizing helpers with several interpolation filters.
"""

import pyvips
from PIL import Image


class ImageResizer:
    """Resize images with multiple interpolation filters."""

    VIPS_FILTERS = {
        "nearest": "nearest",
        "bilinear": "linear",
        "bicubic_mitchell": "cubic",
        "bicubic_catmull": "mitchell",
        "bicubic_bspline": "lanczos2",
        "lanczos3": "lanczos3",
    }

    PIL_FILTERS = {
        "nearest": Image.Resampling.NEAREST,
        "bilinear": Image.Resampling.BILINEAR,
        "bicubic_mitchell": Image.Resampling.LANCZOS,
        "bicubic_catmull": Image.Resampling.LANCZOS,
        "bicubic_bspline": Image.Resampling.LANCZOS,
        "lanczos3": Image.Resampling.LANCZOS,
    }

    def __init__(self):
        self.filter = "lanczos3"
        self.maintain_aspect_ratio = True

    def resize(self, image_path, output_path, width=None, height=None, scale=None):
        """
        Resize an image while optionally preserving aspect ratio.

        Args:
            image_path: Input file path.
            output_path: Output path.
            width: New width in pixels.
            height: New height in pixels.
            scale: Scale factor (e.g. 0.5 for 50%).

        Returns:
            Output path or None on failure.
        """
        try:
            image = pyvips.Image.new_from_file(image_path)
            original_width = image.width
            original_height = image.height

            if scale is not None:
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
            elif width is not None and height is not None:
                new_width = width
                new_height = height
            elif width is not None:
                if self.maintain_aspect_ratio:
                    aspect = original_height / original_width
                    new_width = width
                    new_height = int(width * aspect)
                else:
                    new_width = width
                    new_height = original_height
            elif height is not None:
                if self.maintain_aspect_ratio:
                    aspect = original_width / original_height
                    new_width = int(height * aspect)
                    new_height = height
                else:
                    new_width = original_width
                    new_height = height
            else:
                return None

            vips_filter = self.VIPS_FILTERS.get(self.filter, "lanczos3")

            resized = image.resize(new_width / original_width, vscale=new_height / original_height, kernel=vips_filter)

            resized.write_to_file(output_path)

            return output_path

        except Exception as e:
            print(f"pyvips resize failed: {e}")
            return self._resize_with_pil(image_path, output_path, width, height, scale)

    def _resize_with_pil(self, image_path, output_path, width, height, scale):
        """Fallback that uses Pillow for resizing."""
        try:
            with Image.open(image_path) as img:
                original_width, original_height = img.size

                if scale is not None:
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                elif width is not None and height is not None:
                    new_width = width
                    new_height = height
                elif width is not None:
                    if self.maintain_aspect_ratio:
                        aspect = original_height / original_width
                        new_width = width
                        new_height = int(width * aspect)
                    else:
                        new_width = width
                        new_height = original_height
                elif height is not None:
                    if self.maintain_aspect_ratio:
                        aspect = original_width / original_height
                        new_width = int(height * aspect)
                        new_height = height
                    else:
                        new_width = original_width
                        new_height = height
                else:
                    return None

                pil_filter = self.PIL_FILTERS.get(self.filter, Image.Resampling.LANCZOS)

                resized = img.resize((new_width, new_height), resample=pil_filter)

                resized.save(output_path)

                return output_path

        except Exception as e:
            print(f"PIL resize failed: {e}")
            return None

    def set_filter(self, filter_name):
        """Set interpolation filter."""
        if filter_name in self.VIPS_FILTERS:
            self.filter = filter_name

    def set_maintain_aspect_ratio(self, maintain):
        """Toggle whether the aspect ratio should be preserved."""
        self.maintain_aspect_ratio = bool(maintain)

