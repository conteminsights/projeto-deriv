"""
ZeeK.Web — Bankroll Management

Gerencia stake, Martingale, limites, mini-meta.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MartingaleConfig:
    enabled: bool = False
    multiplier: float = 2.0
    max_steps: int = 5
    reset_on_win: bool = True


@dataclass
class BankrollState:
    """Estado vivo da banca."""
    initial_stake: float = 2.0
    current_stake: float = 2.0
    martingale: MartingaleConfig = MartingaleConfig()
    consecutive_losses: int = 0
    martingale_step: int = 0

    def calculate_next_stake(self, last_trade_won: bool) -> float:
        """Calcula o próximo stake baseado no resultado do último trade."""
        if last_trade_won:
            self.consecutive_losses = 0
            self.martingale_step = 0
            self.current_stake = self.initial_stake
        else:
            self.consecutive_losses += 1
            if self.martingale.enabled and self.martingale_step < self.martingale.max_steps:
                self.martingale_step += 1
                self.current_stake = self.initial_stake * (
                    self.martingale.multiplier ** self.martingale_step
                )

        return self.current_stake
