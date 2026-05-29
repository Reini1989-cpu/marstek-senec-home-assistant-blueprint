# Marstek AUTO/MANUAL nach SENEC-Zustand – Home Assistant Blueprint  
# Marstek AUTO/MANUAL based on SENEC status – Home Assistant Blueprint

## Deutsch

Dieser Home-Assistant-Blueprint steuert einen **Marstek-Speicher** abhängig von Ladeleistung und Ladezustand (SOC) eines **SENEC-Speichers**. Grundsätzlich sollte der Blueprint auch mit **anderen Speichersystemen** funktionieren, sofern deren Ladezustand und Ladeleistung in Home Assistant über eine passende Integration oder API verfügbar sind und Scripts zum Umschalten des Marstek-Speichers bereitstehen.

### Funktion

Der Marstek-Speicher wird in den **AUTO-Modus** geschaltet, wenn mindestens eine der folgenden Bedingungen erfüllt ist:

- Der angeschlossene Referenzspeicher lädt stärker als der frei einstellbare Schwellenwert, Standard: `2300 W`
- Der Ladezustand des Referenzspeichers ist voll, Standard: `SOC >= 100 %`
- Der Ladezustand des Referenzspeichers ist leer, Standard: `SOC < 5 %`

Sind keine AUTO-Bedingungen erfüllt, wird der **MANUAL-Modus** aktiviert.

### Eigenschaften

- Kein unbeabsichtigtes Schalten bei `unknown` oder `unavailable` Sensorwerten
- Modusvergleich unabhängig von Groß-/Kleinschreibung (`Auto`, `AUTO`, `auto`)
- Einstellbare SOC-Schwellenwerte für „leer“ und „voll“
- Kein unnötiges erneutes Auslösen des gleichen Scripts
- Minütliche Prüfung des Systemzustands

### Voraussetzungen

- Home Assistant mit Blueprint-Unterstützung
- Sensor für die Ladeleistung des Referenzspeichers in Watt
- Sensor für den Ladezustand des Referenzspeichers in Prozent
- Sensor, der den aktuellen Marstek-Modus als `Auto` oder `Manual` bereitstellt
- Je ein Home-Assistant-Script zum Umschalten des Marstek-Speichers auf AUTO und MANUAL

Der Referenzspeicher kann ein SENEC-Speicher oder ein anderes kompatibles Speichersystem sein, dessen Werte in Home Assistant zur Verfügung stehen.

### Installation über GitHub

1. Öffne nach dem Upload die Datei  
   `blueprints/automation/marstek_senec/marstek_auto_manual_nach_senec_zustand.yaml`  
   in deinem GitHub-Repository.
2. Kopiere den Link zur Datei.
3. Öffne in Home Assistant **Einstellungen → Automatisierungen & Szenen → Blueprints**.
4. Wähle **Blueprint importieren** und füge den GitHub-Link ein.
5. Lege aus dem importierten Blueprint eine Automation an und wähle deine Sensoren sowie Scripts aus.

Alternativ kann die YAML-Datei manuell nach folgendem Pfad kopiert werden:

```text
/config/blueprints/automation/marstek_senec/marstek_auto_manual_nach_senec_zustand.yaml
```

### Konfiguration

| Eingabe | Beschreibung | Standard |
|---|---|---:|
| SENEC Ladeleistung | Aktuelle Ladeleistung des Referenzspeichers | erforderlich |
| SENEC SOC | Ladezustand des Referenzspeichers | erforderlich |
| Marstek Modus-Sensor | Liefert `Auto` oder `Manual` | erforderlich |
| Script für AUTO-Modus | Schaltet Marstek auf AUTO | erforderlich |
| Script für MANUAL-Modus | Schaltet Marstek auf MANUAL | erforderlich |
| Ladeleistungs-Schwellenwert | AUTO bei Überschreitung | 2300 W |
| SOC Leer-Schwellenwert | AUTO unterhalb dieses SOC | 5 % |
| SOC Voll-Schwellenwert | AUTO ab diesem SOC | 100 % |

