"""
Swatch Beat Scheduler + XCoin Automatic Payments (mit Bedingungen)

Erweiterte Version mit Conditional Logic ähnlich wie Smart Contracts.

Mögliche Bedingungen:
- Qualitätsscore
- Guthaben
- Agent-Status
- Zeitbasierte Regeln
"""

import time
from typing import Callable, Optional


class SimpleXCoinWallet:
    """Minimaler XCoin Wallet für Demo-Zwecke."""

    def __init__(self, address: str, balance: float = 1000.0):
        self.address = address
        self.balance = balance
        self.history = []

    def send(self, to: str, amount: float, memo: str = ""):
        if amount > self.balance:
            print(f"[{self.address}] Nicht genug Guthaben!")
            return False

        self.balance -= amount
        self.history.append({
            "type": "send",
            "to": to,
            "amount": amount,
            "memo": memo
        })
        print(f"[{self.address}] ✓ {amount} XCoin an {to} gesendet ({memo})")
        return True

    def receive(self, from_addr: str, amount: float, memo: str = ""):
        self.balance += amount
        self.history.append({
            "type": "receive",
            "from": from_addr,
            "amount": amount,
            "memo": memo
        })
        print(f"[{self.address}] ✓ {amount} XCoin von {from_addr} empfangen ({memo)})")

    def get_balance(self):
        return self.balance


class ConditionalSwatchBeatScheduler:
    """
    Erweiterter Scheduler mit Bedingungslogik (Smart Contract Style).
    """

    def __init__(self):
        self.jobs = []
        self.wallets = {}

    def register_wallet(self, wallet: SimpleXCoinWallet):
        self.wallets[wallet.address] = wallet

    def schedule_conditional_payment(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        condition: Optional[Callable[[], bool]] = None,
        interval_beats: float = None,
        at_beat: float = None,
        memo: str = ""
    ):
        """
        Plant eine bedingte automatische Zahlung.

        Args:
            condition: Funktion, die True oder False zurückgibt.
                       Wenn None, wird immer ausgeführt.
        """
        job = {
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "memo": memo,
            "condition": condition,
            "type": "conditional_payment"
        }

        if interval_beats:
            job["interval"] = interval_beats
            job["last_run"] = 0.0
        elif at_beat is not None:
            job["target_beat"] = at_beat % 1000
            job["executed_today"] = False

        self.jobs.append(job)

    def _get_current_beat(self) -> float:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        return (seconds / 86.4) % 1000

    def run(self, check_interval: float = 2.0):
        print("[Conditional Payment Scheduler] Gestartet...\n")

        while True:
            current_beat = self._get_current_beat()

            for job in self.jobs:
                # Prüfe Bedingung (falls vorhanden)
                condition_met = True
                if job.get("condition"):
                    try:
                        condition_met = job["condition"]()
                    except Exception as e:
                        print(f"[Scheduler] Fehler bei Bedingung: {e}")
                        condition_met = False

                if not condition_met:
                    continue

                if job.get("interval"):
                    if current_beat - job.get("last_run", 0) >= job["interval"]:
                        self._execute_payment(job)
                        job["last_run"] = current_beat

                elif job.get("target_beat") is not None:
                    if (not job.get("executed_today", False) and
                            abs(current_beat - job["target_beat"]) < 1.5):
                        self._execute_payment(job)
                        job["executed_today"] = True

            # Reset daily flags
            if current_beat < 1.0:
                for job in self.jobs:
                    if job.get("target_beat") is not None:
                        job["executed_today"] = False

            time.sleep(check_interval)

    def _execute_payment(self, job):
        from_wallet = self.wallets.get(job["from"])
        to_wallet = self.wallets.get(job["to"])

        if not from_wallet or not to_wallet:
            print(f"[Scheduler] Wallet nicht gefunden!")
            return

        success = from_wallet.send(
            to=job["to"],
            amount=job["amount"],
            memo=job.get("memo", "Conditional payment")
        )

        if success:
            to_wallet.receive(
                from_addr=job["from"],
                amount=job["amount"],
                memo=job.get("memo", "Conditional payment")
            )


# ====================== DEMO ======================
if __name__ == "__main__":
    scheduler = ConditionalSwatchBeatScheduler()

    monitoring = SimpleXCoinWallet("monitoring_agent", balance=1500)
    data_agent = SimpleXCoinWallet("data_agent", balance=600)

    scheduler.register_wallet(monitoring)
    scheduler.register_wallet(data_agent)

    # Bedingung: Nur zahlen, wenn Qualitätsscore > 80
    def high_quality_data():
        import random
        quality = random.randint(70, 100)
        print(f"   [Condition] Aktueller Qualitätsscore: {quality}")
        return quality > 80

    # Alle 60 Beats eine bedingte Zahlung
    scheduler.schedule_conditional_payment(
        from_address="monitoring_agent",
        to_address="data_agent",
        amount=45.0,
        interval_beats=60,
        condition=high_quality_data,
        memo="Payment nur bei guter Datenqualität"
    )

    print("Starte Conditional XCoin Payment Scheduler...")
    print("(Zahlungen erfolgen nur, wenn die Bedingung erfüllt ist)\n")

    scheduler.run(check_interval=3.0)