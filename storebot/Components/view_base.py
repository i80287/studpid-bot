from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Interaction

from abc import ABC, abstractmethod

from nextcord import Embed
from nextcord.ui import View
if __debug__:
    from nextcord import Member


class ViewBase(ABC, View):
    interaction_check_text: dict[int, str] = {
        0: "**`Sorry, but you can't manage menu called by another user`**",
        1: "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**",
    }

    def __init__(self, lng: int, author_id: int, timeout: float | None = 180.0, auto_defer: bool = True) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.lng: int = lng
        self.author_id: int = author_id
    
    @abstractmethod
    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        return

    @abstractmethod
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return

    async def interaction_check(self, interaction: Interaction) -> bool:
        assert isinstance(interaction.user, Member)
        assert interaction.locale is not None
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                embed=Embed(description=self.interaction_check_text[1 if "ru" in interaction.locale else 0]),
                ephemeral=True
            )
            return False

        return True