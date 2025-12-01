"""
Image cropping helpers.
"""

from PIL import Image


def crop_image(image_path, x, y, width, height):
    """
    Crop an image to the provided rectangle.

    Args:
        image_path: Source file path.
        x: X coordinate of the top-left corner.
        y: Y coordinate of the top-left corner.
        width: Crop width.
        height: Crop height.

    Returns:
        PIL Image instance or None on failure.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            img_width, img_height = img.size
            x = max(0, min(x, img_width))
            y = max(0, min(y, img_height))
            width = min(width, img_width - x)
            height = min(height, img_height - y)
            cropped = img.crop((x, y, x + width, y + height))
            return cropped
    except Exception as e:
        print(f"Cropping failed: {e}")
        return None


def crop_to_selection(image_path, selection_box):
    """
    Crop an image using a selection tuple.

    Args:
        image_path: Source image path.
        selection_box: Tuple (x, y, width, height).

    Returns:
        PIL Image instance or None on failure.
    """
    x, y, width, height = selection_box
    return crop_image(image_path, x, y, width, height)

