from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import (
        Emoji,
        PartialEmoji,
        Interaction
    )

from nextcord import ButtonStyle
from nextcord.ui import Button
if __debug__:
    from ..Components.view_base import ViewBase

class CustomButton(Button):    
    def __init__(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str | None = None,
        disabled: bool = False,
        custom_id: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
        row: int | None = None
    ) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        assert self.custom_id is not None
        await self.view.click_button(interaction, self.custom_id)
