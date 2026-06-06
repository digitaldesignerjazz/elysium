/// XCoin Client Stub mit Staking & Reward Logic (Rust)
///
/// Erweiterte Version für die Integration in den Grok Launcher.
/// Simuliert Staking für Node-Betreiber und Reward-Auszahlungen.

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
    staked: f64,
    history: VecDeque<Transaction>,
}

impl XCoinWallet {
    pub fn new(address: &str) -> Self {
        Self {
            address: address.to_string(),
            balance: 1000.0,
            staked: 0.0,
            history: VecDeque::new(),
        }
    }

    pub fn get_balance(&self) -> f64 {
        self.balance
    }

    pub fn get_staked(&self) -> f64 {
        self.staked
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

    /// Stake XCoin (simuliert Node-Staking für Rewards)
    pub fn stake(&mut self, amount: f64) -> Result<(), String> {
        if amount <= 0.0 {
            return Err("Stake amount must be positive".to_string());
        }
        if amount > self.balance {
            return Err("Not enough balance to stake".to_string());
        }

        self.balance -= amount;
        self.staked += amount;

        let tx = Transaction {
            tx_type: "stake".to_string(),
            from: Some(self.address.clone()),
            to: None,
            amount,
            memo: "Staked for node rewards".to_string(),
        };
        self.history.push_back(tx);

        println!("✓ Staked {} XCoin. Total staked: {}", amount, self.staked);
        Ok(())
    }

    /// Simuliert Reward-Auszahlung (z.B. für Node-Betrieb)
    pub fn claim_reward(&mut self, amount: f64) {
        self.balance += amount;

        let tx = Transaction {
            tx_type: "reward".to_string(),
            from: None,
            to: Some(self.address.clone()),
            amount,
            memo: "Node uptime reward".to_string(),
        };
        self.history.push_back(tx);

        println!("✓ Claimed {} XCoin reward! New balance: {}", amount, self.balance);
    }

    pub fn print_status(&self) {
        println!("\n=== XCoin Wallet Status ===");
        println!("Address:    {}", self.address);
        println!("Balance:    {} XCoin", self.balance);
        println!("Staked:     {} XCoin", self.staked);
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
    println!("=== XCoin Rust Client with Staking & Rewards ===\n");

    let mut wallet = XCoinWallet::new("elysium_node_rust_001");

    wallet.print_status();

    // Demo operations
    let _ = wallet.send("agent_swarm_beta", 120.0, "AI monitoring payment");
    wallet.receive("mesh_node_042", 60.0, "Node uptime reward");
    let _ = wallet.stake(300.0);
    wallet.claim_reward(45.0); // Simulierter Node-Reward

    wallet.print_status();
    wallet.print_history();

    println!("\nNote: Staking & Rewards are simulated. Real on-chain logic later.");
}