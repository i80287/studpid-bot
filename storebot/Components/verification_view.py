from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Interaction

from os import urandom

from nextcord import ButtonStyle

from ..Components.view_base import ViewBase
from ..Components.custom_button import CustomButton


class VerificationView(ViewBase):
    def __init__(self, author_id: int, timeout: float | None = 30.0) -> None:
        super().__init__(0, author_id, timeout)
        self.add_item(CustomButton(
            style=ButtonStyle.green,
            custom_id=f"0_{author_id}_" + urandom(4).hex(),
            emoji="✅"
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.red,
            custom_id=f"1_{author_id}_" + urandom(4).hex(),
            emoji="❌"
        ))
        self.approved: bool | None = None
    
    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        await interaction.response.defer()
        self.approved = custom_id[0] == "0"
        self.stop()
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return
