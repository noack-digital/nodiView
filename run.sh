#!/bin/bash
# nodiView Start-Script

cd "$(dirname "$0")"

# Aktiviere virtuelle Umgebung wenn vorhanden
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Starte Anwendung
python3 -m nodiview "$@"

