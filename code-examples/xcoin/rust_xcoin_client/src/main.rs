/// XCoin Client mit Automatisierten Agent-Zahlungen (Rust)
///
/// Zeigt, wie Agents autonom Zahlungen auslösen können,
/// z. B. wenn ein Service erbracht wurde.

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

    pub fn print_status(&self) {
        println!("\n=== XCoin Wallet Status ===");
        println!("Address:    {}", self.address);
        println!("Balance:    {} XCoin", self.balance);
        println!("Staked:     {} XCoin", self.staked);
    }
}

/// Automatisierte Zahlung, wenn ein Service erbracht wurde
fn automated_service_payment(
    payer: &mut XCoinWallet,
    payee: &mut XCoinWallet,
    amount: f64,
    service_description: &str,
) {
    println!("\n[Automated Payment] {} provided service: {}", payee.address, service_description);
    println!("           Triggering automatic payment of {} XCoin...", amount);

    if payer.send(&payee.address, amount, service_description).is_ok() {
        payee.receive(&payer.address, amount, service_description);
        println!("[Automated Payment] Payment completed successfully.\n");
    }
}

fn main() {
    println!("=== Automatisierte Agent-Zahlungen Demo ===\n");

    let mut monitoring_agent = XCoinWallet::new("monitoring_agent_alpha");
    let mut data_agent = XCoinWallet::new("data_agent_beta");

    // Simuliertes Szenario: Monitoring Agent nutzt Data Agent mehrfach
    println!("Szenario: Monitoring Agent nutzt kontinuierlich Daten vom Data Agent\n");

    // Automatische Zahlungen bei Service-Erbringung
    automated_service_payment(
        &mut monitoring_agent,
        &mut data_agent,
        42.0,
        "Soil moisture + temperature data package",
    );

    automated_service_payment(
        &mut monitoring_agent,
        &mut data_agent,
        38.0,
        "Real-time environmental sensor stream (5min)",
    );

    automated_service_payment(
        &mut monitoring_agent,
        &mut data_agent,
        55.0,
        "Historical soil data analysis report",
    );

    println!("=== End Status ===");
    monitoring_agent.print_status();
    data_agent.print_status();

    println!("\n>>> Automatisierte Agent-Zahlungen funktionieren! <<<");
}