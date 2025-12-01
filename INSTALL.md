# nodiView Installation

## System-Abhängigkeiten

nodiView benötigt einige System-Pakete, die über apt installiert werden müssen:

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

## Python-Abhängigkeiten

Nach der Installation der System-Abhängigkeiten können die Python-Pakete installiert werden:

### Option 1: Virtuelle Umgebung (empfohlen)

```bash
# Virtuelle Umgebung mit System-Paketen erstellen
# (wichtig: --system-site-packages für PyGObject)
python3 -m venv --system-site-packages venv

# Aktivieren
source venv/bin/activate

# Python-Pakete installieren
pip install Pillow pyvips

# Anwendung starten
python3 -m nodiview
```

### Option 2: Mit run.sh

```bash
# Start-Script ausführbar machen (falls noch nicht geschehen)
chmod +x run.sh

# Anwendung starten
./run.sh
```

## Entwicklung

Für die Entwicklung können Sie das Projekt installieren:

```bash
source venv/bin/activate
pip install -e .
```

Dann können Sie `nodiview` direkt aufrufen:

```bash
nodiview
```

## Fehlerbehebung

### "externally-managed-environment" Fehler

Ubuntu 24.04+ verwendet ein "externally-managed-environment". Verwenden Sie eine virtuelle Umgebung (siehe oben).

### PyGObject nicht gefunden

Stellen Sie sicher, dass die System-Abhängigkeiten installiert sind (siehe oben).

### libvips nicht gefunden

Installieren Sie `libvips-dev` und `libvips42t64`:

```bash
sudo apt-get install libvips-dev libvips42t64
```

