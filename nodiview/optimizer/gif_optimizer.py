"""
GIF optimization helpers.
"""

from PIL import Image
import io


class GIFOptimizer:
    """Optimize GIF images, including animated ones."""

    def __init__(self):
        self.reduce_palette = True
        self.palette_colors = 256
        self.dither = True
        self.keep_animation = True

    def optimize(self, image_path, output_path=None):
        """
        Optimize a GIF file.

        Args:
            image_path: Input file.
            output_path: Output destination or None to overwrite.

        Returns:
            Output path or None on failure.
        """
        if output_path is None:
            output_path = image_path

        try:
            with Image.open(image_path) as img:
                is_animated = getattr(img, "is_animated", False)

                if is_animated and self.keep_animation:
                    frames = []
                    durations = []

                    try:
                        while True:
                            frame = img.copy()
                            if self.reduce_palette:
                                frame = frame.convert(
                                    "P",
                                    palette=Image.Palette.ADAPTIVE,
                                    colors=self.palette_colors,
                                )
                            else:
                                frame = frame.convert("P")

                            frames.append(frame)
                            durations.append(img.info.get("duration", 100))

                            img.seek(img.tell() + 1)
                    except EOFError:
                        pass

                    if frames:
                        frames[0].save(
                            output_path,
                            format="GIF",
                            save_all=True,
                            append_images=frames[1:],
                            duration=durations,
                            loop=img.info.get("loop", 0),
                            optimize=True,
                            dither=Image.Dither.FLOYDSTEINBERG if self.dither else Image.Dither.NONE,
                        )

                else:
                    if self.reduce_palette:
                        img = img.convert(
                            "P",
                            palette=Image.Palette.ADAPTIVE,
                            colors=self.palette_colors,
                        )
                    else:
                        img = img.convert("P")

                    save_kwargs = {
                        "format": "GIF",
                        "optimize": True,
                    }

                    if self.dither:
                        save_kwargs["dither"] = Image.Dither.FLOYDSTEINBERG
                    else:
                        save_kwargs["dither"] = Image.Dither.NONE

                    img.save(output_path, **save_kwargs)

                return output_path

        except Exception as e:
            print(f"GIF optimization failed: {e}")
            return None

    def set_reduce_palette(self, reduce):
        """Toggle palette reduction."""
        self.reduce_palette = bool(reduce)

    def set_palette_colors(self, colors):
        """Set number of colors (2-256)."""
        self.palette_colors = max(2, min(256, int(colors)))

    def set_dither(self, dither):
        """Toggle dithering."""
        self.dither = bool(dither)

    def set_keep_animation(self, keep):
        """Toggle whether to keep animation."""
        self.keep_animation = bool(keep)

