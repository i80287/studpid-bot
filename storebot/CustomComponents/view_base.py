from typing import Optional

from nextcord import Interaction
from nextcord.ui import View


class ViewBase(View):
    def __init__(self, *, timeout: Optional[float | int] = 180, auto_defer: bool = True) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
    
    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        return

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return