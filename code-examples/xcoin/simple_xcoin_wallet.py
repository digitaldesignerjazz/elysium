"""
Simple XCoin Wallet Stub

Dies ist ein minimalistischer Wallet-Stub für XCoin.
Er dient als Einstiegspunkt für spätere Integration in:
- Grok Launcher (Rust)
- AI Agent Swarms
- Mesh Node Rewards

Der Stub simuliert grundlegende Wallet-Funktionen.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class XCoinWallet:
    address: str
    balance: float = 1000.0  # Startguthaben für Demo
    transactions: list = None

    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []

    def get_balance(self) -> float:
        """Gibt den aktuellen XCoin-Balance zurück."""
        return self.balance

    def send(self, recipient: str, amount: float, memo: str = "") -> bool:
        """Simuliert das Senden von XCoin."""
        if amount <= 0:
            print("Fehler: Betrag muss positiv sein.")
            return False
        if amount > self.balance:
            print(f"Fehler: Nicht genug Guthaben. Aktuell: {self.balance} XCoin")
            return False

        self.balance -= amount
        tx = {
            "type": "send",
            "to": recipient,
            "amount": amount,
            "memo": memo,
            "status": "simulated"
        }
        self.transactions.append(tx)
        print(f"\u2713 {amount} XCoin erfolgreich an {recipient} gesendet. (Stub)")
        return True

    def receive(self, sender: str, amount: float, memo: str = "") -> None:
        """Simuliert das Empfangen von XCoin."""
        self.balance += amount
        tx = {
            "type": "receive",
            "from": sender,
            "amount": amount,
            "memo": memo,
            "status": "simulated"
        }
        self.transactions.append(tx)
        print(f"\u2713 {amount} XCoin von {sender} empfangen. Neuer Stand: {self.balance} XCoin (Stub)")

    def show_history(self):
        """Zeigt die Transaktionshistorie."""
        print("\n=== XCoin Transaktionshistorie ===")
        if not self.transactions:
            print("Keine Transaktionen vorhanden.")
            return
        for tx in self.transactions:
            print(tx)


# ====================== DEMO ======================
if __name__ == "__main__":
    print("=== XCoin Wallet Stub Demo ===\n")

    wallet = XCoinWallet(address="elysium_node_001")

    print(f"Adresse: {wallet.address}")
    print(f"Startguthaben: {wallet.get_balance()} XCoin\n")

    # Demo Transaktionen
    wallet.send("agent_swarm_alpha", 150.0, "Payment for monitoring service")
    wallet.receive("mesh_node_hannover_042", 75.0, "Node reward")
    wallet.send("soilnova_sensor_03", 40.0, "Data purchase")

    print(f"\nAktueller Stand: {wallet.get_balance()} XCoin")
    wallet.show_history()

    print("\nHinweis: Dies ist ein reiner Stub. Später mit echter Blockchain verbinden.")