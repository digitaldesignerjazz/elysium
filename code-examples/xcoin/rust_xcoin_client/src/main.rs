/// XCoin Client mit Smart Contract-ähnlicher Zahlungslogik (Rust)
///
/// Simuliert bedingte/automatisierte Zahlungen ähnlich wie Smart Contracts.
///
/// Beispiel: Zahlung erfolgt nur, wenn die Service-Qualität ausreichend ist.

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
}

/// Smart Contract-ähnliche Regel: Zahlung nur bei ausreichender Qualität
fn smart_contract_payment(
    payer: &mut XCoinWallet,
    payee: &mut XCoinWallet,
    amount: f64,
    service: &str,
    quality_score: u8,      // 0-100
    min_quality: u8,        // Mindestqualität für Zahlung
) {
    println!("\n[Smart Contract] Evaluating service: {}", service);
    println!("                Quality Score: {} / 100 (minimum required: {})", quality_score, min_quality);

    if quality_score >= min_quality {
        println!("                Condition met ✓ → Executing payment...");
        if payer.send(&payee.address, amount, service).is_ok() {
            payee.receive(&payer.address, amount, service);
            println!("[Smart Contract] Payment executed successfully.\n");
        }
    } else {
        println!("                Condition NOT met ✗ → Payment rejected.\n");
    }
}

fn main() {
    println!("=== Smart Contract Logic for Agent Payments ===\n");

    let mut monitoring_agent = XCoinWallet::new("monitoring_agent_alpha");
    let mut data_agent = XCoinWallet::new("data_agent_beta");

    // Szenario 1: Gute Qualität → Zahlung erfolgt
    smart_contract_payment(
        &mut monitoring_agent,
        &mut data_agent,
        50.0,
        "High-resolution soil sensor data",
        92,   // Qualität
        85,   // Mindestqualität
    );

    // Szenario 2: Schlechte Qualität → Zahlung wird abgelehnt
    smart_contract_payment(
        &mut monitoring_agent,
        &mut data_agent,
        40.0,
        "Low-quality / incomplete sensor data",
        61,   // Qualität
        85,   // Mindestqualität
    );

    println!("=== Final Status ===");
    monitoring_agent.print_status();
    data_agent.print_status();

    println!("\n>>> Smart Contract Logic successfully demonstrated! <<<");
}