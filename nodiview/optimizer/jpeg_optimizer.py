"""
JPEG optimization helpers.
"""

import pyvips
from PIL import Image
import io


class JPEGOptimizer:
    """Optimize JPEG images using pyvips with a PIL fallback."""

    CHROMA_SUBSAMPLING = {
        "none": "4:4:4",
        "low": "4:2:2",
        "medium": "4:2:0",
        "high": "4:1:1",
    }

    def __init__(self):
        self.quality = 85
        self.chroma_subsampling = "medium"
        self.progressive = False
        self.grayscale = False
        self.keep_exif = True

    def optimize(self, image_path, output_path=None):
        """
        Optimize a JPEG file.

        Args:
            image_path: Input file path.
            output_path: Optional output path (defaults to overwriting).

        Returns:
            Output path or None on failure.
        """
        if output_path is None:
            output_path = image_path

        try:
            image = pyvips.Image.new_from_file(image_path)

            if self.grayscale:
                image = image.colourspace("b-w")

            options = {
                "Q": self.quality,
                "optimize_coding": True,
                "trellis_quant": True,
                "overshoot_deringing": True,
                "optimize_scans": True,
            }

            subsampling = self.CHROMA_SUBSAMPLING.get(
                self.chroma_subsampling, "4:2:0"
            )
            options["subsample_mode"] = subsampling

            if self.progressive:
                options["interlace"] = True

            if not self.keep_exif:
                image = image.copy()
                if image.get_typeof("exif-data") != 0:
                    image = image.copy()

            image.write_to_file(output_path, **options)

            return output_path

        except Exception as e:
            print(f"JPEG optimization failed: {e}")
            return self._optimize_with_pil(image_path, output_path)

    def _optimize_with_pil(self, image_path, output_path):
        """Fallback optimizer using Pillow."""
        try:
            with Image.open(image_path) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")

                if self.grayscale:
                    img = img.convert("L").convert("RGB")

                save_kwargs = {
                    "format": "JPEG",
                    "quality": self.quality,
                    "optimize": True,
                }

                if self.progressive:
                    save_kwargs["progressive"] = True

                if not self.keep_exif:
                    exif = img.getexif()
                    if exif:
                        data = list(img.getdata())
                        img_no_exif = Image.new(img.mode, img.size)
                        img_no_exif.putdata(data)
                        img = img_no_exif

                img.save(output_path, **save_kwargs)
                return output_path

        except Exception as e:
            print(f"PIL JPEG optimization failed: {e}")
            return None

    def set_quality(self, quality):
        """Set the JPEG quality (1-100)."""
        self.quality = max(1, min(100, int(quality)))

    def set_chroma_subsampling(self, subsampling):
        """Set chroma subsampling (none, low, medium, high)."""
        if subsampling in self.CHROMA_SUBSAMPLING:
            self.chroma_subsampling = subsampling

    def set_progressive(self, progressive):
        """Enable or disable progressive encoding."""
        self.progressive = bool(progressive)

    def set_grayscale(self, grayscale):
        """Enable or disable grayscale conversion."""
        self.grayscale = bool(grayscale)

    def set_keep_exif(self, keep_exif):
        """Control whether EXIF metadata should be preserved."""
        self.keep_exif = bool(keep_exif)

