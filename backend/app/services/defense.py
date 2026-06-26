"""
ZeeK.Web — Defense System

Implementa os sistemas de defesa: BARREIRA e SOROS (MASTER/SLAVE).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DefenseState:
    """Estado do sistema de defesa para uma página."""
    mode: str = "none"  # none, barrier, soros_master, soros_slave
    barrier: int = 3
    consecutive_losses: int = 0
    waiting_for_barrier: bool = False
    master_id: Optional[str] = None

    def should_operate(self) -> bool:
        """Verifica se a página pode operar baseado na defesa."""
        if self.mode == "none":
            return True
        if self.mode == "barrier":
            return self.consecutive_losses >= self.barrier
        if self.mode == "soros_master":
            return True  # MASTER sempre opera
        if self.mode == "soros_slave":
            return self.consecutive_losses >= self.barrier
        return True

    def on_loss(self):
        """Chamado quando a página tem um loss."""
        self.consecutive_losses += 1

    def on_win(self):
        """Chamado quando a página tem um win."""
        self.consecutive_losses = 0
