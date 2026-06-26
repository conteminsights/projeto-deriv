"""
ZeeK.Web — Bankroll & Defense Management

Gerencia stake, Martingale, Multiplicador, Soros (MASTER/SLAVE),
Defesa (BARREIRA), mini-meta, limites globais e auto-reload.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Configurations ───────────────────────────────────────────────

@dataclass
class MartingaleConfig:
    enabled: bool = False
    multiplier: float = 2.0
    max_steps: int = 5
    reset_on_win: bool = True


@dataclass
class MultiplierConfig:
    enabled: bool = False
    value: float = 2.0


@dataclass
class MiniMetaConfig:
    enabled: bool = False
    profit_target: float = 50.0  # para de operar ao atingir
    max_entries: int = 0  # 0 = ilimitado


@dataclass
class GlobalLimitsConfig:
    enabled: bool = False
    daily_loss_limit: float = 0.0  # 0 = sem limite
    daily_profit_target: float = 0.0
    session_loss_limit: float = 0.0
    consecutive_loss_limit: int = 0  # 0 = sem limite


@dataclass
class AutoReloadConfig:
    enabled: bool = False
    reload_after_minutes: int = 30
    reload_after_entries: int = 0  # 0 = não usar
    reset_on_reload: bool = True


# ─── Per-Page Defense State ──────────────────────────────────────

@dataclass
class DefenseState:
    """Estado do sistema de defesa para uma página."""
    mode: str = "none"  # none, barrier, soros_master, soros_slave
    barrier: int = 3  # perdas consecutivas antes de operar
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
            return True
        if self.mode == "soros_slave":
            return self.consecutive_losses >= self.barrier
        return True

    def on_loss(self):
        self.consecutive_losses += 1

    def on_win(self):
        self.consecutive_losses = 0


# ─── Soros (MASTER/SLAVE) Pair ──────────────────────────────────

@dataclass
class SorosPair:
    """Gerencia um par MASTER/SLAVE."""
    master_page_id: str
    slave_page_id: str
    master_won: bool = False

    def on_master_result(self, won: bool):
        self.master_won = won


# ─── Main Bankroll Manager ──────────────────────────────────────

class BankrollManager:
    """
    Gerencia estado global da banca:
    - Stake + Martingale
    - Multiplicador (entrada fixa * N)
    - Defesas (BARREIRA, SOROS) por página
    - Mini-meta por setup
    - Limites globais (diário, sessão)
    - Auto-reload
    """

    def __init__(self):
        # Stake
        self.initial_stake: float = 2.0
        self.current_stake: float = 2.0
        self.martingale: MartingaleConfig = MartingaleConfig()
        self.multiplier: MultiplierConfig = MultiplierConfig()

        # Defesas por página
        self.defenses: dict[str, DefenseState] = {}

        # Soros pairs
        self.soros_pairs: list[SorosPair] = []

        # Mini-meta
        self.mini_meta: MiniMetaConfig = MiniMetaConfig()

        # Limites globais
        self.limits: GlobalLimitsConfig = GlobalLimitsConfig()

        # Auto-reload
        self.auto_reload: AutoReloadConfig = AutoReloadConfig()

        # Estado vivo
        self.consecutive_losses: int = 0
        self.martingale_step: int = 0
        self.session_profit: float = 0.0
        self.daily_profit: float = 0.0
        self.entries_today: int = 0
        self.session_entries: int = 0
        self.last_trade_won: Optional[bool] = None
        self._stopped: bool = False

    # ── Stake ──────────────────────────────────────────────────

    def calculate_next_stake(self, last_trade_won: bool) -> float:
        """Calcula o próximo stake baseado no resultado."""
        self.last_trade_won = last_trade_won
        self.consecutive_losses = 0 if last_trade_won else self.consecutive_losses + 1

        if last_trade_won:
            self.martingale_step = 0
            self.current_stake = self.initial_stake
        else:
            if self.martingale.enabled and self.martingale_step < self.martingale.max_steps:
                self.martingale_step += 1
                self.current_stake = self.initial_stake * (self.martingale.multiplier ** self.martingale_step)
            else:
                self.current_stake = self.initial_stake

        # Aplicar multiplicador
        if self.multiplier.enabled:
            self.current_stake *= self.multiplier.value

        return self.current_stake

    # ── Defesas por página ──────────────────────────────────────

    def get_defense(self, page_id: str) -> DefenseState:
        if page_id not in self.defenses:
            self.defenses[page_id] = DefenseState()
        return self.defenses[page_id]

    def set_defense_mode(self, page_id: str, mode: str, barrier: int = 3):
        defense = self.get_defense(page_id)
        defense.mode = mode
        defense.barrier = barrier

    # ── Soros ───────────────────────────────────────────────────

    def add_soros_pair(self, master_id: str, slave_id: str):
        """Registra um par MASTER/SLAVE."""
        self.soros_pairs.append(SorosPair(master_page_id=master_id, slave_page_id=slave_id))

    def is_slave_blocked(self, page_id: str) -> bool:
        """Verifica se uma página SLAVE deve estar bloqueada."""
        for pair in self.soros_pairs:
            if pair.slave_page_id == page_id:
                return not pair.master_won
        return False

    def notify_master_result(self, page_id: str, won: bool):
        """Notifica resultado de uma página MASTER."""
        for pair in self.soros_pairs:
            if pair.master_page_id == page_id:
                pair.on_master_result(won)

    # ── Mini-Meta ──────────────────────────────────────────────

    def check_mini_meta(self) -> bool:
        """
        Verifica se a mini-meta foi atingida.
        Returns True se deve parar de operar.
        """
        if not self.mini_meta.enabled:
            return False
        if self.mini_meta.profit_target > 0 and self.session_profit >= self.mini_meta.profit_target:
            logger.info(f"Mini-meta atingida: {self.session_profit:.2f}")
            return True
        if self.mini_meta.max_entries > 0 and self.session_entries >= self.mini_meta.max_entries:
            logger.info(f"Máximo de entradas atingido: {self.session_entries}")
            return True
        return False

    # ── Limites Globais ─────────────────────────────────────────

    def check_limits(self) -> bool:
        """
        Verifica se algum limite global foi excedido.
        Returns True se deve parar.
        """
        if not self.limits.enabled:
            return False

        if self.limits.daily_loss_limit > 0 and self.daily_profit <= -self.limits.daily_loss_limit:
            logger.warning(f"Limite diário de perda atingido: {self.daily_profit:.2f}")
            return True

        if self.limits.daily_profit_target > 0 and self.daily_profit >= self.limits.daily_profit_target:
            logger.info(f"Meta diária de lucro atingida: {self.daily_profit:.2f}")
            return True

        if self.limits.session_loss_limit > 0 and self.session_profit <= -self.limits.session_loss_limit:
            logger.warning(f"Limite de perda da sessão atingido: {self.session_profit:.2f}")
            return True

        if self.limits.consecutive_loss_limit > 0 and self.consecutive_losses >= self.limits.consecutive_loss_limit:
            logger.warning(f"Limite de perdas consecutivas atingido: {self.consecutive_losses}")
            return True

        return False

    # ── Trade Result Recording ─────────────────────────────────

    def record_trade_result(self, profit: float):
        """Registra o resultado de um trade."""
        self.session_profit += profit
        self.daily_profit += profit
        self.session_entries += 1
        self.entries_today += 1

    # ── Auto-Reload ─────────────────────────────────────────────

    def check_auto_reload(self) -> bool:
        """
        Verifica se deve fazer um auto-reload (reset controlado).
        Returns True se reload foi acionado.
        """
        if not self.auto_reload.enabled:
            return False

        if self.auto_reload.reload_after_entries > 0:
            if self.session_entries >= self.auto_reload.reload_after_entries:
                self._do_reload("entries")
                return True

        return False

    def _do_reload(self, reason: str):
        """Executa o reload: reseta estado da sessão."""
        logger.info(f"Auto-reload acionado por {reason}")
        if self.auto_reload.reset_on_reload:
            self.session_profit = 0.0
            self.session_entries = 0
            self.consecutive_losses = 0
            self.martingale_step = 0
            self.current_stake = self.initial_stake
            for defense in self.defenses.values():
                defense.consecutive_losses = 0

    # ── Control ─────────────────────────────────────────────────

    def stop(self):
        self._stopped = True

    def reset_session(self):
        """Reset completo do estado da sessão."""
        self.session_profit = 0.0
        self.session_entries = 0
        self.consecutive_losses = 0
        self.martingale_step = 0
        self.current_stake = self.initial_stake
        for defense in self.defenses.values():
            defense.consecutive_losses = 0
            defense.waiting_for_barrier = False

    @property
    def config_dict(self) -> dict:
        return {
            "initial_stake": self.initial_stake,
            "current_stake": self.current_stake,
            "martingale": {
                "enabled": self.martingale.enabled,
                "multiplier": self.martingale.multiplier,
                "max_steps": self.martingale.max_steps,
            },
            "multiplier": {
                "enabled": self.multiplier.enabled,
                "value": self.multiplier.value,
            },
            "mini_meta": {
                "enabled": self.mini_meta.enabled,
                "profit_target": self.mini_meta.profit_target,
                "max_entries": self.mini_meta.max_entries,
            },
            "limits": {
                "enabled": self.limits.enabled,
                "daily_loss_limit": self.limits.daily_loss_limit,
                "daily_profit_target": self.limits.daily_profit_target,
                "session_loss_limit": self.limits.session_loss_limit,
                "consecutive_loss_limit": self.limits.consecutive_loss_limit,
            },
            "auto_reload": {
                "enabled": self.auto_reload.enabled,
                "reload_after_minutes": self.auto_reload.reload_after_minutes,
                "reload_after_entries": self.auto_reload.reload_after_entries,
            },
        }

    @property
    def state_dict(self) -> dict:
        return {
            "current_stake": self.current_stake,
            "session_profit": round(self.session_profit, 2),
            "daily_profit": round(self.daily_profit, 2),
            "consecutive_losses": self.consecutive_losses,
            "martingale_step": self.martingale_step,
            "session_entries": self.session_entries,
            "entries_today": self.entries_today,
            "stopped": self._stopped,
        }


# Global singleton
bankroll_manager = BankrollManager()
