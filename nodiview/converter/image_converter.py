"""
Image conversion helpers.
"""

from PIL import Image
import os


class ImageConverter:
    """Convert images between multiple formats."""

    SUPPORTED_FORMATS = {
        "JPEG": ["jpg", "jpeg"],
        "PNG": ["png"],
        "GIF": ["gif"],
        "WebP": ["webp"],
        "TIFF": ["tiff", "tif"],
        "BMP": ["bmp"],
        "ICO": ["ico"],
    }

    def __init__(self):
        self.quality = 85
        self.optimize = True

    def convert(self, input_path, output_path, output_format=None):
        """
        Convert an image to another format.

        Args:
            input_path: Source path.
            output_path: Destination path.
            output_format: Target format or None to infer from extension.

        Returns:
            Output path or None on failure.
        """
        if not os.path.exists(input_path):
            return None

        if output_format is None:
            ext = os.path.splitext(output_path)[1].lower().lstrip(".")
            for fmt, exts in self.SUPPORTED_FORMATS.items():
                if ext in exts:
                    output_format = fmt
                    break

        if output_format is None:
            output_format = "PNG"  # Standard

        try:
            with Image.open(input_path) as img:
                if output_format in ("JPEG", "BMP") and img.mode in ("RGBA", "LA", "P"):
                    if img.mode == "RGBA":
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    else:
                        img = img.convert("RGB")
                elif output_format == "JPEG" and img.mode != "RGB":
                    img = img.convert("RGB")

                save_kwargs = {
                    "format": output_format,
                }

                if output_format in ("JPEG", "WebP"):
                    save_kwargs["quality"] = self.quality
                    if self.optimize:
                        save_kwargs["optimize"] = True

                if output_format == "JPEG":
                    save_kwargs["progressive"] = False

                img.save(output_path, **save_kwargs)
                return output_path

        except Exception as e:
            print(f"Image conversion failed: {e}")
            return None

    def get_supported_formats(self):
        """Return the supported formats."""
        return list(self.SUPPORTED_FORMATS.keys())

    def set_quality(self, quality):
        """Set quality for lossy formats (1-100)."""
        self.quality = max(1, min(100, int(quality)))

    def set_optimize(self, optimize):
        """Toggle encoder optimizations."""
        self.optimize = bool(optimize)