Beispiel-Scripts findest du unter [`examples/scripts.yaml`](examples/scripts.yaml). Die Entity-IDs müssen an deine Installation angepasst werden.

### Datenschutz und Sicherheit

Der veröffentlichte Blueprint enthält keine Zugangsdaten, IP-Adressen oder persönlichen Entity-IDs. Veröffentliche niemals deine vollständige `secrets.yaml`, Tokens, Kennwörter oder Home-Assistant-Backups in einem öffentlichen Repository.

### Haftungshinweis

Die Nutzung erfolgt auf eigene Verantwortung. Prüfe die Schaltlogik zunächst kontrolliert und überwache das Verhalten deines Speichersystems, bevor du sie dauerhaft produktiv einsetzt.

---

## English

This Home Assistant blueprint controls a **Marstek battery storage system** based on the charging power and state of charge (SOC) of a **SENEC battery storage system**. In principle, the blueprint should also work with **other storage systems**, provided that their charging power and SOC are exposed to Home Assistant through a suitable integration or API and scripts are available to switch the Marstek system between modes.

### Function

The Marstek battery is switched to **AUTO mode** when at least one of the following conditions is met:

- The connected reference storage system is charging above the configurable threshold, default: `2300 W`
- The reference storage system is full, default: `SOC >= 100%`
- The reference storage system is empty, default: `SOC < 5%`

If none of the AUTO conditions are met, **MANUAL mode** is activated.

### Features

- No unintended switching when sensor states are `unknown` or `unavailable`
- Case-insensitive mode comparison (`Auto`, `AUTO`, `auto`)
- Configurable SOC thresholds for empty and full states
- No unnecessary repeated execution of the same script
- System status checked every minute

### Requirements

- Home Assistant with blueprint support
- Sensor providing the reference battery's charging power in watts
- Sensor providing the reference battery's state of charge in percent
- Sensor providing the current Marstek mode as `Auto` or `Manual`
- One Home Assistant script each for switching the Marstek battery to AUTO and MANUAL

The reference battery may be a SENEC system or another compatible storage system whose values are available in Home Assistant.

### Installation via GitHub

1. After uploading, open  
   `blueprints/automation/marstek_senec/marstek_auto_manual_nach_senec_zustand.yaml`  
   in your GitHub repository.
2. Copy the link to the file.
3. In Home Assistant, open **Settings → Automations & scenes → Blueprints**.
4. Select **Import blueprint** and paste the GitHub link.
5. Create an automation from the imported blueprint and select your sensors and scripts.

Alternatively, copy the YAML file manually to:

```text
/config/blueprints/automation/marstek_senec/marstek_auto_manual_nach_senec_zustand.yaml
```

### Configuration

| Input | Description | Default |
|---|---|---:|
| SENEC charging power | Current charging power of the reference battery | required |
| SENEC SOC | State of charge of the reference battery | required |
| Marstek mode sensor | Provides `Auto` or `Manual` | required |
| AUTO mode script | Switches Marstek to AUTO | required |
| MANUAL mode script | Switches Marstek to MANUAL | required |
| Charging power threshold | Activates AUTO above this value | 2300 W |
| Empty SOC threshold | Activates AUTO below this SOC | 5% |
| Full SOC threshold | Activates AUTO at or above this SOC | 100% |

Example scripts are available in [`examples/scripts.yaml`](examples/scripts.yaml). Adjust the entity IDs to match your installation.

### Privacy and security

The published blueprint does not contain credentials, IP addresses or personal entity IDs. Never publish your complete `secrets.yaml`, tokens, passwords or Home Assistant backups in a public repository.

### Disclaimer

Use this blueprint at your own risk. Test the switching logic carefully and monitor the behaviour of your storage system before using it permanently in production.

---

## License / Lizenz

Dieses Projekt steht unter der MIT-Lizenz. / This project is licensed under the MIT License.
