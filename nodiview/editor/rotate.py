"""
Image rotation helpers.
"""

from PIL import Image


def rotate_image(image_path, degrees):
    """
    Rotate an image by the given angle.

    Args:
        image_path: Path to the source image.
        degrees: Rotation angle (90, 180, 270).

    Returns:
        PIL Image instance or None on failure.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            rotated = img.rotate(-degrees, expand=True)
            return rotated
    except Exception as e:
        print(f"Rotation failed: {e}")
        return None


def rotate_90(image_path):
    """Rotate an image by 90° clockwise."""
    return rotate_image(image_path, 90)


def rotate_180(image_path):
    """Rotate an image by 180°."""
    return rotate_image(image_path, 180)


def rotate_270(image_path):
    """Rotate an image by 270° clockwise (90° counter-clockwise)."""
    return rotate_image(image_path, 270)

