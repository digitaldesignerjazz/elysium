"""
Swatch Beat Scheduler + XCoin Automatic Payments

Demonstriert, wie Agents automatische XCoin-Zahlungen
zu bestimmten Swatch Beat Zeiten auslösen können.

Beispiel-Szenario:
- Monitoring Agent bezahlt Data Agent alle 100 Beats
- Um @500 wird eine Reward-Zahlung getriggert
"""

import time
from typing import Callable


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


class SwatchBeatPaymentScheduler:
    def __init__(self):
        self.jobs = []
        self.wallets = {}  # address -> wallet

    def register_wallet(self, wallet: SimpleXCoinWallet):
        self.wallets[wallet.address] = wallet

    def schedule_payment(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        interval_beats: float = None,
        at_beat: float = None,
        memo: str = ""
    ):
        """Plant eine automatische Zahlung."""
        job = {
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "memo": memo,
            "type": "payment"
        }

        if interval_beats:
            job["type"] = "recurring_payment"
            job["interval"] = interval_beats
            job["last_run"] = 0.0
        elif at_beat is not None:
            job["type"] = "scheduled_payment"
            job["target_beat"] = at_beat % 1000
            job["executed_today"] = False

        self.jobs.append(job)

    def _get_current_beat(self) -> float:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        return (seconds / 86.4) % 1000

    def run(self, check_interval: float = 2.0):
        print("[XCoin Payment Scheduler] Gestartet...\n")

        while True:
            current_beat = self._get_current_beat()

            for job in self.jobs:
                if job["type"] == "recurring_payment":
                    if current_beat - job.get("last_run", 0) >= job["interval"]:
                        self._execute_payment(job)
                        job["last_run"] = current_beat

                elif job["type"] == "scheduled_payment":
                    if (not job.get("executed_today", False) and
                            abs(current_beat - job["target_beat"]) < 1.5):
                        self._execute_payment(job)
                        job["executed_today"] = True

            # Reset daily flags
            if current_beat < 1.0:
                for job in self.jobs:
                    if job["type"] == "scheduled_payment":
                        job["executed_today"] = False

            time.sleep(check_interval)

    def _execute_payment(self, job):
        from_wallet = self.wallets.get(job["from"])
        to_wallet = self.wallets.get(job["to"])

        if not from_wallet or not to_wallet:
            print(f"[Scheduler] Wallet nicht gefunden: {job['from']} -> {job['to']}")
            return

        success = from_wallet.send(
            to=job["to"],
            amount=job["amount"],
            memo=job.get("memo", "Scheduled payment")
        )

        if success:
            to_wallet.receive(
                from_addr=job["from"],
                amount=job["amount"],
                memo=job.get("memo", "Scheduled payment")
            )


# ====================== DEMO ======================
if __name__ == "__main__":
    scheduler = SwatchBeatPaymentScheduler()

    # Zwei Wallets erstellen
    monitoring = SimpleXCoinWallet("monitoring_agent", balance=1200)
    data_agent = SimpleXCoinWallet("data_agent", balance=800)

    scheduler.register_wallet(monitoring)
    scheduler.register_wallet(data_agent)

    # Alle 80 Beats: Monitoring Agent zahlt Data Agent
    scheduler.schedule_payment(
        from_address="monitoring_agent",
        to_address="data_agent",
        amount=35.0,
        interval_beats=80,
        memo="Automatische Datenfee"
    )

    # Um @600: Eine größere Zahlung
    scheduler.schedule_payment(
        from_address="monitoring_agent",
        to_address="data_agent",
        amount=120.0,
        at_beat=600,
        memo="Monatliche Service Fee"
    )

    print("Starte XCoin Payment Scheduler mit Swatch Beat...")
    print("(Strg+C zum Beenden)\n")

    scheduler.run(check_interval=3.0)