# nodiView

A modern, lightweight image viewer for Linux with integrated image optimization capabilities.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GTK4](https://img.shields.io/badge/GTK-4.0-green.svg)](https://www.gtk.org/)

nodiView is a feature-rich image viewer built with GTK4 and Libadwaita, providing a modern interface for viewing, editing, and optimizing images on Linux systems.

## Features

### Image Viewing
- **Format Support**: JPEG, PNG, GIF, WebP, TIFF, BMP, ICO, and more
- **Navigation**: Easy navigation between images in folders
- **Zoom Controls**:
  - Fit to window
  - 100% (actual size)
  - Custom zoom levels (10% - 500%)
  - Synchronized zoom for side-by-side comparison
- **Fullscreen Mode**: Distraction-free viewing

### Image Optimization
- **JPEG Optimization**:
  - Quality control (1-100)
  - Chroma subsampling options (4:4:4, 4:2:2, 4:2:0, 4:1:1)
  - Progressive JPEG support
  - Grayscale conversion
  - EXIF metadata preservation

- **PNG Optimization**:
  - Compression level control (0-9)
  - Color palette reduction
  - Alpha channel handling
  - Interlaced PNG support

- **GIF Optimization**:
  - Color palette reduction
  - Color count control
  - Dithering options
  - Animation preservation

- **Image Resizing**:
  - Proportional scaling
  - Percentage-based resizing
  - Multiple interpolation filters:
    - Nearest Neighbor
    - Bilinear
    - Bicubic (Mitchell-Netravali)
    - Bicubic (Catmull-Rom)
    - B-Spline
    - Lanczos3

### Comparison View
- Side-by-side comparison of original and optimized images
- Synchronized zoom for easy comparison
- Real-time file size information
- Savings calculation (KB/MB and percentage)

### Basic Editing
- **Rotation**: 90°, 180°, 270°
- **Mirroring**: Horizontal and vertical flip
- **Cropping**: Select and crop image regions

### Format Conversion
- Convert between different image formats
- Batch conversion support
- Quality and optimization settings per format

### Batch Operations
- Process multiple images simultaneously
- Batch optimization with consistent settings
- Progress tracking

### Multilingual Support
- English (default)
- German (Deutsch)
- Spanish (Español)
- French (Français)
- Ukrainian (Українська)

## Screenshots

_Coming soon_

## Installation

### Distribution Packages

#### Snap

Install from the Snap Store (coming soon):
```bash
sudo snap install nodiview
```

Or build from source:
```bash
sudo snap install snapcraft --classic
snapcraft
sudo snap install ./nodiview_*.snap --dangerous
```

#### Flatpak

Install from Flathub (coming soon):
```bash
flatpak install flathub org.noackdigital.nodiView
```

Or build from source:
```bash
flatpak-builder --force-clean --install build-dir org.noackdigital.nodiView.yml
```

### System Dependencies

nodiView requires several system packages. Install them using apt:

```bash
sudo apt-get install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1 \
    libvips-dev \
    libgirepository1.0-dev \
    pkg-config \
    python3-dev
```

### From Source

#### Option 1: Using Virtual Environment (Recommended)

```bash
# Create virtual environment with system packages
# (important: --system-site-packages for PyGObject)
python3 -m venv --system-site-packages venv

# Activate
source venv/bin/activate

# Install Python packages
pip install Pillow pyvips

# Run application
python3 -m nodiview
```

#### Option 2: Using run.sh

```bash
# Make script executable (if not already)
chmod +x run.sh

# Run application
./run.sh
```

### Development Installation

For development, install the package in editable mode:

```bash
source venv/bin/activate
pip install -e .
```

Then you can run `nodiview` directly:

```bash
nodiview
```

## Usage

### Starting the Application

```bash
# Using the module
python3 -m nodiview

# Or using the script
./run.sh

# If installed in development mode
nodiview
```

### Opening Images

1. Click **"Open image"** in the menu
2. Navigate to your image file
3. Select and open

### Optimizing Images

1. Open an image
2. Click **"Optimize"** in the menu
3. Adjust optimization settings:
   - Choose output format (JPEG, PNG, GIF)
   - Adjust format-specific settings
   - Configure resize options if needed
4. Click **"Generate preview"** to see the result
5. Use the zoom controls to compare original and optimized versions
6. Click **"Save"** to save the optimized image

### Changing Language

1. Open **Settings** menu
2. Select **Language**
3. Choose your preferred language
4. Restart nodiView to apply changes

## Requirements

- Python 3.10 or higher
- GTK4
- Libadwaita 1.0
- libvips
- gdk-pixbuf
- Pillow (PIL)
- pyvips

## Project Structure

```
nodiview/
├── nodiview/           # Main application package
│   ├── __main__.py     # Application entry point
│   ├── main.py         # Main application class
│   ├── window.py       # Main window implementation
│   ├── image_viewer.py # Image viewer widget
│   ├── optimization_dialog.py  # Optimization dialog
│   ├── i18n.py         # Internationalization
│   ├── settings.py     # Settings dialog
│   ├── optimizer/      # Image optimization modules
│   ├── editor/         # Image editing modules
│   ├── converter/      # Format conversion
│   ├── batch/          # Batch processing
│   └── utils/          # Utility functions
├── data/               # Application data (icons, desktop files)
├── requirements.txt    # Python dependencies
├── setup.py           # Package setup
├── run.sh             # Convenience run script
└── README.md          # This file
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/noack-digital/nodiView.git
cd nodiView

# Create virtual environment
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the application
nodiview
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Write docstrings for classes and functions
- Keep functions focused and modular
- All code and comments must be in English

### Adding Translations

To add a new language:

1. Edit `nodiview/i18n.py`
2. Add language code to `SUPPORTED_LANGUAGES`
3. Add translations to `TRANSLATIONS` dictionary
4. Submit a pull request

## Troubleshooting

### "externally-managed-environment" Error

Ubuntu 24.04+ uses an "externally-managed-environment". Use a virtual environment (see installation instructions above).

### PyGObject Not Found

Make sure system dependencies are installed:
```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

### libvips Not Found

Install libvips development package:
```bash
sudo apt-get install libvips-dev libvips42t64
```

### Chroma Subsampling Error

If you encounter errors with chroma subsampling (e.g., "no value 4:2:0 in gtype"), ensure you have the latest version of pyvips:
```bash
pip install --upgrade pyvips
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [GTK4](https://www.gtk.org/) and [Libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- Image processing powered by [libvips](https://libvips.github.io/libvips/) and [Pillow](https://pypi.org/project/pillow/)
- Icons from [GNOME Icon Library](https://gitlab.gnome.org/Teams/Design/icon-library)

## Author

**noack-digital**
- Website: [https://noack-digital.de](https://noack-digital.de)
- GitHub: [@noack-digital](https://github.com/noack-digital)
