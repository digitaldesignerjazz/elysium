"""
Swatch Beat-basierter Scheduler für AI-Agents

Ermöglicht das Planen von Aufgaben basierend auf Swatch Beat Zeit.

Beispiele:
    - Alle 50 Beats eine Statusmeldung senden
    - Um @500 automatisch Daten abfragen
    - Alle 100 Beats eine Payment-Transaktion triggern
"""

import time
from typing import Callable, List, Dict


class SwatchBeatScheduler:
    def __init__(self):
        self.jobs: List[Dict] = []

    def every(self, beats: float, func: Callable, name: str = None):
        """Plant eine wiederkehrende Aufgabe alle X Beats."""
        self.jobs.append({
            "type": "interval",
            "interval": beats,
            "last_run": 0.0,
            "func": func,
            "name": name or func.__name__
        })

    def at(self, beat_time: float, func: Callable, name: str = None):
        """Plant eine Aufgabe zu einem bestimmten Swatch Beat Zeitpunkt (z.B. @500)."""
        self.jobs.append({
            "type": "at",
            "target_beat": beat_time % 1000,
            "func": func,
            "name": name or func.__name__,
            "executed_today": False
        })

    def _get_current_beat(self) -> float:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        return (seconds / 86.4) % 1000

    def run(self, check_interval: float = 1.0):
        """Startet den Scheduler (blockierend)."""
        print("[SwatchBeatScheduler] Gestartet...")

        while True:
            current_beat = self._get_current_beat()

            for job in self.jobs:
                if job["type"] == "interval":
                    if current_beat - job["last_run"] >= job["interval"]:
                        print(f"[Scheduler] Running: {job['name']} @ {current_beat:.2f}")
                        job["func"]()
                        job["last_run"] = current_beat

                elif job["type"] == "at":
                    # Führt aus, wenn wir den Ziel-Beat erreichen (innerhalb von ~1 Beat Toleranz)
                    if (not job.get("executed_today", False) and
                            abs(current_beat - job["target_beat"]) < 1.0):
                        print(f"[Scheduler] Running scheduled job: {job['name']} @ {current_beat:.2f}")
                        job["func"]()
                        job["executed_today"] = True

            # Reset daily flags at @000
            if current_beat < 1.0:
                for job in self.jobs:
                    if job["type"] == "at":
                        job["executed_today"] = False

            time.sleep(check_interval)


# ====================== Beispiel-Nutzung ======================
if __name__ == "__main__":
    scheduler = SwatchBeatScheduler()

    def status_report():
        print("   → Status Report: Alles OK")

    def soilnova_check():
        print("   → Soilnova Daten abgefragt")

    # Alle 50 Beats einen Status Report
    scheduler.every(50, status_report, name="StatusReport")

    # Um @500 Soilnova-Daten abfragen
    scheduler.at(500, soilnova_check, name="SoilnovaCheck")

    print("Starte Swatch Beat Scheduler... (Strg+C zum Beenden)")
    scheduler.run(check_interval=2.0)  # Alle 2 Sekunden prüfen