"""
PNG optimization helpers.
"""

import pyvips
from PIL import Image
import io


class PNGOptimizer:
    """Optimize PNG images."""

    def __init__(self):
        self.compression_level = 6  # 0-9
        self.reduce_palette = False
        self.keep_alpha = True
        self.interlaced = False

    def optimize(self, image_path, output_path=None):
        """
        Optimize a PNG file.

        Args:
            image_path: Input file.
            output_path: Output destination or None to overwrite.

        Returns:
            Output path or None on failure.
        """
        if output_path is None:
            output_path = image_path

        try:
            image = pyvips.Image.new_from_file(image_path)

            if not self.keep_alpha and image.has_alpha():
                image = image.flatten()

            if self.reduce_palette:
                image = image.colourspace("srgb")
                image = image.quantize(256, "uniform", dither=0.5)

            options = {
                "compression": self.compression_level,
            }

            if self.interlaced:
                options["interlace"] = True

            image.write_to_file(output_path, **options)

            return output_path

        except Exception as e:
            print(f"PNG optimization failed: {e}")
            return self._optimize_with_pil(image_path, output_path)

    def _optimize_with_pil(self, image_path, output_path):
        """Fallback optimizer using Pillow."""
        try:
            with Image.open(image_path) as img:
                if not self.keep_alpha and img.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img)
                    img = background

                if self.reduce_palette:
                    img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)

                save_kwargs = {
                    "format": "PNG",
                    "compress_level": self.compression_level,
                    "optimize": True,
                }

                if self.interlaced:
                    save_kwargs["interlace"] = True

                img.save(output_path, **save_kwargs)
                return output_path

        except Exception as e:
            print(f"PIL PNG optimization failed: {e}")
            return None

    def set_compression_level(self, level):
        """Set compression level (0-9)."""
        self.compression_level = max(0, min(9, int(level)))

    def set_reduce_palette(self, reduce):
        """Toggle palette reduction."""
        self.reduce_palette = bool(reduce)

    def set_keep_alpha(self, keep):
        """Toggle alpha preservation."""
        self.keep_alpha = bool(keep)

    def set_interlaced(self, interlaced):
        """Toggle interlaced encoding."""
        self.interlaced = bool(interlaced)

