"""
Swatch Beat (Internet Time) Implementation in Python

Basiert auf 00:00 UTC wie gewünscht.
Kann als Script oder als Modul verwendet werden.

Beispiel:
    from swatch_beat import get_swatch_beat, format_beat
    print(format_beat(get_swatch_beat()))
"""

import datetime
from typing import Optional


def get_swatch_beat(dt: Optional[datetime.datetime] = None) -> float:
    """
    Berechnet die aktuelle Swatch Beat Zeit.

    Args:
        dt: Optionaler datetime (muss UTC-aware sein). Wenn None, wird aktuelle UTC-Zeit verwendet.

    Returns:
        Swatch Beat als Float zwischen 0.0 und 999.999
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    elif dt.tzinfo is None:
        # Falls naive datetime übergeben wird, als UTC interpretieren
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    # Sekunden seit Mitternacht UTC
    seconds_since_midnight = (
        dt.hour * 3600 +
        dt.minute * 60 +
        dt.second +
        dt.microsecond / 1_000_000
    )

    # 86400 Sekunden = 1000 Beats → 1 Beat = 86.4 Sekunden
    beats = (seconds_since_midnight / 86.4) % 1000
    return beats


def format_beat(beat: float, precision: int = 2) -> str:
    """
    Formatiert die Beat-Zeit im klassischen @XXX.XX Format.

    Args:
        beat: Swatch Beat Wert
        precision: Anzahl Nachkommastellen

    Returns:
        Formatierter String, z.B. '@337.45'
    """
    return f"@{beat:0{3 + precision + 1}.{precision}f}"


def get_current_beat_string(precision: int = 2) -> str:
    """Gibt die aktuelle Swatch Beat Zeit als formatierten String zurück."""
    return format_beat(get_swatch_beat(), precision=precision)


# ====================== CLI ======================
if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Swatch Beat Timekeeper (UTC-basiert)")
    parser.add_argument("--live", action="store_true", help="Live-Update Modus")
    parser.add_argument("--utc", action="store_true", help="Zeigt zusätzlich UTC-Zeit")
    parser.add_argument("--precision", type=int, default=2, help="Nachkommastellen (default: 2)")

    args = parser.parse_args()

    print("Swatch Beat \u2013 basierend auf 00:00 UTC")
    print("=" * 55)

    try:
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            beat_str = format_beat(get_swatch_beat(now), precision=args.precision)

            output = f"Swatch Beat: {beat_str}"
            if args.utc:
                output += f"   |   UTC: {now.strftime('%H:%M:%S')}"

            print(output, end="\r" if not args.live else "\n")

            if args.live:
                # Warte ca. 1 Beat (86.4 Sekunden / 1000 * 10 für häufigeres Update)
                time.sleep(1.0)
            else:
                break

    except KeyboardInterrupt:
        print("\n\nBeendet.")