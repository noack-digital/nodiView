"""
Image helper utilities.
"""

import os
from PIL import Image


def get_image_info(image_path):
    """Return metadata about an image file."""
    try:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": os.path.getsize(image_path),
            }
    except Exception:
        return None


def get_file_size_mb(filepath):
    """Return the file size in megabytes."""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)

