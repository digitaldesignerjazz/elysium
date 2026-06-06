# Swatch Beat Timekeeper

**Internet Time (© Swatch Beat) als Zeitgeber für Elysium.**

Dieses Tool berechnet die aktuelle Swatch Beat Zeit, basierend auf **00:00 UTC**.

## Was ist Swatch Beat?

Swatch Beat (auch Internet Time genannt) teilt den Tag in 1000 Beats.
- 1 Beat = 1 Minute 26,4 Sekunden
- Ein Tag hat 1000 Beats (@000 bis @999)
- Zeitzonen-unabhängig

Ursprünglich von Swatch entwickelt, um eine globale, einheitliche Zeit zu schaffen.

## Installation & Nutzung

```bash
cd code-examples/swatch-beat
python3 swatch_beat.py
```

Oder mit Argumenten:

```bash
python3 swatch_beat.py --live          # Live-Update alle 1.26 Sekunden
python3 swatch_beat.py --utc           # Zeigt UTC + Swatch Beat
```