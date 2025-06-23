# ⚡ Henne CLI — Benutzer-Dokumentation

**Henne** ist ein interaktives Kommandozeilenprogramm in Python, das dem Benutzer vordefinierte Fragen stellt, die aus einer YAML-Datei geladen werden. Es unterstützt die Fragetypen `confirm` (Ja/Nein) und `select` (Auswahlliste).

## 📦 Voraussetzungen

Stellen Sie sicher, dass Python installiert ist und installieren Sie die benötigten Pakete:

```bash
pip install questionary pyyaml
```

## 🚀 Anwendung starten

Führen Sie das Programm mit folgendem Befehl im Terminal aus:

```bash
python main.py
```

💡 Falls Ihre Datei anders heißt, passen Sie den Namen entsprechend an.

## ⚙️ Konfigurationsdatei (config.yaml)

Die Fragen werden aus einer YAML-Datei geladen. Die Datei muss eine Liste mit dem Schlüssel questions enthalten. Jede Frage muss bestimmte Felder enthalten, je nach Typ.

### ✅ Unterstützte Fragetypen

Typ	Beschreibung	Erforderliche Felder
confirm	Ja/Nein-Frage	type, name, message
select	Benutzer wählt eine Option	type, name, message, choices

### 📄 Beispiel: config.yaml

```yaml
questions:
  - type: confirm
    name: elektrika
    message: "Sind sie ein intellenta Elektrika?"

  - type: select
    name: language
    message: "Was willst du tun?"
    choices:
      - Phase inne Nase
      - Neutral fatal
```

## 🧪 Beispielhafte Benutzereingabe

Beim Start des Programms wird der Benutzer wie folgt befragt:

```bash
? Sind sie ein intellenta Elektrika? (Y/n)

? Was willst du tun?  (Pfeiltasten benutzen)
❯ Phase inne Nase
  Neutral fatal
```

## 📥 Ausgabeformat

Die Antworten werden aktuell als Liste im Terminal ausgegeben:

```python
[True, 'Phase inne Nase']
```

⚠️ Die Antworten erscheinen in derselben Reihenfolge wie in der YAML-Datei. Wenn Sie eine benannte Ausgabe im Format {name: antwort} bevorzugen, lässt sich der Code entsprechend anpassen.

## ❗ Fehlerbehandlung & Validierung

Das Programm prüft die Struktur der YAML-Datei und bricht mit einer Fehlermeldung ab, wenn:

- Die Datei fehlt oder ungültig ist
- Fragen unvollständig sind (fehlende type, name, message)
- Ein nicht unterstützter Fragetyp verwendet wird
- Eine select-Frage keine gültige choices-Liste enthält

## 📚 Integrationsanleitung: Nutzung von get_user_settings in deiner Anwendung

Um die YAML-basierte CLI-Fragenfunktion in deinem eigenen Python-Programm zu verwenden, kopiere den Code (alles außer dem Block mit if __name__ == "__main__":) aus dem bereitgestellten Skript in dein Projekt. Dazu gehören:

- validate_question_schema
- load_questions_from_yaml
- ask_questions_and_get_answers
- get_user_settings

Rufe get_user_settings(yaml_path) auf, an der Stelle, an der du den Benutzer befragen möchtest. Übergebe den Pfad zur YAML-Konfigurationsdatei.

Beispiel:

```python
answers = get_user_settings("pfad/zur/config.yaml")
print("User-Answers:", annswers)
```

Verarbeite die zurückgegebenen Antworten, welche aktuell als Liste in der Reihenfolge der YAML-Fragen geliefert werden.
