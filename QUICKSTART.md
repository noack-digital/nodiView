# nodiView - Schnellstart

## Installation und Start

1. **System-Abhängigkeiten installieren** (einmalig):
```bash
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 libvips-dev libgirepository1.0-dev pkg-config python3-dev
```

2. **Virtuelle Umgebung erstellen und aktivieren**:
```bash
cd /home/anoack/nodiview
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install Pillow pyvips
```

3. **Anwendung starten**:
```bash
python3 -m nodiview
```

Oder verwenden Sie das Start-Script:
```bash
./run.sh
```

## Verwendung

- **Datei öffnen**: Klicken Sie auf das Ordner-Icon oder verwenden Sie Strg+O
- **Navigation**: Pfeiltasten oder Buttons für Vorheriges/Nächstes Bild
- **Zoom**: Strg + Mausrad oder Gesten
- **Optimieren**: Klicken Sie auf das Bearbeiten-Icon
- **Bearbeiten**: Menü "Bearbeiten" für Rotation und Spiegeln

Viel Erfolg!
