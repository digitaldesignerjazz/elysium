"""
Unix Timestamp Utility

Saubere und wiederverwendbare Funktionen für Unix-Zeitstempel in Python.
"""

import datetime
from typing import Optional, Union


def get_unix_timestamp(dt: Optional[datetime.datetime] = None) -> float:
    """
    Gibt den Unix-Timestamp zurück.

    Args:
        dt: Optionaler datetime. Wenn None, wird die aktuelle UTC-Zeit verwendet.

    Returns:
        Unix Timestamp als Float (Sekunden seit 1970-01-01 00:00:00 UTC)
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    return dt.timestamp()


def unix_to_datetime(timestamp: Union[int, float]) -> datetime.datetime:
    """
    Konvertiert einen Unix-Timestamp in ein datetime-Objekt (UTC).
    """
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def unix_to_readable(
    timestamp: Union[int, float], 
    fmt: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Gibt einen Unix-Timestamp als lesbaren String zurück.
    """
    dt = unix_to_datetime(timestamp)
    return dt.strftime(fmt)


def datetime_to_unix(dt: datetime.datetime) -> float:
    """
    Konvertiert ein datetime-Objekt in einen Unix-Timestamp.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.timestamp()


def get_current_readable(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Gibt die aktuelle Zeit als lesbaren String zurück."""
    return datetime.datetime.now(datetime.timezone.utc).strftime(fmt)


# ====================== Demo ======================
if __name__ == "__main__":
    import time

    print("Unix Timestamp Utility Demo")
    print("=" * 50)

    # Aktueller Timestamp
    now_ts = get_unix_timestamp()
    print(f"Aktueller Unix Timestamp: {now_ts}")
    print(f"Lesbar: {unix_to_readable(now_ts)}")

    print()

    # Beispiel-Konvertierung
    example_ts = 1710000000
    print(f"Beispiel Timestamp: {example_ts}")
    print(f"Als datetime: {unix_to_datetime(example_ts)}")
    print(f"Lesbar: {unix_to_readable(example_ts)}")

    print()
    print("Aktuelle Zeit (lesbar):", get_current_readable())

    # Warte 2 Sekunden und zeige neuen Timestamp
    print("\nWarte 2 Sekunden...")
    time.sleep(2)
    new_ts = get_unix_timestamp()
    print(f"Neuer Timestamp: {new_ts}")
    print(f"Differenz: {new_ts - now_ts:.2f} Sekunden")