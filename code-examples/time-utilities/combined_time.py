"""
Combined Time Utility

Kombiniert Unix Timestamp und Swatch Beat in einer Funktion.
"""

import datetime
from typing import Dict


def get_combined_time() -> Dict:
    """
    Gibt aktuelle Zeit als Unix Timestamp + Swatch Beat zurück.

    Returns:
        Dictionary mit unix, swatch_beat und formatierten Strings.
    """
    now = datetime.datetime.now(datetime.timezone.utc)

    # Unix Timestamp
    unix_ts = now.timestamp()

    # Swatch Beat berechnen
    seconds_since_midnight = (
        now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1_000_000
    )
    swatch_beat = (seconds_since_midnight / 86.4) % 1000

    return {
        "unix": unix_ts,
        "swatch_beat": round(swatch_beat, 2),
        "formatted": f"@ {swatch_beat:06.2f} | Unix: {unix_ts:.2f}",
        "datetime_utc": now.strftime("%Y-%m-%d %H:%M:%S")
    }


def print_combined_time():
    data = get_combined_time()
    print(f"Swatch Beat: @{data['swatch_beat']:06.2f}")
    print(f"Unix Timestamp: {data['unix']:.2f}")
    print(f"UTC: {data['datetime_utc']}")


if __name__ == "__main__":
    print_combined_time()