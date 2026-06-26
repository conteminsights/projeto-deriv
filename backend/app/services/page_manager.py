"""
ZeeK.Web — Page Manager

Gerencia múltiplas páginas de operação simultâneas.
"""
from typing import Dict, Optional
from datetime import datetime


class Page:
    """Uma página de operação (aba no ZeeK original)."""

    def __init__(self, page_id: str, name: str = "Página 1",
                 market: str = "R_100", mode: str = "CALL_PUT"):
        self.id = page_id
        self.name = name
        self.market = market
        self.mode = mode
        self.operating = False
        self.active_contract_id: Optional[str] = None

        # Stats
        self.session_profit: float = 0.0
        self.wins: int = 0
        self.losses: int = 0
        self.max_consecutive_loss: int = 0
        self.consecutive_losses: int = 0


class PageManager:
    """Gerencia todas as páginas ativas."""

    def __init__(self):
        self.pages: Dict[str, Page] = {}

    def add_page(self, page_id: str, name: str = "Página 1",
                 market: str = "R_100") -> Page:
        page = Page(page_id, name, market)
        self.pages[page_id] = page
        return page

    def remove_page(self, page_id: str):
        self.pages.pop(page_id, None)

    def get_page(self, page_id: str) -> Optional[Page]:
        return self.pages.get(page_id)

    def toggle_operation(self, page_id: str) -> bool:
        page = self.pages.get(page_id)
        if page:
            page.operating = not page.operating
            return page.operating
        return False

    def stop_all(self):
        for page in self.pages.values():
            page.operating = False

    def record_trade(self, page_id: str, profit: float):
        page = self.pages.get(page_id)
        if not page:
            return

        page.session_profit += profit
        if profit > 0:
            page.wins += 1
            page.consecutive_losses = 0
        else:
            page.losses += 1
            page.consecutive_losses += 1
            page.max_consecutive_loss = max(
                page.max_consecutive_loss, page.consecutive_losses
            )

    @property
    def total_profit(self) -> float:
        return sum(p.session_profit for p in self.pages.values())

    @property
    def active_count(self) -> int:
        return sum(1 for p in self.pages.values() if p.operating)


# Global singleton
page_manager = PageManager()
