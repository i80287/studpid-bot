from abc import ABC, abstractmethod
from typing import (
    Optional,
    Union
)

from nextcord import Interaction, Embed
from nextcord.ui import View
if __debug__:
    from nextcord import Member

class ViewBase(ABC, View):
    interaction_check_text: dict[int, str] = {
        0: "**`Sorry, but you can't manage menu called by another user`**",
        1: "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**",
    }

    def __init__(self, *, lng: int, author_id: int, timeout: Optional[Union[int, float]] = 180, auto_defer: bool = True) -> None:
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
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=Embed(description=self.interaction_check_text[self.lng]), ephemeral=True)
            return False
        return True