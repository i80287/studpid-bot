from typing import (
    Optional,
    Union
)

from nextcord import (
    ButtonStyle,
    Interaction,
    Emoji,
    PartialEmoji
)
from nextcord.ui import Button

from CustomComponents.view_base import ViewBase


class CustomButton(Button):    
    def __init__(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        row: Optional[int] = None
    ) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        assert self.custom_id is not None
        await self.view.click_button(interaction, self.custom_id)
