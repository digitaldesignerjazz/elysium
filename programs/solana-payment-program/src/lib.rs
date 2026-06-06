use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};
use solana_program::hash::{hash, Hash};

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod solana_payment_program {
    use super::*;

    pub fn initialize_escrow(
        ctx: Context<InitializeEscrow>,
        amount: u64,
        memo: String,
        condition_hash: Option<[u8; 32]>,
    ) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;
        escrow.payer = ctx.accounts.payer.key();
        escrow.payee = ctx.accounts.payee.key();
        escrow.amount = amount;
        escrow.memo = memo;
        escrow.condition_hash = condition_hash;
        escrow.is_executed = false;
        escrow.is_cancelled = false;

        msg!("Escrow initialized with condition");
        Ok(())
    }

    /// Führt eine normale Zahlung aus
    pub fn execute_payment(ctx: Context<ExecutePayment>) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;

        require!(!escrow.is_executed, PaymentError::AlreadyExecuted);
        require!(!escrow.is_cancelled, PaymentError::AlreadyCancelled);

        let cpi_accounts = Transfer {
            from: ctx.accounts.payer_token_account.to_account_info(),
            to: ctx.accounts.payee_token_account.to_account_info(),
            authority: ctx.accounts.payer.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

        token::transfer(cpi_ctx, escrow.amount)?;
        escrow.is_executed = true;

        msg!("Payment executed");
        Ok(())
    }

    /// Führt eine bedingte Zahlung aus (Condition Hash Validierung)
    pub fn execute_conditional_payment(
        ctx: Context<ExecuteConditionalPayment>,
        condition_data: Vec<u8>,
    ) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;

        require!(!escrow.is_executed, PaymentError::AlreadyExecuted);
        require!(!escrow.is_cancelled, PaymentError::AlreadyCancelled);

        // Condition Hash Validierung
        if let Some(stored_hash) = escrow.condition_hash {
            let computed_hash = hash(&condition_data).to_bytes();
            require!(computed_hash == stored_hash, PaymentError::ConditionNotMet);
        }

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

        msg!("Conditional payment executed successfully");
        Ok(())
    }

    pub fn claim_payment(ctx: Context<ClaimPayment>) -> Result<()> {
        let escrow = &ctx.accounts.escrow;
        require!(escrow.is_executed, PaymentError::NotExecuted);
        require!(ctx.accounts.payee.key() == escrow.payee, PaymentError::Unauthorized);

        msg!("Payment claimed");
        Ok(())
    }

    pub fn cancel_escrow(ctx: Context<CancelEscrow>) -> Result<()> {
        let escrow = &mut ctx.accounts.escrow;
        require!(!escrow.is_executed, PaymentError::AlreadyExecuted);
        require!(ctx.accounts.payer.key() == escrow.payer, PaymentError::Unauthorized);

        escrow.is_cancelled = true;
        msg!("Escrow cancelled");
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeEscrow<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + 32 + 32 + 8 + 200 + 33 + 1 + 1,
        seeds = [b"escrow", payer.key().as_ref(), payee.key().as_ref()],
        bump
    )]
    pub escrow: Account<'info, PaymentEscrow>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub payee: AccountInfo<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecutePayment<'info> {
    #[account(mut, has_one = payer)]
    pub escrow: Account<'info, PaymentEscrow>,

    #[account(mut)]
    pub payer: Signer<'info>,

    #[account(mut)]
    pub payer_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub payee_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct ExecuteConditionalPayment<'info> {
    #[account(mut, has_one = payer)]
    pub escrow: Account<'info, PaymentEscrow>,

    #[account(mut)]
    pub payer: Signer<'info>,

    #[account(mut)]
    pub payer_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub payee_token_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct ClaimPayment<'info> {
    #[account(mut, has_one = payee)]
    pub escrow: Account<'info, PaymentEscrow>,

    pub payee: Signer<'info>,
}

#[derive(Accounts)]
pub struct CancelEscrow<'info> {
    #[account(mut, has_one = payer)]
    pub escrow: Account<'info, PaymentEscrow>,

    pub payer: Signer<'info>,
}

#[account]
pub struct PaymentEscrow {
    pub payer: Pubkey,
    pub payee: Pubkey,
    pub amount: u64,
    pub memo: String,
    pub condition_hash: Option<[u8; 32]>,
    pub is_executed: bool,
    pub is_cancelled: bool,
}

#[error_code]
pub enum PaymentError {
    #[msg("Payment already executed")]
    AlreadyExecuted,
    #[msg("Escrow already cancelled")]
    AlreadyCancelled,
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Unauthorized")]
    Unauthorized,
    #[msg("Payment not executed yet")]
    NotExecuted,
    #[msg("Condition not satisfied")]
    ConditionNotMet,
}