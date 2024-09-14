from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import (Interaction)

from abc import ABC, abstractmethod

from nextcord import Embed
from nextcord.ui import View
if __debug__:
    from nextcord import Member
    from nextcord.abc import GuildChannel

class ViewBase(ABC, View):
    def __init__(self, lng: int, author_id: int, timeout: float | None = 180.0, auto_defer: bool = True) -> None:
        super().__init__(timeout=timeout, auto_defer=auto_defer)
        self.lng: int = lng
        self.author_id: int = author_id

    @staticmethod
    async def try_delete(interaction: Interaction, view: ViewBase) -> None:
        assert isinstance(interaction.channel, GuildChannel)
        assert interaction.guild is not None
        try:
            await interaction.delete_original_message()
            return
        except:
            pass

        for child_component in view.children:
            if __debug__:
                from ..Components.custom_button import CustomButton
                from ..Components.custom_select import CustomSelect
                assert isinstance(child_component, (CustomButton, CustomSelect))
            child_component.disabled = True # type: ignore
        try:
            await interaction.edit_original_message(view=view)
        except:
            return

    @abstractmethod
    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        return

    @abstractmethod
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return

    async def interaction_check(self, interaction: Interaction) -> bool:
        assert isinstance(interaction.user, Member)
        assert interaction.locale is not None
        if ((user := interaction.user) is None) or (user.id != self.author_id):
            description = "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**" \
                if (locale := interaction.locale) and "ru" in locale else \
                "**`Sorry, but you can't manage menu called by another user`**"
            await interaction.response.send_message(
                embed=Embed(description=description),
                ephemeral=True
            )
            return False

        return True
