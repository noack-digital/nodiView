"""
Image mirroring helpers.
"""

from PIL import Image


def flip_horizontal(image_path):
    """
    Flip an image horizontally.

    Args:
        image_path: Source image path.

    Returns:
        PIL Image instance or None on failure.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            flipped = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            return flipped
    except Exception as e:
        print(f"Horizontal flip failed: {e}")
        return None


def flip_vertical(image_path):
    """
    Flip an image vertically.

    Args:
        image_path: Source image path.

    Returns:
        PIL Image instance or None on failure.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            flipped = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            return flipped
    except Exception as e:
        print(f"Vertical flip failed: {e}")
        return None

