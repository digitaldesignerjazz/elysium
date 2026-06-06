use eframe::egui;
use std::collections::VecDeque;

#[derive(Debug, Clone)]
struct XCoinTx {
    tx_type: String,
    counterparty: String,
    amount: f64,
    memo: String,
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1050.0, 800.0])
            .with_title("Grok Launcher – Elysium MVP"),
        ..Default::default()
    };

    eframe::run_native(
        "Grok Launcher",
        options,
        Box::new(|_cc| Ok(Box::new(GrokLauncherApp::default()))),
    )
}

struct GrokLauncherApp {
    // Grok
    api_key: String,
    prompt: String,
    response: String,
    status: String,

    // XCoin Wallet
    xcoin_balance: f64,
    xcoin_staked: f64,
    xcoin_address: String,
    xcoin_history: VecDeque<XCoinTx>,

    // Send Form State
    show_send_window: bool,
    send_recipient: String,
    send_amount: String,
    send_memo: String,
}

impl Default for GrokLauncherApp {
    fn default() -> Self {
        Self {
            api_key: String::new(),
            prompt: String::new(),
            response: String::new(),
            status: "Ready – Elysium Grok Launcher MVP".to_string(),

            xcoin_balance: 885.0,
            xcoin_staked: 300.0,
            xcoin_address: "elysium_node_001".to_string(),
            xcoin_history: VecDeque::new(),

            show_send_window: false,
            send_recipient: String::new(),
            send_amount: String::new(),
            send_memo: String::new(),
        }
    }
}

impl eframe::App for GrokLauncherApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Grok Launcher – Elysium MVP");
            ui.label("Rust + egui | Grok + AI Agents + Mesh + XCoin");
            ui.separator();

            // Status
            ui.horizontal(|ui| {
                ui.label("Status:");
                ui.colored_label(egui::Color32::GREEN, &self.status);
            });

            ui.add_space(10.0);

            // === XCoin Wallet Section ===
            ui.collapsing("XCoin Wallet", |ui| {
                ui.horizontal(|ui| {
                    ui.label("Address:");
                    ui.monospace(&self.xcoin_address);
                });

                ui.horizontal(|ui| {
                    ui.label("Balance:");
                    ui.strong(format!("{:.2} XCoin", self.xcoin_balance));
                });

                ui.horizontal(|ui| {
                    ui.label("Staked:");
                    ui.strong(format!("{:.2} XCoin", self.xcoin_staked));
                });

                ui.add_space(8.0);

                // Action Buttons
                ui.horizontal(|ui| {
                    if ui.button("Send XCoin").clicked() {
                        self.show_send_window = true;
                        self.status = "Opening send dialog...".to_string();
                    }
                    if ui.button("Stake 50 XCoin").clicked() {
                        if self.xcoin_balance >= 50.0 {
                            self.xcoin_balance -= 50.0;
                            self.xcoin_staked += 50.0;
                            self.add_tx("stake", "self", 50.0, "Staked for node rewards");
                            self.status = "Staked 50 XCoin".to_string();
                        } else {
                            self.status = "Not enough balance to stake".to_string();
                        }
                    }
                    if ui.button("Claim Rewards").clicked() {
                        self.xcoin_balance += 25.0;
                        self.add_tx("reward", "network", 25.0, "Node uptime reward");
                        self.status = "Claimed 25 XCoin reward".to_string();
                    }
                });

                ui.add_space(10.0);

                // Transaction History
                ui.label("Recent Transactions:");
                if self.xcoin_history.is_empty() {
                    ui.label("(No transactions yet)");
                } else {
                    egui::ScrollArea::vertical().max_height(120.0).show(ui, |ui| {
                        for tx in self.xcoin_history.iter().rev().take(8) {
                            ui.label(format!("{} | {:.2} XCoin | {}", tx.tx_type, tx.amount, tx.memo));
                        }
                    });
                }
            });

            ui.add_space(15.0);

            // Grok Session
            ui.heading("Grok Session");
            ui.text_edit_multiline(&mut self.prompt).desired_rows(4);

            if ui.button("Send to Grok (Stub)").clicked() {
                self.response = format!(
                    "[STUB] Grok would respond to: {}\n\n(Real implementation: call xAI API here)",
                    self.prompt
                );
                self.status = "Grok request simulated".to_string();
            }

            ui.add_space(10.0);
            ui.label("Response:");
            ui.text_edit_multiline(&mut self.response).desired_rows(6);

            ui.add_space(20.0);

            // Quick Actions
            ui.heading("Quick Actions");
            ui.horizontal(|ui| {
                if ui.button("Launch Agent Swarm").clicked() {
                    self.status = "Agent Swarm launched (stub)".to_string();
                    self.response = "[STUB] Would start Layered AI Agent Swarm with XCoin payments...".to_string();
                }
                if ui.button("Check Mesh Nodes").clicked() {
                    self.status = "Mesh status checked (stub)".to_string();
                }
            });

            ui.add_space(20.0);
            ui.separator();
            ui.small("MVP Stub – XCoin Wallet + History integration active");
            ui.small("Part of Elysium – github.com/digitaldesignerjazz/elysium");
        });

        // === Send XCoin Window ===
        if self.show_send_window {
            egui::Window::new("Send XCoin")
                .collapsible(false)
                .resizable(false)
                .show(ctx, |ui| {
                    ui.label("Send XCoin to another address or agent");
                    ui.add_space(8.0);

                    ui.horizontal(|ui| {
                        ui.label("Recipient:");
                        ui.text_edit_singleline(&mut self.send_recipient);
                    });

                    ui.horizontal(|ui| {
                        ui.label("Amount:");
                        ui.text_edit_singleline(&mut self.send_amount);
                    });

                    ui.horizontal(|ui| {
                        ui.label("Memo:");
                        ui.text_edit_singleline(&mut self.send_memo);
                    });

                    ui.add_space(12.0);

                    ui.horizontal(|ui| {
                        if ui.button("Send").clicked() {
                            if let Ok(amount) = self.send_amount.parse::<f64>() {
                                if amount > 0.0 && amount <= self.xcoin_balance {
                                    self.xcoin_balance -= amount;
                                    self.add_tx(
                                        "send",
                                        &self.send_recipient,
                                        amount,
                                        &self.send_memo,
                                    );
                                    self.status = format!("Sent {} XCoin", amount);
                                    self.show_send_window = false;

                                    // Clear form
                                    self.send_recipient.clear();
                                    self.send_amount.clear();
                                    self.send_memo.clear();
                                } else {
                                    self.status = "Invalid amount or insufficient balance".to_string();
                                }
                            } else {
                                self.status = "Please enter a valid number".to_string();
                            }
                        }

                        if ui.button("Cancel").clicked() {
                            self.show_send_window = false;
                        }
                    });
                });
        }
    }
}

impl GrokLauncherApp {
    fn add_tx(&mut self, tx_type: &str, counterparty: &str, amount: f64, memo: &str) {
        self.xcoin_history.push_back(XCoinTx {
            tx_type: tx_type.to_string(),
            counterparty: counterparty.to_string(),
            amount,
            memo: memo.to_string(),
        });
    }
}