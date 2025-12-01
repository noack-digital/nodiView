"""
File helper utilities.
"""

import os


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".tiff",
    ".tif",
    ".bmp",
    ".ico",
    ".svg",
    ".heic",
    ".heif",
}


def is_image_file(filepath):
    """Return True if the file extension is supported."""
    if not filepath:
        return False
    ext = os.path.splitext(filepath)[1].lower()
    return ext in IMAGE_EXTENSIONS


def get_image_files_in_directory(directory):
    """Return a sorted list of image files within the given directory."""
    if not directory or not os.path.isdir(directory):
        return []

    image_files = []
    try:
        for filename in sorted(os.listdir(directory)):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and is_image_file(filepath):
                image_files.append(filepath)
    except PermissionError:
        pass

    return image_files

