use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod solana_payment_program {
    use super::*;

    /// Initialisiert einen Escrow für eine geplante Zahlung
    pub fn initialize_escrow(
        ctx: Context<InitializeEscrow>,
        amount: u64,
        memo: String,
    ) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;
        escrow.payer = ctx.accounts.payer.key();
        escrow.payee = ctx.accounts.payee.key();
        escrow.amount = amount;
        escrow.memo = memo;
        escrow.is_executed = false;

        msg!("Escrow initialized for {} lamports", amount);
        Ok(())
    }

    /// Führt die Zahlung aus (einfache Version ohne Bedingungen)
    pub fn execute_payment(ctx: Context<ExecutePayment>) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;

        require!(!escrow.is_executed, PaymentError::AlreadyExecuted);
        require!(escrow.amount > 0, PaymentError::InvalidAmount);

        // SPL Token Transfer
        let cpi_accounts = Transfer {
            from: ctx.accounts.payer_token_account.to_account_info(),
            to: ctx.accounts.payee_token_account.to_account_info(),
            authority: ctx.accounts.payer.to_account_info(),
        };

        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

        token::transfer(cpi_ctx, escrow.amount)?;

        escrow.is_executed = true;

        msg!("Payment executed successfully");
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeEscrow<'info> {
    #[account(init, payer = payer, space = 8 + 32 + 32 + 8 + 200 + 1)]
    pub escrow: Account<'info, PaymentEscrow>,

    #[account(mut)]
    pub payer: Signer<'info>,

    /// CHECK: Payee account
    pub payee: AccountInfo<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecutePayment<'info> {
    #[account(mut)]
    pub escrow: Account<'info, PaymentEscrow>,

    #[account(mut)]
    pub payer: Signer<'info>,

    #[account(mut)]
    pub payer_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub payee_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[account]
pub struct PaymentEscrow {
    pub payer: Pubkey,
    pub payee: Pubkey,
    pub amount: u64,
    pub memo: String,
    pub is_executed: bool,
}

#[error_code]
pub enum PaymentError {
    #[msg("Payment already executed")]
    AlreadyExecuted,
    #[msg("Invalid payment amount")]
    InvalidAmount,
}