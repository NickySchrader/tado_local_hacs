# Tado Local - HACS Integration für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/NickySchrader/tado_local_hacs.svg)](https://GitHub.com/NickySchrader/tado_local_hacs/releases/)

**Lokale Steuerung deines Tado Smart Heating Systems ohne Cloud-Abhängigkeiten!**

Diese Custom Component ermöglicht die direkte lokale Kommunikation mit deinem Tado-System über das HomeKit-Protokoll. Keine Rate-Limits, keine Cloud-Verzögerungen, instant Response-Zeiten.

## ✨ Features

- 🔌 **Lokale Kontrolle** - Direkte Kommunikation mit der Tado Bridge über HomeKit-Protokoll
- ⚡ **Schnelle Reaktion** - Keine Cloud-Verzögerungen
- 🌡️ **Vollständige Integration** - Climate und Sensor Entities
- 🔄 **Echtzeit-Updates** - SSE-Stream für sofortige Statusänderungen
- 💾 **Historische Daten** - SQLite-Datenbank mit kompletter State-Historie
- 🎨 **Config Flow** - Einfache Einrichtung über die UI

## 📋 Voraussetzungen

Bevor du die Integration installierst, musst du den **Tado Local Server** einrichten und starten. Dieser Server bildet die Brücke zwischen deiner Tado Bridge und Home Assistant.

### Tado Local Server Installation

1. **Anforderungen:**
   - Python 3.11 oder höher
   - Tado Bridge IP-Adresse (in deinem Router nachsehen)
   - HomeKit PIN (Aufkleber auf der Tado Bridge, Format: XXX-XX-XXX)

2. **Installation:**

   ```bash
   # Repository klonen
   git clone https://github.com/NickySchrader/tado_local_hacs.git
   cd tado_local_hacs

   # Installieren
   pip install -e .
   ```

3. **Erste Einrichtung:**

   ```bash
   # Server starten
   python -m tado_local --bridge-ip <DEINE_BRIDGE_IP> --pin <DEIN_PIN>
   ```

4. **Tado OAuth Authentifizierung:**
   - Beim ersten Start zeigt der Server eine URL an
   - Öffne diese URL und melde dich mit deinem Tado-Account an
   - Nach erfolgreicher Authentifizierung läuft der Server

5. **Server im Hintergrund laufen lassen:**
   ```bash
   # Mit systemd (empfohlen für Linux)
   sudo cp systemd/tado-local.service /etc/systemd/system/
   sudo systemctl enable tado-local
   sudo systemctl start tado-local
   ```

Detaillierte Anweisungen findest du im [Hauptrepository](https://github.com/NickySchrader/tado_local_hacs).

## 📦 Installation via HACS

### HACS Installation

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrationen"
3. Klicke auf die drei Punkte oben rechts
4. Wähle "Benutzerdefinierte Repositories"
5. Füge die Repository-URL hinzu: `https://github.com/NickySchrader/tado_local_hacs`
6. Wähle Kategorie: "Integration"
7. Klicke auf "Hinzufügen"
8. Suche nach "Tado Local" und klicke auf "Herunterladen"
9. Starte Home Assistant neu

### Manuelle Installation

1. Kopiere den `custom_components/tado_local` Ordner in dein `config/custom_components` Verzeichnis
2. Starte Home Assistant neu

## ⚙️ Konfiguration

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ Integration hinzufügen**
3. Suche nach **Tado Local**
4. Gib die Details deines Tado Local Servers ein:
   - **Host**: `localhost` (wenn auf demselben System) oder die IP des Servers
   - **Port**: `8000` (Standard)
5. Klicke auf **Absenden**

Die Integration erstellt automatisch:

- Climate Entities für alle Zonen
- Temperature Sensors
- Humidity Sensors (falls verfügbar)

## 🎯 Verwendung

Nach der Einrichtung erscheinen alle deine Tado-Zonen als Climate-Entities in Home Assistant:

```yaml
# Beispiel Automation
automation:
  - alias: "Morgens Heizung an"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      service: climate.set_temperature
      target:
        entity_id: climate.wohnzimmer
      data:
        temperature: 21
```

## 📊 Entities

Die Integration erstellt folgende Entity-Typen:

- **Climate**: Steuerung von Temperatur und HVAC-Modi
- **Sensor**: Aktuelle Temperatur und Luftfeuchtigkeit

## 🐛 Fehlersuche

### Integration findet den Server nicht

- Überprüfe, ob der Tado Local Server läuft
- Teste die Verbindung: `curl http://localhost:8000/health`
- Überprüfe Firewall-Einstellungen

### Keine Zonen werden angezeigt

- Stelle sicher, dass die Tado OAuth-Authentifizierung erfolgreich war
- Überprüfe die Logs des Tado Local Servers
- Prüfe die Home Assistant Logs unter **Einstellungen** → **System** → **Protokolle**

## 🔗 Links

- [Tado Local Repository](https://github.com/NickySchrader/tado_local_hacs)
- [Dokumentation](https://github.com/NickySchrader/tado_local_hacs#readme)
- [Issue Tracker](https://github.com/NickySchrader/tado_local_hacs/issues)

## 📝 Lizenz

Apache License 2.0 - siehe [LICENSE](LICENSE) Datei

## 🙏 Credits

Diese Integration verwendet:

- [aiohomekit](https://github.com/Jc2k/aiohomekit) für HomeKit-Protokoll-Kommunikation
- [FastAPI](https://fastapi.tiangolo.com/) für den REST API Server
- Das großartige Tado-System von tado GmbH

---

**Hinweis**: Dies ist ein Community-Projekt und steht in keiner Verbindung mit der tado GmbH.
