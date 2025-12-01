"""
Setup-Script für nodiView
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lese README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="nodiview",
    version="0.1.0",
    description="Ein moderner Linux-Bildbetrachter mit integrierter Bildoptimierung",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="nodiView Team",
    license="GPL-3.0",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "PyGObject>=3.42.0",
        "Pillow>=10.0.0",
        "pyvips>=2.2.0",
    ],
    entry_points={
        "console_scripts": [
            "nodiview=nodiview.main:main",
        ],
    },
    package_data={
        "nodiview": [
            "data/icons/*",
            "data/*.desktop",
            "data/*.appdata.xml",
        ],
    },
    data_files=[
        ("share/applications", ["data/nodiview.desktop"]),
        ("share/metainfo", ["data/nodiview.appdata.xml"]),
        ("share/icons/hicolor/scalable/apps", ["data/icons/nodiview.svg"]),
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Viewers",
    ],
)

