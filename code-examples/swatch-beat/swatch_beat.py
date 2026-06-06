"""
Swatch Beat Timekeeper

Berechnet Swatch Beat Zeit basierend auf 00:00 UTC.
"""

import datetime
import time
import argparse


def get_swatch_beat(dt: datetime.datetime = None) -> float:
    """Berechnet die aktuelle Swatch Beat Zeit (0.0 - 999.999)."""
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)

    # Swatch Beat basiert auf UTC (wie vom User gewünscht)
    # Mitternacht UTC = @000
    seconds_since_midnight = (
        dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1_000_000
    )

    # 1 Tag = 86400 Sekunden = 1000 Beats
    # 1 Beat = 86.4 Sekunden
    beats = (seconds_since_midnight / 86.4) % 1000
    return beats


def format_beat(beat: float) -> str:
    """Formatiert die Beat-Zeit als @XXX.XX"""
    return f"@{beat:06.2f}"


def main():
    parser = argparse.ArgumentParser(description="Swatch Beat Timekeeper (UTC-basiert)")
    parser.add_argument("--live", action="store_true", help="Live-Update alle ~1.26 Sekunden")
    parser.add_argument("--utc", action="store_true", help="Zeigt zusätzlich die UTC-Zeit")
    args = parser.parse_args()

    print("Swatch Beat Timekeeper (basiert auf 00:00 UTC)")
    print("=" * 50)

    try:
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            beat = get_swatch_beat(now)

            output = f"Swatch Beat: {format_beat(beat)}"

            if args.utc:
                output += f"   |   UTC: {now.strftime('%H:%M:%S')}"

            print(output, end="\r" if not args.live else "\n")

            if args.live:
                time.sleep(1.264)  # ca. 1 Beat
            else:
                break

    except KeyboardInterrupt:
        print("\n\nBeendet.")


if __name__ == "__main__":
    main()