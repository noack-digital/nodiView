# nodiView

Ein moderner, schlanker Bildbetrachter für Linux mit integrierter Bildoptimierung.

## Features

- **Bildanzeige**: Unterstützung für gängige Bildformate (JPEG, PNG, GIF, WebP, TIFF, BMP, ICO, etc.)
- **Navigation**: Einfache Navigation zwischen Bildern im Ordner
- **Zoom**: Fit to Window, 100%, Custom Zoom
- **Grundlegende Bearbeitung**: Rotation, Spiegeln, Zuschneiden
- **Bildoptimierung**: 
  - JPEG-Optimierung mit Quality- und Chroma-Subsampling-Steuerung
  - PNG-Optimierung mit Komprimierungsoptionen
  - GIF-Optimierung
  - Größenänderung mit verschiedenen Interpolationsfiltern
- **Konvertierung**: Einzel- und Batch-Konvertierung zwischen verschiedenen Formaten
- **Batch-Operationen**: Mehrere Bilder gleichzeitig optimieren

## Installation

### Aus dem Quellcode

```bash
pip install -r requirements.txt
python -m nodiview
```

### Snap (geplant)

```bash
snap install nodiview
```

### Flatpak (geplant)

```bash
flatpak install nodiview
```

## Abhängigkeiten

- Python 3.10+
- GTK4
- libvips
- gdk-pixbuf

## Entwicklung

```bash
# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python -m nodiview
```

## Lizenz

GPL-3.0

