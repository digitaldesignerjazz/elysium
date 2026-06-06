/// XCoin Client Stub (Rust)
///
/// Dieser Stub zeigt die geplante Struktur für die XCoin-Integration
/// in den Grok Launcher und AI-Agenten.
///
/// Später: echte Blockchain-Connection, Wallet-Management,
/// Payments zwischen Agents, Node-Rewards usw.

use std::collections::VecDeque;

#[derive(Debug, Clone)]
pub struct Transaction {
    pub tx_type: String,
    pub from: Option<String>,
    pub to: Option<String>,
    pub amount: f64,
    pub memo: String,
}

pub struct XCoinWallet {
    pub address: String,
    balance: f64,
    history: VecDeque<Transaction>,
}

impl XCoinWallet {
    pub fn new(address: &str) -> Self {
        Self {
            address: address.to_string(),
            balance: 1000.0,
            history: VecDeque::new(),
        }
    }

    pub fn get_balance(&self) -> f64 {
        self.balance
    }

    pub fn send(&mut self, to: &str, amount: f64, memo: &str) -> Result<(), String> {
        if amount <= 0.0 {
            return Err("Amount must be positive".to_string());
        }
        if amount > self.balance {
            return Err(format!("Insufficient balance: {}", self.balance));
        }

        self.balance -= amount;

        let tx = Transaction {
            tx_type: "send".to_string(),
            from: Some(self.address.clone()),
            to: Some(to.to_string()),
            amount,
            memo: memo.to_string(),
        };
        self.history.push_back(tx);

        println!("✓ Sent {} XCoin to {} (memo: {})", amount, to, memo);
        Ok(())
    }

    pub fn receive(&mut self, from: &str, amount: f64, memo: &str) {
        self.balance += amount;

        let tx = Transaction {
            tx_type: "receive".to_string(),
            from: Some(from.to_string()),
            to: Some(self.address.clone()),
            amount,
            memo: memo.to_string(),
        };
        self.history.push_back(tx);

        println!("✓ Received {} XCoin from {} (memo: {})", amount, from, memo);
    }

    pub fn print_history(&self) {
        println!("\n=== XCoin Transaction History ===");
        if self.history.is_empty() {
            println!("No transactions yet.");
            return;
        }
        for tx in &self.history {
            println!("{:?}", tx);
        }
    }
}

fn main() {
    println!("=== XCoin Rust Client Stub ===\n");

    let mut wallet = XCoinWallet::new("elysium_node_rust_001");

    println!("Address: {}", wallet.address);
    println!("Initial Balance: {} XCoin\n", wallet.get_balance());

    // Demo operations
    let _ = wallet.send("agent_swarm_beta", 120.0, "AI monitoring payment");
    wallet.receive("mesh_node_042", 60.0, "Node uptime reward");
    let _ = wallet.send("soilnova_unit_07", 35.0, "Environmental data purchase");

    println!("\nCurrent Balance: {} XCoin", wallet.get_balance());
    wallet.print_history();

    println!("\nNote: This is a stub. Real blockchain connection coming later.");
}