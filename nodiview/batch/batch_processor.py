"""
Batch processing helpers.
"""

import os
from pathlib import Path
from ..converter.image_converter import ImageConverter
from ..optimizer.jpeg_optimizer import JPEGOptimizer
from ..optimizer.png_optimizer import PNGOptimizer
from ..optimizer.gif_optimizer import GIFOptimizer
from ..optimizer.resize import ImageResizer


class BatchProcessor:
    """Run conversions, optimizations, and resizes on multiple files."""

    def __init__(self):
        self.progress_callback = None

    def convert_batch(
        self, input_files, output_dir, output_format, quality=85, optimize=True
    ):
        """
        Convert several images to the same format.

        Args:
            input_files: Iterable of input paths.
            output_dir: Destination directory.
            output_format: Target format.
            quality: Quality for lossy formats.
            optimize: Enable encoder optimizations.

        Returns:
            List of generated files.
        """
        converter = ImageConverter()
        converter.set_quality(quality)
        converter.set_optimize(optimize)

        converted_files = []
        total = len(input_files)

        for i, input_file in enumerate(input_files):
            if self.progress_callback:
                self.progress_callback(i, total, f"Konvertiere {os.path.basename(input_file)}")

            # Bestimme Ausgabedateiname
            base_name = Path(input_file).stem
            ext = ImageConverter.SUPPORTED_FORMATS.get(output_format, ["png"])[0]
            output_file = os.path.join(output_dir, f"{base_name}.{ext}")

            # Konvertiere
            result = converter.convert(input_file, output_file, output_format)
            if result:
                converted_files.append(result)

        if self.progress_callback:
            self.progress_callback(total, total, "Fertig")

        return converted_files

    def optimize_batch(
        self,
        input_files,
        output_dir=None,
        jpeg_quality=85,
        jpeg_chroma="medium",
        png_compression=6,
        gif_reduce_palette=True,
    ):
        """
        Optimize multiple images according to their format.

        Args:
            input_files: List of input files.
            output_dir: Optional output directory (overwrite if None).
            jpeg_quality: JPEG quality.
            jpeg_chroma: JPEG chroma subsampling.
            png_compression: PNG compression level.
            gif_reduce_palette: Toggle GIF palette reduction.

        Returns:
            List of optimized files.
        """
        optimized_files = []
        total = len(input_files)

        for i, input_file in enumerate(input_files):
            if self.progress_callback:
                self.progress_callback(
                    i, total, f"Optimiere {os.path.basename(input_file)}"
                )

            # Bestimme Format
            ext = os.path.splitext(input_file)[1].lower()

            # Bestimme Ausgabedatei
            if output_dir:
                output_file = os.path.join(output_dir, os.path.basename(input_file))
            else:
                output_file = input_file

            # Optimiere je nach Format
            result = None
            if ext in (".jpg", ".jpeg"):
                optimizer = JPEGOptimizer()
                optimizer.set_quality(jpeg_quality)
                optimizer.set_chroma_subsampling(jpeg_chroma)
                result = optimizer.optimize(input_file, output_file)
            elif ext == ".png":
                optimizer = PNGOptimizer()
                optimizer.set_compression_level(png_compression)
                result = optimizer.optimize(input_file, output_file)
            elif ext == ".gif":
                optimizer = GIFOptimizer()
                optimizer.set_reduce_palette(gif_reduce_palette)
                result = optimizer.optimize(input_file, output_file)

            if result:
                optimized_files.append(result)

        if self.progress_callback:
            self.progress_callback(total, total, "Fertig")

        return optimized_files

    def resize_batch(
        self,
        input_files,
        output_dir,
        width=None,
        height=None,
        scale=None,
        filter_name="lanczos3",
    ):
        """
        Resize multiple images.

        Args:
            input_files: Sequence of files.
            output_dir: Destination directory.
            width: Optional width.
            height: Optional height.
            scale: Optional scale factor.
            filter_name: Interpolation filter.

        Returns:
            List of resized files.
        """
        resizer = ImageResizer()
        resizer.set_filter(filter_name)

        resized_files = []
        total = len(input_files)

        for i, input_file in enumerate(input_files):
            if self.progress_callback:
                self.progress_callback(
                    i, total, f"Skaliere {os.path.basename(input_file)}"
                )

            output_file = os.path.join(output_dir, os.path.basename(input_file))
            result = resizer.resize(input_file, output_file, width, height, scale)

            if result:
                resized_files.append(result)

        if self.progress_callback:
            self.progress_callback(total, total, "Fertig")

        return resized_files

    def set_progress_callback(self, callback):
        """Register a callback to report progress."""
        self.progress_callback = callback

