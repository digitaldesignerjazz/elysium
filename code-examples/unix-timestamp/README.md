# Unix Timestamp Utility (Python)

Einfache und wiederverwendbare Funktionen zum Arbeiten mit Unix-Zeitstempeln.

## Funktionen

- Aktuellen Unix-Timestamp holen
- `datetime` ↔ Unix Timestamp konvertieren
- Lesbare Datums-/Zeitdarstellung

## Nutzung

```bash
cd code-examples/unix-timestamp
python3 unix_timestamp.py
```

Oder als Modul:

```python
from unix_timestamp import get_unix_timestamp, unix_to_datetime

print(get_unix_timestamp())
print(unix_to_datetime(1710000000))
```